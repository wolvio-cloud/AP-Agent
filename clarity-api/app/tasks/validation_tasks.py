"""
Background Tasks for Invoice Validation

Handles asynchronous validation of extracted invoice data.
"""

from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.invoice import Invoice
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name='app.tasks.validation.validate_invoice')
def validate_invoice_task(invoice_id: str):
    """
    Background task to validate invoice data

    Args:
        invoice_id: UUID of invoice to validate

    Returns:
        dict with validation results
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting validation for invoice {invoice_id}")

        # Import here to avoid circular dependency
        from app.services.validation_service import validate_invoice_data

        invoice = db.query(Invoice).filter(Invoice.id == UUID(invoice_id)).first()
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")

        # Run validation
        result = validate_invoice_data(invoice, db)

        # Update invoice with validation results
        invoice.validation_issues = result.issues
        invoice.validation_status = "valid" if result.is_valid else "has_issues"

        # If critical issues, mark for review
        if not result.is_valid:
            critical_count = sum(1 for issue in result.issues if issue['severity'] in ['critical', 'high'])
            if critical_count > 0:
                invoice.requires_review = True
                invoice.review_priority = "high" if critical_count > 2 else "medium"

        db.commit()

        logger.info(f"Validation completed for invoice {invoice_id}: {len(result.issues)} issues, {len(result.warnings)} warnings")

        return {
            'status': 'success',
            'is_valid': result.is_valid,
            'issues_count': len(result.issues),
            'warnings_count': len(result.warnings)
        }

    except Exception as e:
        logger.exception(f"Validation error for invoice {invoice_id}")
        raise

    finally:
        db.close()


@celery_app.task(name='app.tasks.validation.batch_validate')
def batch_validate_invoices_task(invoice_ids: list):
    """
    Validate multiple invoices in batch

    Args:
        invoice_ids: List of invoice UUIDs

    Returns:
        dict with batch validation results
    """
    results = []

    for invoice_id in invoice_ids:
        result = validate_invoice_task.delay(invoice_id)
        results.append({
            'invoice_id': invoice_id,
            'task_id': result.id
        })

    return {
        'status': 'completed',
        'total': len(invoice_ids),
        'tasks': results
    }
