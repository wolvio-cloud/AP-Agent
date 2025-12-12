"""
Vendor Management API Endpoints

Enhanced vendor CRUD with analytics and payment terms tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.vendor import Vendor
from app.models.invoice import Invoice
from app.services.audit_service import log_audit_event
from app.services.rbac_service import check_permission
from pydantic import BaseModel, Field

router = APIRouter()


# Pydantic Schemas
class VendorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = "net30"
    notes: Optional[str] = None


class VendorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class VendorResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    tax_id: Optional[str]
    payment_terms: Optional[str]
    is_active: bool
    notes: Optional[str]

    # Analytics
    total_invoices: int
    average_invoice_amount: Optional[Decimal]
    last_invoice_date: Optional[datetime]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VendorStats(BaseModel):
    """Vendor analytics and statistics"""
    vendor_id: uuid.UUID
    vendor_name: str
    total_invoices: int
    total_amount: Decimal
    average_amount: Decimal
    pending_invoices: int
    pending_amount: Decimal
    approved_invoices: int
    approved_amount: Decimal
    last_invoice_date: Optional[datetime]
    payment_terms: Optional[str]


@router.get("/vendors", response_model=List[VendorResponse])
async def list_vendors(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name, email, or tax ID"),
    active_only: bool = Query(True, description="Show only active vendors"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List vendors for organization with optional search and filtering

    **Permissions:** vendors.view
    """
    # Check permission
    if not check_permission(current_user, 'vendors.view', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view vendors"
        )

    query = db.query(Vendor).filter(
        Vendor.organization_id == current_user.organization_id
    )

    # Filter by active status
    if active_only:
        query = query.filter(Vendor.is_active == True)

    # Search
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Vendor.name.ilike(search_term)) |
            (Vendor.email.ilike(search_term)) |
            (Vendor.tax_id.ilike(search_term))
        )

    # Order by name
    query = query.order_by(Vendor.name.asc())

    # Pagination
    vendors = query.offset(skip).limit(limit).all()

    return vendors


@router.get("/vendors/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    vendor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get vendor by ID

    **Permissions:** vendors.view
    """
    # Check permission
    if not check_permission(current_user, 'vendors.view', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view vendors"
        )

    vendor = db.query(Vendor).filter(
        Vendor.id == vendor_id,
        Vendor.organization_id == current_user.organization_id
    ).first()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )

    return vendor


@router.post("/vendors", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor_data: VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new vendor

    **Permissions:** vendors.create
    """
    # Check permission
    if not check_permission(current_user, 'vendors.create', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create vendors"
        )

    # Check for duplicate name
    existing = db.query(Vendor).filter(
        Vendor.organization_id == current_user.organization_id,
        Vendor.name == vendor_data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vendor '{vendor_data.name}' already exists"
        )

    # Create vendor
    vendor = Vendor(
        organization_id=current_user.organization_id,
        name=vendor_data.name,
        email=vendor_data.email,
        phone=vendor_data.phone,
        address=vendor_data.address,
        tax_id=vendor_data.tax_id,
        payment_terms=vendor_data.payment_terms,
        notes=vendor_data.notes,
        is_active=True,
        total_invoices=0
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    # Audit log
    log_audit_event(
        db=db,
        event_type='vendor_created',
        action='create',
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        resource_type='vendor',
        resource_id=vendor.id,
        details={'vendor_name': vendor.name}
    )

    return vendor


@router.put("/vendors/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: uuid.UUID,
    vendor_data: VendorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update vendor

    **Permissions:** vendors.edit
    """
    # Check permission
    if not check_permission(current_user, 'vendors.edit', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to edit vendors"
        )

    # Get vendor
    vendor = db.query(Vendor).filter(
        Vendor.id == vendor_id,
        Vendor.organization_id == current_user.organization_id
    ).first()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )

    # Track changes
    changes = {}

    # Update fields
    update_fields = vendor_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        if hasattr(vendor, field) and getattr(vendor, field) != value:
            changes[field] = {'old': getattr(vendor, field), 'new': value}
            setattr(vendor, field, value)

    db.commit()
    db.refresh(vendor)

    # Audit log
    if changes:
        log_audit_event(
            db=db,
            event_type='vendor_updated',
            action='update',
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            resource_type='vendor',
            resource_id=vendor.id,
            details={'vendor_name': vendor.name, 'changes': changes}
        )

    return vendor


@router.delete("/vendors/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(
    vendor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete vendor (soft delete - marks as inactive)

    **Permissions:** vendors.delete
    """
    # Check permission
    if not check_permission(current_user, 'vendors.delete', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete vendors"
        )

    # Get vendor
    vendor = db.query(Vendor).filter(
        Vendor.id == vendor_id,
        Vendor.organization_id == current_user.organization_id
    ).first()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )

    # Soft delete (mark as inactive)
    vendor.is_active = False
    db.commit()

    # Audit log
    log_audit_event(
        db=db,
        event_type='vendor_deleted',
        action='delete',
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        resource_type='vendor',
        resource_id=vendor.id,
        details={'vendor_name': vendor.name}
    )

    return None


@router.get("/vendors/{vendor_id}/stats", response_model=VendorStats)
async def get_vendor_stats(
    vendor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get vendor analytics and statistics

    **Permissions:** vendors.view
    """
    # Check permission
    if not check_permission(current_user, 'vendors.view', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view vendor statistics"
        )

    # Get vendor
    vendor = db.query(Vendor).filter(
        Vendor.id == vendor_id,
        Vendor.organization_id == current_user.organization_id
    ).first()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )

    # Calculate statistics
    all_invoices = db.query(Invoice).filter(
        Invoice.vendor_id == vendor_id,
        Invoice.organization_id == current_user.organization_id
    )

    total_count = all_invoices.count()

    # Get amounts (from extracted_json)
    total_amount = Decimal('0.00')
    pending_amount = Decimal('0.00')
    approved_amount = Decimal('0.00')
    pending_count = 0
    approved_count = 0
    last_date = None

    for invoice in all_invoices.all():
        if invoice.extracted_json and 'total_amount' in invoice.extracted_json:
            amount = Decimal(str(invoice.extracted_json['total_amount']))
            total_amount += amount

            if invoice.status == 'pending_approval':
                pending_amount += amount
                pending_count += 1
            elif invoice.status == 'approved':
                approved_amount += amount
                approved_count += 1

        if not last_date or (invoice.created_at and invoice.created_at > last_date):
            last_date = invoice.created_at

    avg_amount = total_amount / total_count if total_count > 0 else Decimal('0.00')

    return VendorStats(
        vendor_id=vendor.id,
        vendor_name=vendor.name,
        total_invoices=total_count,
        total_amount=total_amount,
        average_amount=avg_amount,
        pending_invoices=pending_count,
        pending_amount=pending_amount,
        approved_invoices=approved_count,
        approved_amount=approved_amount,
        last_invoice_date=last_date,
        payment_terms=vendor.payment_terms
    )


@router.get("/vendors/{vendor_id}/invoices", response_model=List[dict])
async def get_vendor_invoices(
    vendor_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all invoices for a vendor

    **Permissions:** vendors.view, invoices.view
    """
    # Check permissions
    if not check_permission(current_user, 'vendors.view', db) or \
       not check_permission(current_user, 'invoices.view', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    # Verify vendor exists and belongs to organization
    vendor = db.query(Vendor).filter(
        Vendor.id == vendor_id,
        Vendor.organization_id == current_user.organization_id
    ).first()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )

    # Get invoices
    invoices = db.query(Invoice).filter(
        Invoice.vendor_id == vendor_id,
        Invoice.organization_id == current_user.organization_id
    ).order_by(desc(Invoice.created_at)).offset(skip).limit(limit).all()

    return [
        {
            'id': str(invoice.id),
            'invoice_number': invoice.extracted_json.get('invoice_number') if invoice.extracted_json else None,
            'invoice_date': invoice.extracted_json.get('invoice_date') if invoice.extracted_json else None,
            'total_amount': invoice.extracted_json.get('total_amount') if invoice.extracted_json else None,
            'currency': invoice.extracted_json.get('currency', 'USD') if invoice.extracted_json else 'USD',
            'status': invoice.status,
            'created_at': invoice.created_at.isoformat() if invoice.created_at else None
        }
        for invoice in invoices
    ]
