"""
Analytics Dashboard API Endpoints

Provides comprehensive analytics and metrics for invoice processing, costs, and trends.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.services.rbac_service import check_permission
from pydantic import BaseModel, Field

router = APIRouter()


# Pydantic Schemas
class DashboardStats(BaseModel):
    """High-level dashboard statistics"""
    # Invoices
    total_invoices: int
    pending_invoices: int
    approved_invoices: int
    rejected_invoices: int
    processing_invoices: int

    # Amounts
    total_amount: Decimal
    pending_amount: Decimal
    approved_amount: Decimal

    # Vendors
    total_vendors: int
    active_vendors: int

    # Processing metrics
    average_processing_time_hours: Optional[float]
    invoices_this_month: int
    invoices_last_month: int

    # Validation
    invoices_with_issues: int
    validation_accuracy_percent: float


class InvoiceStatusBreakdown(BaseModel):
    """Invoice count by status"""
    status: str
    count: int
    total_amount: Decimal


class MonthlyTrend(BaseModel):
    """Monthly invoice trends"""
    month: str  # YYYY-MM
    invoice_count: int
    total_amount: Decimal
    average_amount: Decimal
    approved_count: int
    rejected_count: int


class VendorSpendAnalysis(BaseModel):
    """Top vendors by spend"""
    vendor_id: uuid.UUID
    vendor_name: str
    invoice_count: int
    total_spend: Decimal
    average_invoice: Decimal
    last_invoice_date: Optional[datetime]


class ValidationMetrics(BaseModel):
    """Validation and quality metrics"""
    total_invoices: int
    valid_invoices: int
    invoices_with_issues: int
    invoices_with_warnings: int
    accuracy_percent: float

    # Common issues
    top_validation_issues: List[Dict[str, int]]  # [{issue_type: count}]


class ProcessingPerformance(BaseModel):
    """Processing time and performance metrics"""
    total_processed: int
    average_processing_time_minutes: float
    median_processing_time_minutes: float
    fastest_processing_minutes: float
    slowest_processing_minutes: float

    # By status
    average_extraction_time_minutes: float
    average_validation_time_minutes: float
    average_approval_time_minutes: float


@router.get("/analytics/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get high-level dashboard statistics

    **Permissions:** analytics.view
    """
    # Check permission
    if not check_permission(current_user, 'analytics.view', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view analytics"
        )

    # Date range
    start_date = datetime.utcnow() - timedelta(days=days)

    # Base query
    invoices = db.query(Invoice).filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.created_at >= start_date
    )

    # Count by status
    total_count = invoices.count()
    pending_count = invoices.filter(Invoice.status == 'pending_approval').count()
    approved_count = invoices.filter(Invoice.status == 'approved').count()
    rejected_count = invoices.filter(Invoice.status == 'rejected').count()
    processing_count = invoices.filter(Invoice.status.in_(['processing', 'extracting'])).count()

    # Calculate amounts
    total_amount = Decimal('0.00')
    pending_amount = Decimal('0.00')
    approved_amount = Decimal('0.00')
    issues_count = 0

    for invoice in invoices.all():
        if invoice.extracted_json and 'total_amount' in invoice.extracted_json:
            amount = Decimal(str(invoice.extracted_json['total_amount']))
            total_amount += amount

            if invoice.status == 'pending_approval':
                pending_amount += amount
            elif invoice.status == 'approved':
                approved_amount += amount

        # Check for validation issues
        if invoice.validation_status == 'has_issues':
            issues_count += 1

    # Vendor counts
    vendor_query = db.query(Vendor).filter(
        Vendor.organization_id == current_user.organization_id
    )
    total_vendors = vendor_query.count()
    active_vendors = vendor_query.filter(Vendor.is_active == True).count()

    # Monthly trends
    now = datetime.utcnow()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

    this_month_count = db.query(Invoice).filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.created_at >= this_month_start
    ).count()

    last_month_count = db.query(Invoice).filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.created_at >= last_month_start,
        Invoice.created_at < this_month_start
    ).count()

    # Processing time (mock calculation - would need actual timestamps)
    avg_processing_time = None  # TODO: Calculate from actual processing timestamps

    # Validation accuracy
    valid_count = total_count - issues_count
    accuracy = (valid_count / total_count * 100) if total_count > 0 else 100.0

    return DashboardStats(
        total_invoices=total_count,
        pending_invoices=pending_count,
        approved_invoices=approved_count,
        rejected_invoices=rejected_count,
        processing_invoices=processing_count,
        total_amount=total_amount,
        pending_amount=pending_amount,
        approved_amount=approved_amount,
        total_vendors=total_vendors,
        active_vendors=active_vendors,
        average_processing_time_hours=avg_processing_time,
        invoices_this_month=this_month_count,
        invoices_last_month=last_month_count,
        invoices_with_issues=issues_count,
        validation_accuracy_percent=round(accuracy, 2)
    )


@router.get("/analytics/status-breakdown", response_model=List[InvoiceStatusBreakdown])
async def get_status_breakdown(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get invoice count and amount breakdown by status

    **Permissions:** analytics.view
    """
    # Check permission
    if not check_permission(current_user, 'analytics.view', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view analytics"
        )

    start_date = datetime.utcnow() - timedelta(days=days)

    invoices = db.query(Invoice).filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.created_at >= start_date
    ).all()

    # Group by status
    status_map: Dict[str, Dict] = {}

    for invoice in invoices:
        status_key = invoice.status or 'unknown'

        if status_key not in status_map:
            status_map[status_key] = {
                'status': status_key,
                'count': 0,
                'total_amount': Decimal('0.00')
            }

        status_map[status_key]['count'] += 1

        if invoice.extracted_json and 'total_amount' in invoice.extracted_json:
            amount = Decimal(str(invoice.extracted_json['total_amount']))
            status_map[status_key]['total_amount'] += amount

    return [
        InvoiceStatusBreakdown(**data)
        for data in status_map.values()
    ]


@router.get("/analytics/monthly-trends", response_model=List[MonthlyTrend])
async def get_monthly_trends(
    months: int = Query(12, ge=1, le=24, description="Number of months to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get monthly invoice trends

    **Permissions:** analytics.view
    """
    # Check permission
    if not check_permission(current_user, 'analytics.view', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view analytics"
        )

    # Get invoices for the period
    start_date = datetime.utcnow() - timedelta(days=months * 31)

    invoices = db.query(Invoice).filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.created_at >= start_date
    ).all()

    # Group by month
    monthly_data: Dict[str, Dict] = {}

    for invoice in invoices:
        if not invoice.created_at:
            continue

        month_key = invoice.created_at.strftime('%Y-%m')

        if month_key not in monthly_data:
            monthly_data[month_key] = {
                'month': month_key,
                'invoice_count': 0,
                'total_amount': Decimal('0.00'),
                'approved_count': 0,
                'rejected_count': 0
            }

        monthly_data[month_key]['invoice_count'] += 1

        if invoice.status == 'approved':
            monthly_data[month_key]['approved_count'] += 1
        elif invoice.status == 'rejected':
            monthly_data[month_key]['rejected_count'] += 1

        if invoice.extracted_json and 'total_amount' in invoice.extracted_json:
            amount = Decimal(str(invoice.extracted_json['total_amount']))
            monthly_data[month_key]['total_amount'] += amount

    # Calculate averages and create response
    trends = []
    for month_key in sorted(monthly_data.keys()):
        data = monthly_data[month_key]
        avg_amount = data['total_amount'] / data['invoice_count'] if data['invoice_count'] > 0 else Decimal('0.00')

        trends.append(MonthlyTrend(
            month=data['month'],
            invoice_count=data['invoice_count'],
            total_amount=data['total_amount'],
            average_amount=avg_amount,
            approved_count=data['approved_count'],
            rejected_count=data['rejected_count']
        ))

    return trends


@router.get("/analytics/top-vendors", response_model=List[VendorSpendAnalysis])
async def get_top_vendors(
    limit: int = Query(10, ge=1, le=50, description="Number of top vendors to return"),
    days: int = Query(365, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get top vendors by spend

    **Permissions:** analytics.view
    """
    # Check permission
    if not check_permission(current_user, 'analytics.view', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view analytics"
        )

    start_date = datetime.utcnow() - timedelta(days=days)

    # Get all invoices with vendors
    invoices = db.query(Invoice).filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.created_at >= start_date,
        Invoice.vendor_id.isnot(None)
    ).all()

    # Group by vendor
    vendor_data: Dict[uuid.UUID, Dict] = {}

    for invoice in invoices:
        vendor_id = invoice.vendor_id

        if vendor_id not in vendor_data:
            vendor_data[vendor_id] = {
                'invoice_count': 0,
                'total_spend': Decimal('0.00'),
                'last_invoice_date': None
            }

        vendor_data[vendor_id]['invoice_count'] += 1

        if invoice.extracted_json and 'total_amount' in invoice.extracted_json:
            amount = Decimal(str(invoice.extracted_json['total_amount']))
            vendor_data[vendor_id]['total_spend'] += amount

        if not vendor_data[vendor_id]['last_invoice_date'] or \
           (invoice.created_at and invoice.created_at > vendor_data[vendor_id]['last_invoice_date']):
            vendor_data[vendor_id]['last_invoice_date'] = invoice.created_at

    # Get vendor details and create response
    results = []

    for vendor_id, data in vendor_data.items():
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()

        if vendor:
            avg_invoice = data['total_spend'] / data['invoice_count'] if data['invoice_count'] > 0 else Decimal('0.00')

            results.append(VendorSpendAnalysis(
                vendor_id=vendor.id,
                vendor_name=vendor.name,
                invoice_count=data['invoice_count'],
                total_spend=data['total_spend'],
                average_invoice=avg_invoice,
                last_invoice_date=data['last_invoice_date']
            ))

    # Sort by total spend and limit
    results.sort(key=lambda x: x.total_spend, reverse=True)

    return results[:limit]


@router.get("/analytics/validation-metrics", response_model=ValidationMetrics)
async def get_validation_metrics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get validation and quality metrics

    **Permissions:** analytics.view
    """
    # Check permission
    if not check_permission(current_user, 'analytics.view', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view analytics"
        )

    start_date = datetime.utcnow() - timedelta(days=days)

    invoices = db.query(Invoice).filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.created_at >= start_date
    ).all()

    total_count = len(invoices)
    valid_count = 0
    issues_count = 0
    warnings_count = 0

    # Track issue types
    issue_types: Dict[str, int] = {}

    for invoice in invoices:
        if invoice.validation_status == 'valid':
            valid_count += 1
        elif invoice.validation_status == 'has_issues':
            issues_count += 1
        elif invoice.validation_status == 'has_warnings':
            warnings_count += 1

        # Extract issue types from validation_issues JSONB
        if invoice.validation_issues:
            for issue in invoice.validation_issues:
                issue_type = issue.get('type', 'unknown')
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

    # Calculate accuracy
    accuracy = (valid_count / total_count * 100) if total_count > 0 else 100.0

    # Get top issues
    top_issues = [
        {issue_type: count}
        for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    return ValidationMetrics(
        total_invoices=total_count,
        valid_invoices=valid_count,
        invoices_with_issues=issues_count,
        invoices_with_warnings=warnings_count,
        accuracy_percent=round(accuracy, 2),
        top_validation_issues=top_issues
    )
