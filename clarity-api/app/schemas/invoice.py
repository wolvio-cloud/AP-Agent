from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class InvoiceBase(BaseModel):
    """Base invoice schema"""
    file_name: str
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    total_amount: Optional[Decimal] = None


class InvoiceCreate(BaseModel):
    """Schema for creating an invoice (internal use)"""
    organization_id: UUID
    file_name: str
    file_path: str
    file_type: str
    status: str = "uploaded"


class InvoiceUpdate(BaseModel):
    """Schema for updating invoice data"""
    vendor_name: Optional[str] = None
    vendor_address: Optional[str] = None
    vendor_tax_id: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    currency: Optional[str] = None
    payment_terms: Optional[str] = None
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    line_items: Optional[List[dict]] = None
    gl_account: Optional[str] = None


class InvoiceListItem(BaseModel):
    """Schema for invoice list item"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    file_name: str
    status: str
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    total_amount: Optional[Decimal] = None
    invoice_date: Optional[datetime] = None
    created_at: datetime


class InvoiceDetail(BaseModel):
    """Schema for detailed invoice view"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    vendor_id: Optional[UUID] = None

    # File info
    file_name: str
    file_path: str
    file_type: str
    file_url: Optional[str] = None  # Signed URL for download

    # Status
    status: str
    validation_status: Optional[str] = None

    # Extracted data
    vendor_name: Optional[str] = None
    vendor_address: Optional[str] = None
    vendor_tax_id: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    currency: Optional[str] = None
    payment_terms: Optional[str] = None

    # Amounts
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None

    # Line items
    line_items: Optional[List[dict]] = None

    # GL coding
    gl_account: Optional[str] = None
    gl_confidence: Optional[Decimal] = None

    # Metadata
    extraction_data: Optional[dict] = None
    validation_issues: Optional[List[dict]] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    extracted_at: Optional[datetime] = None
    validated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None


class InvoiceUploadResponse(BaseModel):
    """Response after invoice upload"""
    success: bool
    message: str
    data: InvoiceListItem


class InvoiceListResponse(BaseModel):
    """Response for invoice list"""
    success: bool
    data: List[InvoiceListItem]
    total: int
    page: int
    limit: int


class InvoiceDetailResponse(BaseModel):
    """Response for invoice detail"""
    success: bool
    data: InvoiceDetail
