"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2024-12-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('slug', sa.String, unique=True, nullable=False),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('country', sa.String, default='US'),
        sa.Column('currency', sa.String, default='USD'),
        sa.Column('default_gl_account', sa.String, default='6000'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('first_name', sa.String, nullable=False),
        sa.Column('last_name', sa.String, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_superuser', sa.Boolean, default=False),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create vendors table
    op.create_table(
        'vendors',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('address', sa.String),
        sa.Column('tax_id', sa.String),
        sa.Column('default_gl_account', sa.String),
        sa.Column('average_invoice_amount', sa.Numeric(10, 2), default=0),
        sa.Column('invoice_count', sa.Numeric, default=0),
        sa.Column('metadata', JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create invoices table
    op.create_table(
        'invoices',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('vendor_id', UUID(as_uuid=True), sa.ForeignKey('vendors.id'), nullable=True),
        sa.Column('file_name', sa.String, nullable=False),
        sa.Column('file_path', sa.String, nullable=False),
        sa.Column('file_type', sa.String, nullable=False),
        sa.Column('status', sa.String, default='uploaded'),
        sa.Column('validation_status', sa.String),
        sa.Column('vendor_name', sa.String),
        sa.Column('vendor_address', sa.Text),
        sa.Column('vendor_tax_id', sa.String),
        sa.Column('invoice_number', sa.String),
        sa.Column('invoice_date', sa.DateTime),
        sa.Column('due_date', sa.DateTime),
        sa.Column('currency', sa.String, default='USD'),
        sa.Column('payment_terms', sa.String),
        sa.Column('subtotal', sa.Numeric(10, 2)),
        sa.Column('tax_amount', sa.Numeric(10, 2)),
        sa.Column('tax_rate', sa.Numeric(5, 2)),
        sa.Column('total_amount', sa.Numeric(10, 2)),
        sa.Column('line_items', JSONB, server_default='[]'),
        sa.Column('gl_account', sa.String),
        sa.Column('gl_confidence', sa.Numeric(3, 2)),
        sa.Column('extraction_data', JSONB, server_default='{}'),
        sa.Column('validation_issues', JSONB, server_default='[]'),
        sa.Column('extracted_at', sa.DateTime),
        sa.Column('validated_at', sa.DateTime),
        sa.Column('approved_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime)
    )

    # Create gl_accounts table
    op.create_table(
        'gl_accounts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('code', sa.String, unique=True, nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('category', sa.String),
        sa.Column('keywords', sa.String),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_organizations_slug', 'organizations', ['slug'])
    op.create_index('idx_invoices_org', 'invoices', ['organization_id'])
    op.create_index('idx_invoices_status', 'invoices', ['status'])


def downgrade() -> None:
    op.drop_index('idx_invoices_status')
    op.drop_index('idx_invoices_org')
    op.drop_index('idx_organizations_slug')
    op.drop_index('idx_users_email')

    op.drop_table('gl_accounts')
    op.drop_table('invoices')
    op.drop_table('vendors')
    op.drop_table('users')
    op.drop_table('organizations')
