"""
QuickBooks Export API - MVP Version

Endpoints:
1. Export single invoice to IIF
2. Export multiple invoices to IIF
3. Export to CSV (alternative)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import uuid
import io

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.invoice import Invoice
from app.services.quickbooks_export import (
    generate_qbo_iif,
    generate_iif_file,
    generate_csv_export,
    validate_invoice_for_export
)
from pydantic import BaseModel

router = APIRouter()


class ExportRequest(BaseModel):
    """Request to export invoices"""
    invoice_ids: List[str]


@router.get("/export/iif/{invoice_id}")
async def export_invoice_to_iif(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export single invoice to QuickBooks IIF format

    Returns downloadable .iif file that user can import to QuickBooks manually.
    """
    # Get invoice
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.organization_id == current_user.organization_id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    # Check if invoice has been reviewed
    if not invoice.extracted_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice must be reviewed before export"
        )

    # Prepare invoice data
    invoice_data = {
        'id': str(invoice.id),
        'extracted_data': invoice.extracted_json,
        'status': invoice.status
    }

    # Validate
    errors = validate_invoice_for_export(invoice_data)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {', '.join(errors)}"
        )

    # Generate IIF content
    iif_content = generate_qbo_iif(invoice_data)

    # Return as downloadable file
    filename = f"invoice_{invoice.extracted_json.get('invoice_number', invoice_id)}.iif"

    return Response(
        content=iif_content,
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.post("/export/iif/batch")
async def export_invoices_batch(
    request: ExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export multiple invoices to single IIF file

    Useful for batch importing to QuickBooks
    """
    # Get invoices
    invoice_uuids = [uuid.UUID(id) for id in request.invoice_ids]

    invoices = db.query(Invoice).filter(
        Invoice.id.in_(invoice_uuids),
        Invoice.organization_id == current_user.organization_id
    ).all()

    if not invoices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No invoices found"
        )

    # Prepare invoice data
    invoice_data_list = []
    for invoice in invoices:
        if not invoice.extracted_json:
            continue  # Skip unreviewed invoices

        invoice_data = {
            'id': str(invoice.id),
            'extracted_data': invoice.extracted_json,
            'status': invoice.status
        }

        # Validate
        errors = validate_invoice_for_export(invoice_data)
        if errors:
            continue  # Skip invalid invoices

        invoice_data_list.append(invoice_data)

    if not invoice_data_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid invoices to export"
        )

    # Generate IIF
    iif_content = generate_iif_file(invoice_data_list)

    # Return as downloadable file
    filename = f"invoices_batch_{len(invoice_data_list)}.iif"

    return Response(
        content=iif_content,
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/export/csv")
async def export_all_invoices_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export all reviewed invoices to CSV

    Alternative format for users who prefer spreadsheets
    """
    # Get all reviewed invoices
    invoices = db.query(Invoice).filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.status.in_(['reviewed', 'approved'])
    ).all()

    if not invoices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No invoices to export"
        )

    # Prepare invoice data
    invoice_data_list = [
        {
            'id': str(inv.id),
            'extracted_data': inv.extracted_json,
            'status': inv.status
        }
        for inv in invoices
        if inv.extracted_json
    ]

    # Generate CSV
    csv_content = generate_csv_export(invoice_data_list)

    # Return as downloadable file
    filename = f"invoices_export_{len(invoice_data_list)}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/validate/{invoice_id}")
async def validate_invoice_export(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate if invoice is ready for export

    Returns list of validation errors if any
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

    invoice_data = {
        'id': str(invoice.id),
        'extracted_data': invoice.extracted_json or {},
        'status': invoice.status
    }

    errors = validate_invoice_for_export(invoice_data)

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'invoice_id': str(invoice.id)
    }
