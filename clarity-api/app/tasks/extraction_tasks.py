"""
Background Tasks for Invoice Extraction

Handles asynchronous invoice processing through 4-tier AI pipeline.
"""

from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.extraction_service import process_invoice_extraction
from app.models.invoice import Invoice
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='app.tasks.extraction.process_invoice')
def process_invoice_task(self, invoice_id: str):
    """
    Background task to process invoice extraction

    Args:
        invoice_id: UUID of invoice to process

    Returns:
        dict with processing results
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting extraction for invoice {invoice_id}")

        # Get invoice
        invoice = db.query(Invoice).filter(Invoice.id == UUID(invoice_id)).first()
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")

        # Update invoice status
        invoice.status = "processing"
        db.commit()

        # Update task status
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Extracting data...', 'progress': 25}
        )

        # Process extraction (uses mock for now)
        result = process_invoice_extraction(UUID(invoice_id), db)

        self.update_state(
            state='PROCESSING',
            meta={'status': 'Validating...', 'progress': 75}
        )

        # Run validation
        from app.tasks.validation_tasks import validate_invoice_task
        validate_invoice_task.delay(invoice_id)

        logger.info(f"Completed extraction for invoice {invoice_id}")

        return {
            'status': 'success',
            'invoice_id': invoice_id,
            'confidence': float(result.get('overall_confidence', 0)),
            'requires_review': result.get('requires_review', False),
            'processing_tier': result.get('processing_tier', 'unknown')
        }

    except Exception as e:
        logger.exception(f"Error processing invoice {invoice_id}")

        # Update invoice status to error
        try:
            invoice = db.query(Invoice).filter(Invoice.id == UUID(invoice_id)).first()
            if invoice:
                invoice.status = "error"
                db.commit()
        except:
            pass

        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise

    finally:
        db.close()


@celery_app.task(bind=True, name='app.tasks.extraction.batch_process')
def batch_process_invoices_task(self, invoice_ids: list):
    """
    Process multiple invoices in sequence

    Args:
        invoice_ids: List of invoice UUIDs

    Returns:
        dict with batch processing results
    """
    results = []
    total = len(invoice_ids)

    for idx, invoice_id in enumerate(invoice_ids):
        self.update_state(
            state='PROCESSING',
            meta={
                'current': idx + 1,
                'total': total,
                'status': f'Processing invoice {idx + 1} of {total}'
            }
        )

        # Queue individual extraction task
        result = process_invoice_task.apply_async(args=[invoice_id])
        results.append({
            'invoice_id': invoice_id,
            'task_id': result.id
        })

    return {
        'status': 'completed',
        'total': total,
        'tasks': results
    }


@celery_app.task(name='app.tasks.extraction.retry_failed')
def retry_failed_extraction_task(invoice_id: str, force_tier: int = None):
    """
    Retry extraction for failed invoice

    Args:
        invoice_id: UUID of invoice to retry
        force_tier: Optional tier to force (for testing)
    """
    db = SessionLocal()
    try:
        invoice = db.query(Invoice).filter(Invoice.id == UUID(invoice_id)).first()
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")

        # Reset status
        invoice.status = "processing"
        invoice.processing_tier = "uploaded"
        db.commit()

        # Trigger extraction
        result = process_invoice_extraction(UUID(invoice_id), db, force_tier=force_tier)

        logger.info(f"Retry completed for invoice {invoice_id}")
        return result

    finally:
        db.close()
