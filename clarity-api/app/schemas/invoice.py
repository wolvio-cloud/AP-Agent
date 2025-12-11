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

    # Phase 4: Extraction fields
    processing_tier: Optional[str] = None
    overall_confidence: Optional[Decimal] = None
    requires_review: Optional[bool] = None
    review_priority: Optional[str] = None


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

    # Phase 4: AI Extraction fields
    extracted_json: Optional[dict] = None  # Complete extracted data
    per_field_confidence: Optional[dict] = None  # Confidence for each field
    processing_tier: Optional[str] = None
    overall_confidence: Optional[Decimal] = None
    requires_review: Optional[bool] = None
    review_priority: Optional[str] = None
    processing_history: Optional[List[dict]] = None

    # Phase 4: India e-Invoice fields
    irn: Optional[str] = None  # Invoice Reference Number
    buyer_gstin: Optional[str] = None
    seller_gstin: Optional[str] = None
    source_type: Optional[str] = None  # 'pdf', 'image', 'einvoice_json'
    anomaly_flags: Optional[List[str]] = None

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


# Phase 4: e-Invoice JSON ingestion schemas

class EInvoiceJsonPayload(BaseModel):
    """Schema for India e-Invoice JSON payload"""
    # Mandatory fields
    irn: str  # Invoice Reference Number (64 chars)
    seller_gstin: str  # Seller GSTIN (15 chars)
    buyer_gstin: str  # Buyer GSTIN (15 chars)
    doc_no: str  # Document/Invoice number
    doc_date: str  # Document date (DD/MM/YYYY)
    doc_type: str  # INV, CRN, DBN

    # Optional but common fields
    total_value: Optional[Decimal] = None
    cgst_value: Optional[Decimal] = None
    sgst_value: Optional[Decimal] = None
    igst_value: Optional[Decimal] = None
    taxable_value: Optional[Decimal] = None

    # Seller details
    seller_legal_name: Optional[str] = None
    seller_trade_name: Optional[str] = None
    seller_address: Optional[str] = None
    seller_location: Optional[str] = None
    seller_pincode: Optional[str] = None
    seller_state_code: Optional[str] = None

    # Buyer details
    buyer_legal_name: Optional[str] = None
    buyer_trade_name: Optional[str] = None
    buyer_address: Optional[str] = None
    buyer_location: Optional[str] = None
    buyer_pincode: Optional[str] = None
    buyer_state_code: Optional[str] = None

    # Additional metadata
    supply_type: Optional[str] = None  # B2B, B2C, SEZWP, SEZWOP, EXPWP, EXPWOP, DEXP
    reverse_charge: Optional[bool] = None
    qr_code: Optional[str] = None
    signed_invoice: Optional[str] = None
    signed_qr_code: Optional[str] = None

    # Line items
    item_list: Optional[List[dict]] = None

    # Store complete JSON
    raw_json: Optional[dict] = None


class EInvoiceIngestRequest(BaseModel):
    """Request to ingest e-Invoice JSON only"""
    einvoice_json: dict  # Complete e-Invoice JSON payload


class EInvoiceIngestPairRequest(BaseModel):
    """Request to ingest PDF + e-Invoice JSON pair"""
    einvoice_json: dict  # e-Invoice JSON payload
    # File will be uploaded separately via multipart form


class EInvoiceIngestResponse(BaseModel):
    """Response after e-Invoice ingestion"""
    success: bool
    message: str
    data: InvoiceDetail
