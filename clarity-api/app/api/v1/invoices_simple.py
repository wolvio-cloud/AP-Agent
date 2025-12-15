"""
Simplified Invoice API - MVP Version

Core Features:
1. Upload invoice → Immediate AI extraction (synchronous)
2. Edit extracted data
3. Export to QuickBooks

NO Celery, NO approvals, NO RBAC - just the essentials.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.services.storage_service import storage_service
from app.services.extraction_service import extract_invoice_data
from pydantic import BaseModel, Field

router = APIRouter()


# ============= SCHEMAS =============

class InvoiceData(BaseModel):
    """Extracted/edited invoice data"""
    vendor_name: str
    invoice_number: str
    invoice_date: str
    due_date: Optional[str] = None
    currency: str = "USD"
    subtotal: float
    tax_amount: float = 0.0
    tax_rate: Optional[float] = None
    total_amount: float
    payment_terms: Optional[str] = None
    line_items: list = []
    gl_account: Optional[str] = None


class InvoiceResponse(BaseModel):
    """Invoice response"""
    id: str
    status: str
    extracted_data: Optional[InvoiceData]
    file_name: str
    file_path: str
    created_at: datetime
    extraction_confidence: Optional[float] = None

    class Config:
        from_attributes = True


class InvoiceUpdateRequest(BaseModel):
    """Update invoice data after user edits"""
    data: InvoiceData


# ============= ENDPOINTS =============

@router.post("/upload", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_extract_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload invoice and IMMEDIATELY extract data (synchronous)

    Flow:
    1. Upload file to storage
    2. Call Gemini AI for extraction (3-5 seconds)
    3. Return extracted data for user to review

    NO background processing - user waits for result.
    """

    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    # Upload file to storage
    try:
        file_path, file_type = await storage_service.upload_document(
            file=file,
            organization_id=str(current_user.organization_id)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

    # Create invoice record
    invoice = Invoice(
        organization_id=current_user.organization_id,
        file_name=file.filename,
        file_path=file_path,
        file_type=file_type,
        status="processing",
        created_at=datetime.utcnow()
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    # ===== SYNCHRONOUS EXTRACTION =====
    # No Celery, no background task - just do it now
    try:
        # Extract data using Gemini AI
        extraction_result = extract_invoice_data(
            file_path=file_path,
            file_type=file_type
        )

        # Update invoice with extracted data
        invoice.extracted_json = extraction_result.get('data', {})
        invoice.per_field_confidence = extraction_result.get('confidence', {})
        invoice.overall_confidence = extraction_result.get('overall_confidence', 0.0)
        invoice.status = "extracted"
        invoice.extracted_at = datetime.utcnow()

        # Basic validation
        data = invoice.extracted_json
        if data:
            # Check math: subtotal + tax = total
            subtotal = float(data.get('subtotal', 0))
            tax = float(data.get('tax_amount', 0))
            total = float(data.get('total_amount', 0))

            if abs((subtotal + tax) - total) > 0.01:
                invoice.validation_issues = [{
                    'type': 'math_error',
                    'message': f'Subtotal ({subtotal}) + Tax ({tax}) ≠ Total ({total})'
                }]
                invoice.validation_status = 'has_issues'
            else:
                invoice.validation_status = 'valid'

        db.commit()
        db.refresh(invoice)

    except Exception as e:
        invoice.status = "failed"
        invoice.validation_issues = [{
            'type': 'extraction_error',
            'message': str(e)
        }]
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI extraction failed: {str(e)}"
        )

    # Return extracted data
    return InvoiceResponse(
        id=str(invoice.id),
        status=invoice.status,
        extracted_data=InvoiceData(**invoice.extracted_json) if invoice.extracted_json else None,
        file_name=invoice.file_name,
        file_path=invoice.file_path,
        created_at=invoice.created_at,
        extraction_confidence=invoice.overall_confidence
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get invoice by ID"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.organization_id == current_user.organization_id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    return InvoiceResponse(
        id=str(invoice.id),
        status=invoice.status,
        extracted_data=InvoiceData(**invoice.extracted_json) if invoice.extracted_json else None,
        file_name=invoice.file_name,
        file_path=invoice.file_path,
        created_at=invoice.created_at,
        extraction_confidence=invoice.overall_confidence
    )


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice_data(
    invoice_id: uuid.UUID,
    update: InvoiceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update invoice data after user reviews/edits

    This is where the user corrects any AI extraction errors.
    """
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.organization_id == current_user.organization_id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    # Update with user-edited data
    invoice.extracted_json = update.data.model_dump()
    invoice.status = "reviewed"
    invoice.validated_at = datetime.utcnow()

    # Create/update vendor if needed
    vendor_name = update.data.vendor_name
    vendor = db.query(Vendor).filter(
        Vendor.organization_id == current_user.organization_id,
        Vendor.name == vendor_name
    ).first()

    if not vendor:
        vendor = Vendor(
            organization_id=current_user.organization_id,
            name=vendor_name
        )
        db.add(vendor)
        db.flush()

    invoice.vendor_id = vendor.id

    db.commit()
    db.refresh(invoice)

    return InvoiceResponse(
        id=str(invoice.id),
        status=invoice.status,
        extracted_data=InvoiceData(**invoice.extracted_json),
        file_name=invoice.file_name,
        file_path=invoice.file_path,
        created_at=invoice.created_at,
        extraction_confidence=invoice.overall_confidence
    )


@router.get("", response_model=list[InvoiceResponse])
async def list_invoices(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all invoices for current user's organization"""
    invoices = db.query(Invoice).filter(
        Invoice.organization_id == current_user.organization_id
    ).order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    return [
        InvoiceResponse(
            id=str(inv.id),
            status=inv.status,
            extracted_data=InvoiceData(**inv.extracted_json) if inv.extracted_json else None,
            file_name=inv.file_name,
            file_path=inv.file_path,
            created_at=inv.created_at,
            extraction_confidence=inv.overall_confidence
        )
        for inv in invoices
    ]


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete invoice"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.organization_id == current_user.organization_id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    # Soft delete
    invoice.deleted_at = datetime.utcnow()
    invoice.status = "deleted"
    db.commit()

    return None
