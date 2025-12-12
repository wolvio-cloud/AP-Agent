"""
Audit Logging Service for SOC 2 Compliance

Tracks all critical actions for security and compliance purposes.
"""

from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Text, DateTime, JSONB
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from app.models.user import User
from datetime import datetime
from typing import Optional, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)


class AuditLog(BaseModel):
    """Audit log model for tracking all system actions"""
    __tablename__ = 'audit_logs'

    organization_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True))

    # Event details
    event_type = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(UUID(as_uuid=True))
    action = Column(String(50), nullable=False)

    # Event metadata
    details = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    session_id = Column(String(100))

    # Security
    status = Column(String(20), default='success')
    error_message = Column(Text)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)


def log_audit_event(
    db: Session,
    event_type: str,
    action: str,
    organization_id: uuid.UUID,
    user_id: Optional[uuid.UUID] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[uuid.UUID] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    session_id: Optional[str] = None,
    status: str = 'success',
    error_message: Optional[str] = None
) -> AuditLog:
    """
    Log an audit event

    Args:
        db: Database session
        event_type: Type of event (login, invoice_created, etc.)
        action: Action performed (create, read, update, delete, approve, reject)
        organization_id: Organization ID
        user_id: Optional user ID who performed the action
        resource_type: Optional type of resource affected
        resource_id: Optional ID of resource affected
        details: Optional additional details (as dict)
        ip_address: Optional IP address of user
        user_agent: Optional user agent string
        session_id: Optional session ID
        status: Event status (success, failure, error)
        error_message: Optional error message if status is failure/error

    Returns:
        Created AuditLog instance
    """
    audit_log = AuditLog(
        organization_id=organization_id,
        user_id=user_id,
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        details=details or {},
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id,
        status=status,
        error_message=error_message
    )

    db.add(audit_log)
    db.commit()

    logger.info(f"Audit log created: {event_type}/{action} by user {user_id}")

    return audit_log


# Convenience functions for common audit events

def log_login(db: Session, user: User, ip_address: str, user_agent: str, success: bool = True):
    """Log user login attempt"""
    return log_audit_event(
        db=db,
        event_type='user_login',
        action='login',
        organization_id=user.organization_id,
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        status='success' if success else 'failure',
        details={'email': user.email}
    )


def log_logout(db: Session, user: User):
    """Log user logout"""
    return log_audit_event(
        db=db,
        event_type='user_logout',
        action='logout',
        organization_id=user.organization_id,
        user_id=user.id
    )


def log_invoice_created(db: Session, user: User, invoice_id: uuid.UUID, details: Dict):
    """Log invoice creation"""
    return log_audit_event(
        db=db,
        event_type='invoice_created',
        action='create',
        organization_id=user.organization_id,
        user_id=user.id,
        resource_type='invoice',
        resource_id=invoice_id,
        details=details
    )


def log_invoice_updated(db: Session, user: User, invoice_id: uuid.UUID, changes: Dict):
    """Log invoice update"""
    return log_audit_event(
        db=db,
        event_type='invoice_updated',
        action='update',
        organization_id=user.organization_id,
        user_id=user.id,
        resource_type='invoice',
        resource_id=invoice_id,
        details={'changes': changes}
    )


def log_invoice_approved(db: Session, user: User, invoice_id: uuid.UUID, notes: Optional[str] = None):
    """Log invoice approval"""
    return log_audit_event(
        db=db,
        event_type='invoice_approved',
        action='approve',
        organization_id=user.organization_id,
        user_id=user.id,
        resource_type='invoice',
        resource_id=invoice_id,
        details={'notes': notes} if notes else {}
    )


def log_invoice_rejected(db: Session, user: User, invoice_id: uuid.UUID, reason: str):
    """Log invoice rejection"""
    return log_audit_event(
        db=db,
        event_type='invoice_rejected',
        action='reject',
        organization_id=user.organization_id,
        user_id=user.id,
        resource_type='invoice',
        resource_id=invoice_id,
        details={'reason': reason}
    )


def log_invoice_deleted(db: Session, user: User, invoice_id: uuid.UUID):
    """Log invoice deletion"""
    return log_audit_event(
        db=db,
        event_type='invoice_deleted',
        action='delete',
        organization_id=user.organization_id,
        user_id=user.id,
        resource_type='invoice',
        resource_id=invoice_id
    )


def log_data_export(db: Session, user: User, export_type: str, record_count: int):
    """Log data export"""
    return log_audit_event(
        db=db,
        event_type='data_exported',
        action='export',
        organization_id=user.organization_id,
        user_id=user.id,
        details={
            'export_type': export_type,
            'record_count': record_count
        }
    )


def log_settings_changed(db: Session, user: User, setting_name: str, old_value: Any, new_value: Any):
    """Log settings change"""
    return log_audit_event(
        db=db,
        event_type='settings_changed',
        action='update',
        organization_id=user.organization_id,
        user_id=user.id,
        resource_type='settings',
        details={
            'setting_name': setting_name,
            'old_value': str(old_value),
            'new_value': str(new_value)
        }
    )


def log_permission_changed(db: Session, admin_user: User, target_user_id: uuid.UUID, changes: Dict):
    """Log permission/role changes"""
    return log_audit_event(
        db=db,
        event_type='permission_changed',
        action='update',
        organization_id=admin_user.organization_id,
        user_id=admin_user.id,
        resource_type='user',
        resource_id=target_user_id,
        details={'changes': changes}
    )
