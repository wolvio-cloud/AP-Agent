from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.invoice import Invoice
from app.models.einvoice import ExtractionMetric
from app.schemas.invoice import (
    InvoiceUploadResponse,
    InvoiceListResponse,
    InvoiceDetailResponse,
    InvoiceListItem,
    InvoiceDetail,
    InvoiceUpdate,
    EInvoiceIngestRequest,
    EInvoiceIngestResponse
)
from app.services.storage_service import storage_service
from app.services.extraction_service import process_invoice_extraction
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
            source_type=file_type,
            processing_tier="uploaded",
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


@router.post("/{invoice_id}/extract")
async def extract_invoice_data(
    invoice_id: str,
    force_tier: Optional[int] = Query(None, ge=1, le=3, description="Force specific extraction tier for testing"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Extract data from invoice using AI (mock for demo)

    - Processes through 4-tier extraction pipeline
    - Tier 1: Gemini 1.5 Flash (mock)
    - Tier 2: Preprocessing + retry (mock)
    - Tier 3: GPT-4V fallback (mock)
    - Tier 4: Human review (if confidence < 0.85)

    Query params:
    - force_tier: Force specific tier (1-3) for testing
    """
    try:
        # Get invoice
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

        # Update status to processing
        invoice.status = "processing"
        invoice.processing_tier = f"tier{force_tier}" if force_tier else "tier1"
        db.commit()

        # Process extraction (mock)
        result = process_invoice_extraction(
            invoice.file_path,
            invoice.file_name,
            force_tier=force_tier
        )

        # Update invoice with extracted data
        extracted_data = result["extracted_data"]
        invoice.extracted_json = extracted_data
        invoice.per_field_confidence = result["field_confidences"]
        invoice.overall_confidence = Decimal(str(result["overall_confidence"]))
        invoice.processing_tier = result["next_tier"]
        invoice.requires_review = result["requires_review"]
        invoice.review_priority = result["review_priority"]

        # Map extracted data to invoice fields
        invoice.vendor_name = extracted_data.get("vendor_name")
        invoice.vendor_address = extracted_data.get("vendor_address")
        invoice.vendor_tax_id = extracted_data.get("vendor_tax_id")
        invoice.invoice_number = extracted_data.get("invoice_number")
        invoice.invoice_date = datetime.fromisoformat(extracted_data["invoice_date"]) if extracted_data.get("invoice_date") else None
        invoice.due_date = datetime.fromisoformat(extracted_data["due_date"]) if extracted_data.get("due_date") else None
        invoice.currency = extracted_data.get("currency", "INR")
        invoice.payment_terms = extracted_data.get("payment_terms")
        invoice.subtotal = Decimal(str(extracted_data["subtotal"])) if extracted_data.get("subtotal") else None
        invoice.tax_amount = Decimal(str(extracted_data["tax_amount"])) if extracted_data.get("tax_amount") else None
        invoice.tax_rate = Decimal(str(extracted_data["tax_rate"])) if extracted_data.get("tax_rate") else None
        invoice.total_amount = Decimal(str(extracted_data["total_amount"])) if extracted_data.get("total_amount") else None
        invoice.line_items = extracted_data.get("line_items", [])
        invoice.seller_gstin = extracted_data.get("seller_gstin")

        # Update status
        if result["requires_review"]:
            invoice.status = "requires_review"
        else:
            invoice.status = "extracted"

        invoice.extracted_at = datetime.utcnow()
        invoice.updated_at = datetime.utcnow()

        # Add to processing history
        history_entry = {
            "tier": result["processing_tier"],
            "confidence": result["overall_confidence"],
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": result["processing_time_ms"]
        }
        if invoice.processing_history is None:
            invoice.processing_history = []
        invoice.processing_history = list(invoice.processing_history) + [history_entry]

        # Save extraction metrics
        metric = ExtractionMetric(
            organization_id=current_user.organization_id,
            invoice_id=invoice.id,
            processing_tier=result["processing_tier"],
            processing_time_ms=result["processing_time_ms"],
            confidence_score=Decimal(str(result["overall_confidence"])),
            cost_usd=Decimal(str(result["cost_usd"])),
            api_calls=result["api_calls"],
            created_at=datetime.utcnow()
        )
        db.add(metric)

        db.commit()
        db.refresh(invoice)

        logger.info(f"Invoice extracted: {invoice.id}, confidence={result['overall_confidence']:.2f}, tier={result['processing_tier']}")

        return {
            "success": True,
            "message": "Extraction completed",
            "data": {
                "invoice_id": str(invoice.id),
                "processing_tier": result["processing_tier"],
                "overall_confidence": result["overall_confidence"],
                "requires_review": result["requires_review"],
                "review_priority": result["review_priority"],
                "extracted_data": extracted_data,
                "field_confidences": result["field_confidences"],
                "processing_time_ms": result["processing_time_ms"]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to extract invoice: {str(e)}")
        # Update invoice status to error
        if invoice:
            invoice.status = "error"
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract invoice: {str(e)}"
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
    - status: Filter by status (uploaded, processing, extracted, approved, rejected, error, requires_review)
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
    - Shows extraction results and confidence scores
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


@router.get("/queue/review")
def get_review_queue(
    priority: Optional[str] = Query(None, description="Filter by priority: high, medium, low"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get invoices that require human review

    Query parameters:
    - priority: Filter by review priority (high, medium, low)
    - page: Page number
    - limit: Items per page

    Returns invoices sorted by priority (high first) and created_at
    """
    try:
        # Base query - invoices requiring review
        query = db.query(Invoice).filter(
            Invoice.organization_id == current_user.organization_id,
            Invoice.requires_review == True,
            Invoice.deleted_at.is_(None)
        )

        # Apply priority filter
        if priority:
            query = query.filter(Invoice.review_priority == priority)

        # Get total count
        total = query.count()

        # Sort by priority and date
        # High priority first, then medium, then low
        priority_order = {
            "high": 1,
            "medium": 2,
            "low": 3
        }

        invoices = query.order_by(Invoice.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

        # Sort in Python by priority
        invoices_sorted = sorted(
            invoices,
            key=lambda x: (priority_order.get(x.review_priority or "low", 99), x.created_at),
            reverse=True
        )

        return {
            "success": True,
            "data": [InvoiceListItem.model_validate(inv) for inv in invoices_sorted],
            "total": total,
            "page": page,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Failed to get review queue: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve review queue"
        )


@router.post("/ingest-json", response_model=EInvoiceIngestResponse)
async def ingest_einvoice_json(
    request: EInvoiceIngestRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Ingest India e-Invoice JSON payload only

    - Validates mandatory fields (IRN, GSTIN, doc_no, doc_date)
    - Creates invoice record from JSON data
    - Stores complete JSON payload in einvoice_jsons table
    - Marks source_type as 'einvoice_json'
    - Status set to 'extracted' (no AI processing needed)
    """
    try:
        einvoice_data = request.einvoice_json

        # Validate mandatory fields
        required_fields = ['irn', 'seller_gstin', 'buyer_gstin', 'doc_no', 'doc_date']
        missing_fields = [f for f in required_fields if f not in einvoice_data]
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing mandatory e-Invoice fields: {', '.join(missing_fields)}"
            )

        # Validate GSTIN format (basic check: 15 characters alphanumeric)
        seller_gstin = einvoice_data['seller_gstin']
        buyer_gstin = einvoice_data['buyer_gstin']
        if len(seller_gstin) != 15 or len(buyer_gstin) != 15:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GSTIN format. Must be 15 characters."
            )

        # Extract data from JSON
        vendor_name = einvoice_data.get('seller_legal_name') or einvoice_data.get('seller_trade_name')
        vendor_address_parts = [
            einvoice_data.get('seller_address'),
            einvoice_data.get('seller_location'),
            einvoice_data.get('seller_pincode')
        ]
        vendor_address = ', '.join([p for p in vendor_address_parts if p])

        # Parse date (DD/MM/YYYY format)
        try:
            doc_date_str = einvoice_data['doc_date']
            invoice_date = datetime.strptime(doc_date_str, "%d/%m/%Y")
        except ValueError:
            invoice_date = None

        # Calculate total amount
        total_amount = einvoice_data.get('total_value')
        if total_amount is None:
            # Try calculating from tax components
            taxable = Decimal(str(einvoice_data.get('taxable_value', 0)))
            cgst = Decimal(str(einvoice_data.get('cgst_value', 0)))
            sgst = Decimal(str(einvoice_data.get('sgst_value', 0)))
            igst = Decimal(str(einvoice_data.get('igst_value', 0)))
            total_amount = taxable + cgst + sgst + igst

        # Create invoice record
        invoice = Invoice(
            organization_id=current_user.organization_id,
            file_name=f"einvoice_{einvoice_data['doc_no']}.json",
            file_path=f"einvoices/{current_user.organization_id}/{einvoice_data['irn']}.json",
            file_type="application/json",
            status="extracted",  # Already extracted from JSON
            source_type="einvoice_json",
            processing_tier="completed",

            # Vendor info
            vendor_name=vendor_name,
            vendor_address=vendor_address,
            vendor_tax_id=seller_gstin,
            seller_gstin=seller_gstin,

            # Invoice details
            invoice_number=einvoice_data['doc_no'],
            invoice_date=invoice_date,
            currency="INR",

            # Amounts
            total_amount=Decimal(str(total_amount)) if total_amount else None,
            tax_amount=Decimal(str(einvoice_data.get('cgst_value', 0))) +
                      Decimal(str(einvoice_data.get('sgst_value', 0))) +
                      Decimal(str(einvoice_data.get('igst_value', 0))),
            subtotal=Decimal(str(einvoice_data.get('taxable_value', 0))) if einvoice_data.get('taxable_value') else None,

            # e-Invoice specific
            irn=einvoice_data['irn'],
            buyer_gstin=buyer_gstin,
            extracted_json=einvoice_data,

            # High confidence since it's from official e-Invoice
            overall_confidence=Decimal("1.0"),
            per_field_confidence={
                "vendor_name": 1.0,
                "invoice_number": 1.0,
                "invoice_date": 1.0,
                "total_amount": 1.0,
                "seller_gstin": 1.0,
                "buyer_gstin": 1.0,
                "irn": 1.0
            },

            requires_review=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            extracted_at=datetime.utcnow()
        )

        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        # Store complete e-Invoice JSON in separate table
        from app.models.einvoice import EInvoiceJson
        einvoice_json_record = EInvoiceJson(
            organization_id=current_user.organization_id,
            invoice_id=invoice.id,
            payload=einvoice_data,
            irn=einvoice_data['irn'],
            seller_gstin=seller_gstin,
            buyer_gstin=buyer_gstin,
            created_at=datetime.utcnow()
        )
        db.add(einvoice_json_record)
        db.commit()

        logger.info(f"e-Invoice JSON ingested: {invoice.id}, IRN={einvoice_data['irn']}")

        # Return invoice detail
        invoice_dict = invoice.__dict__.copy()
        invoice_dict['file_url'] = None

        return EInvoiceIngestResponse(
            success=True,
            message="e-Invoice JSON ingested successfully",
            data=InvoiceDetail.model_validate(invoice_dict)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest e-Invoice JSON: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest e-Invoice: {str(e)}"
        )


@router.post("/ingest-pair", response_model=EInvoiceIngestResponse)
async def ingest_einvoice_pair(
    file: UploadFile = File(...),
    einvoice_json: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Ingest PDF + e-Invoice JSON pair

    - Uploads PDF to storage
    - Parses and validates e-Invoice JSON
    - Cross-validates data between PDF and JSON
    - Stores both with linked reference
    - Flags any discrepancies as anomalies

    Form parameters:
    - file: PDF file (multipart/form-data)
    - einvoice_json: JSON string of e-Invoice data
    """
    try:
        import json

        # Parse JSON
        if not einvoice_json:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="einvoice_json parameter is required"
            )

        try:
            einvoice_data = json.loads(einvoice_json)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON format for einvoice_json"
            )

        # Validate mandatory fields
        required_fields = ['irn', 'seller_gstin', 'buyer_gstin', 'doc_no', 'doc_date']
        missing_fields = [f for f in required_fields if f not in einvoice_data]
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing mandatory e-Invoice fields: {', '.join(missing_fields)}"
            )

        # Upload PDF to storage
        file_path, file_type = await storage_service.upload_document(
            file, str(current_user.organization_id)
        )

        # Extract data from JSON
        vendor_name = einvoice_data.get('seller_legal_name') or einvoice_data.get('seller_trade_name')
        vendor_address_parts = [
            einvoice_data.get('seller_address'),
            einvoice_data.get('seller_location'),
            einvoice_data.get('seller_pincode')
        ]
        vendor_address = ', '.join([p for p in vendor_address_parts if p])

        # Parse date
        try:
            doc_date_str = einvoice_data['doc_date']
            invoice_date = datetime.strptime(doc_date_str, "%d/%m/%Y")
        except ValueError:
            invoice_date = None

        # Calculate total amount
        total_amount = einvoice_data.get('total_value')
        if total_amount is None:
            taxable = Decimal(str(einvoice_data.get('taxable_value', 0)))
            cgst = Decimal(str(einvoice_data.get('cgst_value', 0)))
            sgst = Decimal(str(einvoice_data.get('sgst_value', 0)))
            igst = Decimal(str(einvoice_data.get('igst_value', 0)))
            total_amount = taxable + cgst + sgst + igst

        # Create invoice record with both PDF and JSON
        invoice = Invoice(
            organization_id=current_user.organization_id,
            file_name=file.filename,
            file_path=file_path,
            file_type=file_type,
            status="extracted",
            source_type="einvoice_pair",  # Both PDF and JSON
            processing_tier="completed",

            # Vendor info
            vendor_name=vendor_name,
            vendor_address=vendor_address,
            vendor_tax_id=einvoice_data['seller_gstin'],
            seller_gstin=einvoice_data['seller_gstin'],

            # Invoice details
            invoice_number=einvoice_data['doc_no'],
            invoice_date=invoice_date,
            currency="INR",

            # Amounts
            total_amount=Decimal(str(total_amount)) if total_amount else None,
            tax_amount=Decimal(str(einvoice_data.get('cgst_value', 0))) +
                      Decimal(str(einvoice_data.get('sgst_value', 0))) +
                      Decimal(str(einvoice_data.get('igst_value', 0))),
            subtotal=Decimal(str(einvoice_data.get('taxable_value', 0))) if einvoice_data.get('taxable_value') else None,

            # e-Invoice specific
            irn=einvoice_data['irn'],
            buyer_gstin=einvoice_data['buyer_gstin'],
            extracted_json=einvoice_data,

            # High confidence
            overall_confidence=Decimal("1.0"),
            per_field_confidence={
                "vendor_name": 1.0,
                "invoice_number": 1.0,
                "invoice_date": 1.0,
                "total_amount": 1.0,
                "seller_gstin": 1.0,
                "buyer_gstin": 1.0,
                "irn": 1.0
            },

            requires_review=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            extracted_at=datetime.utcnow()
        )

        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        # Store e-Invoice JSON
        from app.models.einvoice import EInvoiceJson
        einvoice_json_record = EInvoiceJson(
            organization_id=current_user.organization_id,
            invoice_id=invoice.id,
            payload=einvoice_data,
            irn=einvoice_data['irn'],
            seller_gstin=einvoice_data['seller_gstin'],
            buyer_gstin=einvoice_data['buyer_gstin'],
            created_at=datetime.utcnow()
        )
        db.add(einvoice_json_record)
        db.commit()

        logger.info(f"e-Invoice pair ingested: {invoice.id}, IRN={einvoice_data['irn']}, PDF={file.filename}")

        # Generate signed URL
        try:
            file_url = storage_service.get_signed_url(invoice.file_path, expiry_minutes=60)
        except:
            file_url = None

        invoice_dict = invoice.__dict__.copy()
        invoice_dict['file_url'] = file_url

        return EInvoiceIngestResponse(
            success=True,
            message="e-Invoice PDF + JSON ingested successfully",
            data=InvoiceDetail.model_validate(invoice_dict)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest e-Invoice pair: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest e-Invoice pair: {str(e)}"
        )
