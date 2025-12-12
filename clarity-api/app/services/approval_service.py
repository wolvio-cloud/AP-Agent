"""
Approval Workflows Service

Implements flexible multi-level approval routing for invoices.

Features:
- Rule-based routing (amount thresholds, vendor-specific rules)
- Multi-level approvals with parallel/sequential steps
- Timeout handling and escalation
- Audit trail for compliance
"""

from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Integer, Boolean, JSONB, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from app.models.user import User
from app.models.invoice import Invoice
from app.services.audit_service import log_audit_event
from app.tasks.notification_tasks import send_approval_request_task
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import enum
import logging

logger = logging.getLogger(__name__)


class ApprovalStatus(enum.Enum):
    """Approval status enum"""
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    escalated = "escalated"
    expired = "expired"


class ApprovalWorkflow(BaseModel):
    """Workflow definition model"""
    __tablename__ = 'approval_workflows'

    organization_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String(500))

    # Workflow conditions (when to trigger this workflow)
    conditions = Column(JSONB)  # e.g., {"min_amount": 1000, "vendor_ids": [...]}

    # Workflow steps
    steps = Column(JSONB)  # Array of step definitions

    # Priority (higher number = higher priority when multiple workflows match)
    priority = Column(Integer, default=0)

    # Active/inactive
    is_active = Column(Boolean, default=True)


class InvoiceApproval(BaseModel):
    """Active approval request"""
    __tablename__ = 'invoice_approvals'

    invoice_id = Column(UUID(as_uuid=True), ForeignKey('invoices.id'), nullable=False)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey('approval_workflows.id'), nullable=False)
    organization_id = Column(UUID(as_uuid=True), nullable=False)

    # Current approval step
    current_step = Column(Integer, default=1)
    total_steps = Column(Integer, nullable=False)

    # Status
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.pending)

    # Approvers
    assigned_to = Column(JSONB)  # List of user IDs who can approve current step

    # Deadlines
    due_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Notes
    notes = Column(String(1000))


class ApprovalResponse(BaseModel):
    """Individual approval/rejection response"""
    __tablename__ = 'approval_responses'

    approval_id = Column(UUID(as_uuid=True), ForeignKey('invoice_approvals.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    # Response
    status = Column(SQLEnum(ApprovalStatus), nullable=False)
    notes = Column(String(1000))
    responded_at = Column(DateTime, default=datetime.utcnow)


def route_invoice_for_approval(invoice: Invoice, db: Session) -> Optional[InvoiceApproval]:
    """
    Route invoice through appropriate approval workflow

    Args:
        invoice: Invoice to route
        db: Database session

    Returns:
        InvoiceApproval if workflow found, None if no approval needed
    """
    # Get all active workflows for this organization
    workflows = db.query(ApprovalWorkflow).filter(
        ApprovalWorkflow.organization_id == invoice.organization_id,
        ApprovalWorkflow.is_active == True
    ).order_by(ApprovalWorkflow.priority.desc()).all()

    # Find matching workflow
    matching_workflow = None
    for workflow in workflows:
        if _workflow_matches_invoice(workflow, invoice):
            matching_workflow = workflow
            break

    if not matching_workflow:
        logger.info(f"No approval workflow found for invoice {invoice.id}")
        return None

    # Create approval request
    steps = matching_workflow.steps
    first_step = steps[0] if steps else {}

    approval = InvoiceApproval(
        invoice_id=invoice.id,
        workflow_id=matching_workflow.id,
        organization_id=invoice.organization_id,
        current_step=1,
        total_steps=len(steps),
        status=ApprovalStatus.pending,
        assigned_to=first_step.get('approvers', []),
        due_at=datetime.utcnow() + timedelta(hours=first_step.get('timeout_hours', 48))
    )

    db.add(approval)

    # Update invoice status
    invoice.status = 'pending_approval'

    db.commit()

    # Send notifications to approvers
    _notify_approvers(approval, invoice, first_step, db)

    # Log
    log_audit_event(
        db=db,
        event_type='approval_routed',
        action='create',
        organization_id=invoice.organization_id,
        resource_type='invoice',
        resource_id=invoice.id,
        details={
            'workflow': matching_workflow.name,
            'approvers': first_step.get('approvers', []),
            'step': 1,
            'total_steps': len(steps)
        }
    )

    logger.info(f"Routed invoice {invoice.id} to workflow '{matching_workflow.name}'")

    return approval


def _workflow_matches_invoice(workflow: ApprovalWorkflow, invoice: Invoice) -> bool:
    """
    Check if workflow conditions match invoice

    Args:
        workflow: ApprovalWorkflow to check
        invoice: Invoice to match

    Returns:
        True if conditions match
    """
    conditions = workflow.conditions or {}

    # Check minimum amount
    if 'min_amount' in conditions:
        if not invoice.extracted_json or 'total_amount' not in invoice.extracted_json:
            return False
        amount = Decimal(str(invoice.extracted_json['total_amount']))
        if amount < Decimal(str(conditions['min_amount'])):
            return False

    # Check maximum amount
    if 'max_amount' in conditions:
        if not invoice.extracted_json or 'total_amount' not in invoice.extracted_json:
            return False
        amount = Decimal(str(invoice.extracted_json['total_amount']))
        if amount > Decimal(str(conditions['max_amount'])):
            return False

    # Check vendor IDs
    if 'vendor_ids' in conditions and invoice.vendor_id:
        if str(invoice.vendor_id) not in conditions['vendor_ids']:
            return False

    # Check categories
    if 'categories' in conditions and invoice.extracted_json:
        invoice_category = invoice.extracted_json.get('category')
        if invoice_category not in conditions['categories']:
            return False

    return True


def _notify_approvers(approval: InvoiceApproval, invoice: Invoice, step: Dict, db: Session):
    """Send notifications to approvers"""
    approver_ids = step.get('approvers', [])

    for approver_id in approver_ids:
        try:
            approver = db.query(User).filter(User.id == uuid.UUID(approver_id)).first()
            if approver and approver.email:
                # Send async notification
                send_approval_request_task.delay(
                    invoice_id=str(invoice.id),
                    approver_email=approver.email,
                    approver_name=approver.full_name
                )
                logger.info(f"Sent approval notification to {approver.email}")
        except Exception as e:
            logger.error(f"Failed to send approval notification: {e}")


def process_approval_response(
    approval_id: uuid.UUID,
    user_id: uuid.UUID,
    status: str,
    notes: Optional[str],
    db: Session
) -> InvoiceApproval:
    """
    Process approval/rejection response

    Args:
        approval_id: Approval request ID
        user_id: User responding
        status: 'approved' or 'rejected'
        notes: Optional notes
        db: Database session

    Returns:
        Updated InvoiceApproval
    """
    # Get approval
    approval = db.query(InvoiceApproval).filter(InvoiceApproval.id == approval_id).first()
    if not approval:
        raise ValueError("Approval request not found")

    # Check user is assigned to this step
    if str(user_id) not in approval.assigned_to:
        raise ValueError("User not authorized to approve this step")

    # Check approval is still pending
    if approval.status != ApprovalStatus.pending:
        raise ValueError(f"Approval already {approval.status.value}")

    # Get user
    user = db.query(User).filter(User.id == user_id).first()

    # Record response
    response = ApprovalResponse(
        approval_id=approval_id,
        user_id=user_id,
        status=ApprovalStatus[status],
        notes=notes,
        responded_at=datetime.utcnow()
    )
    db.add(response)

    # Get invoice
    invoice = db.query(Invoice).filter(Invoice.id == approval.invoice_id).first()

    if status == 'rejected':
        # Rejection - workflow stops
        approval.status = ApprovalStatus.rejected
        approval.completed_at = datetime.utcnow()
        invoice.status = 'rejected'
        invoice.rejected_by = user_id
        invoice.rejected_at = datetime.utcnow()

        # Log rejection
        log_audit_event(
            db=db,
            event_type='invoice_rejected',
            action='reject',
            organization_id=approval.organization_id,
            user_id=user_id,
            resource_type='invoice',
            resource_id=invoice.id,
            details={'notes': notes, 'step': approval.current_step}
        )

        logger.info(f"Invoice {invoice.id} rejected by user {user_id}")

    elif status == 'approved':
        # Get workflow
        workflow = db.query(ApprovalWorkflow).filter(
            ApprovalWorkflow.id == approval.workflow_id
        ).first()

        if approval.current_step >= approval.total_steps:
            # Final approval - mark as approved
            approval.status = ApprovalStatus.approved
            approval.completed_at = datetime.utcnow()
            invoice.status = 'approved'
            invoice.approved_by = user_id
            invoice.approved_at = datetime.utcnow()

            # Log approval
            log_audit_event(
                db=db,
                event_type='invoice_approved',
                action='approve',
                organization_id=approval.organization_id,
                user_id=user_id,
                resource_type='invoice',
                resource_id=invoice.id,
                details={'notes': notes, 'final_step': True}
            )

            logger.info(f"Invoice {invoice.id} fully approved by user {user_id}")

        else:
            # Move to next step
            approval.current_step += 1
            next_step = workflow.steps[approval.current_step - 1]

            approval.assigned_to = next_step.get('approvers', [])
            approval.due_at = datetime.utcnow() + timedelta(hours=next_step.get('timeout_hours', 48))

            # Notify next approvers
            _notify_approvers(approval, invoice, next_step, db)

            # Log step completion
            log_audit_event(
                db=db,
                event_type='approval_step_completed',
                action='approve',
                organization_id=approval.organization_id,
                user_id=user_id,
                resource_type='invoice',
                resource_id=invoice.id,
                details={
                    'notes': notes,
                    'completed_step': approval.current_step - 1,
                    'next_step': approval.current_step
                }
            )

            logger.info(f"Invoice {invoice.id} moved to approval step {approval.current_step}")

    db.commit()

    return approval


def get_pending_approvals(user_id: uuid.UUID, db: Session) -> List[InvoiceApproval]:
    """
    Get pending approvals for a user

    Args:
        user_id: User ID
        db: Database session

    Returns:
        List of pending approvals
    """
    # Get approvals where user is in assigned_to list
    approvals = db.query(InvoiceApproval).filter(
        InvoiceApproval.status == ApprovalStatus.pending,
        InvoiceApproval.assigned_to.contains([str(user_id)])
    ).order_by(InvoiceApproval.due_at.asc()).all()

    return approvals


def check_overdue_approvals(db: Session):
    """
    Background task to check for overdue approvals and escalate

    Should be called periodically (e.g., hourly via Celery Beat)
    """
    now = datetime.utcnow()

    overdue = db.query(InvoiceApproval).filter(
        InvoiceApproval.status == ApprovalStatus.pending,
        InvoiceApproval.due_at < now
    ).all()

    for approval in overdue:
        # Mark as escalated
        approval.status = ApprovalStatus.escalated

        # Get workflow to find escalation config
        workflow = db.query(ApprovalWorkflow).filter(
            ApprovalWorkflow.id == approval.workflow_id
        ).first()

        if workflow and workflow.steps:
            current_step = workflow.steps[approval.current_step - 1]
            escalation_to = current_step.get('escalate_to', [])

            if escalation_to:
                # Add escalation approvers
                approval.assigned_to.extend(escalation_to)
                approval.due_at = now + timedelta(hours=24)  # New deadline

                logger.warning(f"Escalated overdue approval {approval.id} to {escalation_to}")
            else:
                logger.warning(f"Approval {approval.id} overdue but no escalation configured")

        # Log escalation
        log_audit_event(
            db=db,
            event_type='approval_escalated',
            action='escalate',
            organization_id=approval.organization_id,
            resource_type='invoice',
            resource_id=approval.invoice_id,
            details={
                'original_due': approval.due_at.isoformat(),
                'step': approval.current_step
            }
        )

    db.commit()

    logger.info(f"Checked overdue approvals: {len(overdue)} escalated")
