from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.invoice import Invoice
from app.schemas.invoice import (
    InvoiceUploadResponse,
    InvoiceListResponse,
    InvoiceDetailResponse,
    InvoiceListItem,
    InvoiceDetail,
    InvoiceUpdate
)
from app.services.storage_service import storage_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=InvoiceUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_invoice(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload an invoice file

    - Accepts PDF, JPG, PNG files
    - Maximum file size: 10MB
    - Uploads to Google Cloud Storage
    - Creates invoice record in database with 'uploaded' status
    """
    try:
        # Upload to storage
        file_path, file_type = await storage_service.upload_document(
            file, str(current_user.organization_id)
        )

        # Create invoice record
        invoice = Invoice(
            organization_id=current_user.organization_id,
            file_name=file.filename,
            file_path=file_path,
            file_type=file_type,
            status="uploaded",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        logger.info(f"Invoice uploaded successfully: {invoice.id}")

        return InvoiceUploadResponse(
            success=True,
            message="Invoice uploaded successfully",
            data=InvoiceListItem.model_validate(invoice)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload invoice: {str(e)}"
        )


@router.get("", response_model=InvoiceListResponse)
def list_invoices(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all invoices for the current user's organization

    Query parameters:
    - status: Filter by status (uploaded, processing, extracted, approved, rejected, error)
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)

    Returns paginated list of invoices sorted by created_at DESC
    """
    try:
        # Base query
        query = db.query(Invoice).filter(
            Invoice.organization_id == current_user.organization_id,
            Invoice.deleted_at.is_(None)
        )

        # Apply status filter
        if status_filter:
            query = query.filter(Invoice.status == status_filter)

        # Get total count
        total = query.count()

        # Apply pagination and sorting
        invoices = query.order_by(Invoice.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

        return InvoiceListResponse(
            success=True,
            data=[InvoiceListItem.model_validate(inv) for inv in invoices],
            total=total,
            page=page,
            limit=limit
        )

    except Exception as e:
        logger.error(f"Failed to list invoices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoices"
        )


@router.get("/{invoice_id}", response_model=InvoiceDetailResponse)
def get_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed invoice information

    - Returns full invoice details
    - Includes signed URL for document download (valid for 60 minutes)
    - Only accessible by users in the same organization
    """
    try:
        # Query invoice
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.organization_id == current_user.organization_id,
            Invoice.deleted_at.is_(None)
        ).first()

        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )

        # Generate signed URL for file download
        try:
            file_url = storage_service.get_signed_url(invoice.file_path, expiry_minutes=60)
        except Exception as e:
            logger.warning(f"Failed to generate signed URL: {str(e)}")
            file_url = None

        # Convert to schema
        invoice_dict = invoice.__dict__.copy()
        invoice_dict['file_url'] = file_url
        invoice_detail = InvoiceDetail.model_validate(invoice_dict)

        return InvoiceDetailResponse(
            success=True,
            data=invoice_detail
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoice"
        )


@router.patch("/{invoice_id}", response_model=InvoiceDetailResponse)
def update_invoice(
    invoice_id: str,
    update_data: InvoiceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update invoice data (manual corrections)

    - Only users from the same organization can update
    - Updates extracted data fields
    - Sets updated_at timestamp
    """
    try:
        # Query invoice
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.organization_id == current_user.organization_id,
            Invoice.deleted_at.is_(None)
        ).first()

        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(invoice, field, value)

        invoice.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(invoice)

        logger.info(f"Invoice updated: {invoice.id}")

        # Generate signed URL
        try:
            file_url = storage_service.get_signed_url(invoice.file_path, expiry_minutes=60)
        except:
            file_url = None

        invoice_dict = invoice.__dict__.copy()
        invoice_dict['file_url'] = file_url

        return InvoiceDetailResponse(
            success=True,
            data=InvoiceDetail.model_validate(invoice_dict)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update invoice"
        )


@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: str,
    hard_delete: bool = Query(False, description="Permanently delete from storage"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an invoice

    - soft delete (default): Sets deleted_at timestamp
    - hard delete: Removes from database and storage (use with caution)
    """
    try:
        # Query invoice
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.organization_id == current_user.organization_id
        ).first()

        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )

        if hard_delete:
            # Delete from storage
            storage_service.delete_document(invoice.file_path)

            # Delete from database
            db.delete(invoice)
            db.commit()

            logger.info(f"Invoice hard deleted: {invoice_id}")
            message = "Invoice permanently deleted"
        else:
            # Soft delete
            invoice.deleted_at = datetime.utcnow()
            db.commit()

            logger.info(f"Invoice soft deleted: {invoice_id}")
            message = "Invoice deleted"

        return {
            "success": True,
            "message": message
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete invoice"
        )
