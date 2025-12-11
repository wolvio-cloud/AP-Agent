from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True)

    # File information
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # GCS path
    file_type = Column(String, nullable=False)  # pdf, jpg, png

    # Status tracking
    status = Column(String, default="uploaded")  # uploaded, processing, extracted, approved, rejected, error
    validation_status = Column(String)  # passed, flagged, failed

    # Extracted data (from AI)
    vendor_name = Column(String)
    vendor_address = Column(Text)
    vendor_tax_id = Column(String)
    invoice_number = Column(String)
    invoice_date = Column(DateTime)
    due_date = Column(DateTime)
    currency = Column(String, default="USD")
    payment_terms = Column(String)

    # Amounts
    subtotal = Column(Numeric(10, 2))
    tax_amount = Column(Numeric(10, 2))
    tax_rate = Column(Numeric(5, 2))  # Percentage
    total_amount = Column(Numeric(10, 2))

    # Line items (JSONB array)
    line_items = Column(JSONB, default=[])

    # GL Coding
    gl_account = Column(String)
    gl_confidence = Column(Numeric(3, 2))  # 0.0 to 1.0

    # Extraction metadata
    extraction_data = Column(JSONB, default={})  # Full AI response with confidence scores
    validation_issues = Column(JSONB, default=[])  # List of validation issues

    # Processing times
    extracted_at = Column(DateTime)
    validated_at = Column(DateTime)
    approved_at = Column(DateTime)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)  # Soft delete

    # Relationships
    organization = relationship("Organization", back_populates="invoices")
    vendor = relationship("Vendor", back_populates="invoices")
