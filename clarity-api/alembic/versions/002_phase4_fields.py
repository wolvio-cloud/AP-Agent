"""add phase4 extraction fields

Revision ID: 002_phase4_fields
Revises: 001_initial
Create Date: 2024-12-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision = '002_phase4_fields'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new fields to invoices table
    op.add_column('invoices', sa.Column('extracted_json', JSONB, nullable=True))
    op.add_column('invoices', sa.Column('per_field_confidence', JSONB, nullable=True))
    op.add_column('invoices', sa.Column('processing_tier', sa.String(16), server_default='uploaded'))
    op.add_column('invoices', sa.Column('irn', sa.String(64), nullable=True))
    op.add_column('invoices', sa.Column('buyer_gstin', sa.String(20), nullable=True))
    op.add_column('invoices', sa.Column('seller_gstin', sa.String(20), nullable=True))
    op.add_column('invoices', sa.Column('source_type', sa.String(32), nullable=True))
    op.add_column('invoices', sa.Column('processing_history', JSONB, server_default='[]'))
    op.add_column('invoices', sa.Column('overall_confidence', sa.Numeric(3, 2), nullable=True))
    op.add_column('invoices', sa.Column('requires_review', sa.Boolean, server_default='false'))
    op.add_column('invoices', sa.Column('review_priority', sa.String(16), nullable=True))
    op.add_column('invoices', sa.Column('anomaly_flags', JSONB, server_default='[]'))

    # Add GSTIN to organizations table
    op.add_column('organizations', sa.Column('gstin', sa.String(20), nullable=True))

    # Create einvoice_jsons table
    op.create_table(
        'einvoice_jsons',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('invoice_id', UUID(as_uuid=True), sa.ForeignKey('invoices.id'), nullable=True),
        sa.Column('payload', JSONB, nullable=False),
        sa.Column('irn', sa.String(64), nullable=True),
        sa.Column('seller_gstin', sa.String(20), nullable=True),
        sa.Column('buyer_gstin', sa.String(20), nullable=True),
        sa.Column('invoice_number', sa.String, nullable=True),
        sa.Column('invoice_date', sa.DateTime, nullable=True),
        sa.Column('total_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('validation_status', sa.String(32), server_default='pending'),
        sa.Column('validation_errors', JSONB, server_default='[]'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create extraction_metrics table
    op.create_table(
        'extraction_metrics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('invoice_id', UUID(as_uuid=True), sa.ForeignKey('invoices.id'), nullable=False),
        sa.Column('processing_tier', sa.String(16), nullable=False),
        sa.Column('processing_time_ms', sa.Integer, nullable=True),
        sa.Column('confidence_score', sa.Numeric(3, 2), nullable=True),
        sa.Column('field_accuracy', JSONB, nullable=True),
        sa.Column('cost_usd', sa.Numeric(10, 4), nullable=True),
        sa.Column('api_calls', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )

    # Add indexes
    op.create_index('idx_invoices_processing_tier', 'invoices', ['processing_tier'])
    op.create_index('idx_invoices_requires_review', 'invoices', ['requires_review'])
    op.create_index('idx_invoices_irn', 'invoices', ['irn'])
    op.create_index('idx_einvoice_irn', 'einvoice_jsons', ['irn'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_invoices_processing_tier')
    op.drop_index('idx_invoices_requires_review')
    op.drop_index('idx_invoices_irn')
    op.drop_index('idx_einvoice_irn')

    # Drop tables
    op.drop_table('extraction_metrics')
    op.drop_table('einvoice_jsons')

    # Remove columns from organizations
    op.drop_column('organizations', 'gstin')

    # Remove columns from invoices
    op.drop_column('invoices', 'extracted_json')
    op.drop_column('invoices', 'per_field_confidence')
    op.drop_column('invoices', 'processing_tier')
    op.drop_column('invoices', 'irn')
    op.drop_column('invoices', 'buyer_gstin')
    op.drop_column('invoices', 'seller_gstin')
    op.drop_column('invoices', 'source_type')
    op.drop_column('invoices', 'processing_history')
    op.drop_column('invoices', 'overall_confidence')
    op.drop_column('invoices', 'requires_review')
    op.drop_column('invoices', 'review_priority')
    op.drop_column('invoices', 'anomaly_flags')
