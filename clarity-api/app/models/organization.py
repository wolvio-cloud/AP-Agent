from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)  # slug@process.clarityap.com
    country = Column(String, default="US")
    currency = Column(String, default="USD")
    default_gl_account = Column(String, default="6000")
    gstin = Column(String(20))  # India GST Identification Number
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="organization")
    invoices = relationship("Invoice", back_populates="organization")
    vendors = relationship("Vendor", back_populates="organization")
