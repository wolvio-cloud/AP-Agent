from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class EInvoiceJson(Base):
    """India e-Invoice JSON storage"""
    __tablename__ = "einvoice_jsons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True)

    # Raw e-Invoice payload
    payload = Column(JSONB, nullable=False)

    # Extracted key fields for quick access
    irn = Column(String(64))  # Invoice Reference Number
    seller_gstin = Column(String(20))
    buyer_gstin = Column(String(20))
    invoice_number = Column(String)
    invoice_date = Column(DateTime)
    total_amount = Column(Numeric(10, 2))

    # Validation
    validation_status = Column(String(32), default="pending")  # pending, valid, invalid
    validation_errors = Column(JSONB, default=[])

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    invoice = relationship("Invoice")


class ExtractionMetric(Base):
    """Tracks extraction performance metrics"""
    __tablename__ = "extraction_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)

    # Processing details
    processing_tier = Column(String(16), nullable=False)  # tier1, tier2, tier3, tier4
    processing_time_ms = Column(Numeric)
    confidence_score = Column(Numeric(3, 2))

    # Accuracy tracking (for testing)
    field_accuracy = Column(JSONB)  # {"vendor_name": true, "total_amount": true, ...}

    # Cost tracking
    cost_usd = Column(Numeric(10, 4))  # API costs
    api_calls = Column(JSONB)  # {"gemini": 1, "gpt4v": 0}

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    invoice = relationship("Invoice")
