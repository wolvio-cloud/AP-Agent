"""
Security and Compliance Features

- Audit logging for all critical actions
- RBAC (Role-Based Access Control)
- Approval workflows
- Vendor management

Revision ID: 003_security_compliance
Revises: 002_phase4_fields
Create Date: 2024-12-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid


# revision identifiers, used by Alembic.
revision = '003_security_compliance'
down_revision = '002_phase4_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === AUDIT LOG TABLE ===
    op.create_table(
        'audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),

        # Event details
        sa.Column('event_type', sa.String(100), nullable=False),  # login, invoice_created, invoice_approved, etc
        sa.Column('resource_type', sa.String(50)),  # invoice, user, vendor, etc
        sa.Column('resource_id', UUID(as_uuid=True)),
        sa.Column('action', sa.String(50), nullable=False),  # create, read, update, delete, approve, reject

        # Event metadata
        sa.Column('details', JSONB),  # Additional event data
        sa.Column('ip_address', sa.String(45)),  # IPv4 or IPv6
        sa.Column('user_agent', sa.String(500)),
        sa.Column('session_id', sa.String(100)),

        # Security
        sa.Column('status', sa.String(20), server_default='success'),  # success, failure, error
        sa.Column('error_message', sa.Text),

        # Timestamps
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),

        # Indexes for fast queries
        sa.Index('idx_audit_logs_org', 'organization_id'),
        sa.Index('idx_audit_logs_user', 'user_id'),
        sa.Index('idx_audit_logs_resource', 'resource_type', 'resource_id'),
        sa.Index('idx_audit_logs_event_type', 'event_type'),
        sa.Index('idx_audit_logs_created_at', 'created_at'),
    )

    # === ROLES AND PERMISSIONS ===
    op.create_table(
        'roles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('permissions', JSONB, nullable=False, server_default='{}'),
        # Permissions structure:
        # {
        #   "invoices": ["create", "read", "update", "delete", "approve"],
        #   "vendors": ["create", "read", "update"],
        #   "users": ["read"],
        #   "analytics": ["read"]
        # }
        sa.Column('is_system_role', sa.Boolean, server_default='false'),  # Cannot be deleted
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()')),

        sa.UniqueConstraint('organization_id', 'name', name='uq_role_name_per_org'),
        sa.Index('idx_roles_org', 'organization_id'),
    )

    # === APPROVAL WORKFLOWS ===
    op.create_table(
        'approval_workflows',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('workflow_name', sa.String(255), nullable=False),

        # Workflow rules (JSON structure defining steps and conditions)
        sa.Column('rules', JSONB, nullable=False),
        # Structure:
        # {
        #   "steps": [
        #     {
        #       "name": "Manager Approval",
        #       "condition": {"field": "total_amount", "operator": "gt", "value": 1000},
        #       "approvers": ["role:manager"],
        #       "required_approvals": 1,
        #       "timeout_hours": 48
        #     }
        #   ]
        # }

        sa.Column('is_default', sa.Boolean, server_default='false'),
        sa.Column('is_enabled', sa.Boolean, server_default='true'),

        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()')),

        sa.Index('idx_workflows_org', 'organization_id'),
        sa.Index('idx_workflows_default', 'organization_id', 'is_default', 'is_enabled'),
    )

    # === INVOICE APPROVALS ===
    op.create_table(
        'invoice_approvals',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('invoice_id', UUID(as_uuid=True), sa.ForeignKey('invoices.id'), nullable=False),
        sa.Column('workflow_id', UUID(as_uuid=True), sa.ForeignKey('approval_workflows.id')),

        sa.Column('step_number', sa.Integer, nullable=False),  # Which step in workflow
        sa.Column('step_name', sa.String(255)),

        sa.Column('required_approvers', JSONB),  # List of user IDs or roles
        sa.Column('required_approvals', sa.Integer, server_default='1'),

        sa.Column('status', sa.String(50), server_default='pending'),  # pending, approved, rejected, escalated

        sa.Column('requested_at', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('due_at', sa.DateTime),  # Timeout deadline
        sa.Column('completed_at', sa.DateTime),

        sa.Index('idx_approvals_invoice', 'invoice_id'),
        sa.Index('idx_approvals_status', 'status'),
        sa.Index('idx_approvals_due_at', 'due_at'),
    )

    # === APPROVAL RESPONSES ===
    op.create_table(
        'approval_responses',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('approval_id', UUID(as_uuid=True), sa.ForeignKey('invoice_approvals.id'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),

        sa.Column('status', sa.String(50)),  # approved, rejected
        sa.Column('notes', sa.Text),

        sa.Column('responded_at', sa.DateTime, server_default=sa.text('NOW()')),

        sa.Index('idx_approval_responses_approval', 'approval_id'),
        sa.Index('idx_approval_responses_user', 'user_id'),
    )

    # === VALIDATION RULES ===
    op.create_table(
        'validation_rules',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('rule_name', sa.String(255), nullable=False),
        sa.Column('rule_type', sa.String(50), nullable=False),
        # Types: amount_threshold, vendor_whitelist, gl_code_required, etc

        sa.Column('conditions', JSONB, nullable=False),
        # Example: {"field": "total_amount", "operator": "gt", "value": 10000}

        sa.Column('action', JSONB, nullable=False),
        # Example: {"type": "flag", "severity": "high", "message": "..."}

        sa.Column('priority', sa.Integer, server_default='100'),  # Lower = higher priority
        sa.Column('is_enabled', sa.Boolean, server_default='true'),

        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),

        sa.Index('idx_validation_rules_org', 'organization_id'),
        sa.Index('idx_validation_rules_enabled', 'organization_id', 'is_enabled'),
    )

    # === ENHANCED VENDOR TABLE ===
    # Note: average_invoice_amount already exists from 001_initial migration
    op.add_column('vendors', sa.Column('total_invoices', sa.Integer, server_default='0'))
    op.add_column('vendors', sa.Column('last_invoice_date', sa.DateTime))
    op.add_column('vendors', sa.Column('payment_terms', sa.String(50)))
    op.add_column('vendors', sa.Column('is_active', sa.Boolean, server_default='true'))
    op.add_column('vendors', sa.Column('notes', sa.Text))

    # === ENHANCED USER TABLE ===
    op.add_column('users', sa.Column('role_id', UUID(as_uuid=True), sa.ForeignKey('roles.id')))
    op.add_column('users', sa.Column('department', sa.String(100)))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime))
    op.add_column('users', sa.Column('last_login_ip', sa.String(45)))
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer, server_default='0'))
    op.add_column('users', sa.Column('locked_until', sa.DateTime))

    # === ENHANCED INVOICE TABLE ===
    op.add_column('invoices', sa.Column('approved_by', UUID(as_uuid=True), sa.ForeignKey('users.id')))
    op.add_column('invoices', sa.Column('approved_at', sa.DateTime))
    op.add_column('invoices', sa.Column('rejected_by', UUID(as_uuid=True), sa.ForeignKey('users.id')))
    op.add_column('invoices', sa.Column('rejected_at', sa.DateTime))
    op.add_column('invoices', sa.Column('processing_task_id', sa.String(100)))  # Celery task ID

    # Add indexes
    op.create_index('idx_invoices_approved_by', 'invoices', ['approved_by'])
    op.create_index('idx_invoices_rejected_by', 'invoices', ['rejected_by'])
    op.create_index('idx_invoices_task_id', 'invoices', ['processing_task_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_invoices_task_id', 'invoices')
    op.drop_index('idx_invoices_rejected_by', 'invoices')
    op.drop_index('idx_invoices_approved_by', 'invoices')

    # Drop columns from existing tables
    op.drop_column('invoices', 'processing_task_id')
    op.drop_column('invoices', 'rejected_at')
    op.drop_column('invoices', 'rejected_by')
    op.drop_column('invoices', 'approved_at')
    op.drop_column('invoices', 'approved_by')

    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'last_login_ip')
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'department')
    op.drop_column('users', 'role_id')

    op.drop_column('vendors', 'notes')
    op.drop_column('vendors', 'is_active')
    op.drop_column('vendors', 'payment_terms')
    op.drop_column('vendors', 'last_invoice_date')
    op.drop_column('vendors', 'total_invoices')
    # Note: average_invoice_amount belongs to 001_initial migration, not dropped here

    # Drop tables
    op.drop_table('validation_rules')
    op.drop_table('approval_responses')
    op.drop_table('invoice_approvals')
    op.drop_table('approval_workflows')
    op.drop_table('roles')
    op.drop_table('audit_logs')
