"""
Comprehensive Invoice Validation Service

Implements intelligent validation rules to catch errors before they reach customers:
- Mathematical accuracy
- Date logic
- Duplicate detection
- Vendor validation
- Amount reasonableness
- Required fields
- Line item validation
"""

from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.invoice import Invoice
from app.models.vendor import Vendor
import logging

logger = logging.getLogger(__name__)


class ValidationResult:
    """Container for validation results"""

    def __init__(self):
        self.is_valid = True
        self.issues: List[Dict] = []
        self.warnings: List[Dict] = []

    def add_issue(self, type: str, severity: str, message: str, field: str = None):
        """
        Add validation issue or warning

        Args:
            type: Issue type identifier
            severity: critical, high, medium, low
            message: Human-readable message
            field: Optional field name that has the issue
        """
        issue = {
            'type': type,
            'severity': severity,
            'message': message,
            'field': field,
            'timestamp': datetime.utcnow().isoformat()
        }

        if severity in ['critical', 'high']:
            self.is_valid = False
            self.issues.append(issue)
        else:
            self.warnings.append(issue)


def validate_invoice_data(invoice: Invoice, db: Session) -> ValidationResult:
    """
    Comprehensive invoice validation

    Runs all validation checks and returns detailed results.

    Args:
        invoice: Invoice to validate
        db: Database session

    Returns:
        ValidationResult with all issues and warnings
    """
    result = ValidationResult()

    # Run all validation checks
    _validate_required_fields(invoice, result)
    _validate_math(invoice, result)
    _validate_dates(invoice, result)
    _validate_duplicates(invoice, db, result)
    _validate_vendor(invoice, db, result)
    _validate_amounts(invoice, db, result)
    _validate_line_items(invoice, result)
    _validate_confidence_scores(invoice, result)

    logger.info(f"Validation complete for invoice {invoice.id}: {len(result.issues)} issues, {len(result.warnings)} warnings")

    return result


def _validate_required_fields(invoice: Invoice, result: ValidationResult):
    """Check all required fields are present"""

    if not invoice.extracted_json:
        result.add_issue(
            type='missing_extraction',
            severity='critical',
            message="Invoice has not been processed - no extracted data available",
            field=None
        )
        return

    data = invoice.extracted_json

    required_fields = {
        'vendor_name': 'Vendor name',
        'invoice_number': 'Invoice number',
        'invoice_date': 'Invoice date',
        'total_amount': 'Total amount',
        'currency': 'Currency'
    }

    for field, display_name in required_fields.items():
        if not data.get(field):
            result.add_issue(
                type='missing_field',
                severity='high',
                message=f"Missing required field: {display_name}",
                field=field
            )


def _validate_math(invoice: Invoice, result: ValidationResult):
    """Validate mathematical accuracy"""

    if not invoice.extracted_json:
        return

    data = invoice.extracted_json

    # Check: subtotal + tax = total (within $0.01)
    if data.get('subtotal') and data.get('tax_amount') and data.get('total_amount'):
        try:
            calculated_total = Decimal(str(data['subtotal'])) + Decimal(str(data['tax_amount']))
            actual_total = Decimal(str(data['total_amount']))

            difference = abs(calculated_total - actual_total)

            if difference > Decimal('0.01'):
                result.add_issue(
                    type='math_error',
                    severity='high',
                    message=f"Math error: Subtotal (${data['subtotal']}) + Tax (${data['tax_amount']}) = ${calculated_total}, but Total shows ${actual_total}. Difference: ${difference}",
                    field='total_amount'
                )
        except (ValueError, TypeError, Decimal.InvalidOperation) as e:
            logger.warning(f"Error validating math: {e}")

    # Check: line items sum to subtotal
    if data.get('line_items') and data.get('subtotal'):
        try:
            line_total = sum(Decimal(str(item.get('amount', 0))) for item in data['line_items'])
            subtotal = Decimal(str(data['subtotal']))
            difference = abs(line_total - subtotal)

            if difference > Decimal('0.01'):
                result.add_issue(
                    type='line_items_mismatch',
                    severity='medium',
                    message=f"Line items sum to ${line_total} but subtotal shows ${subtotal} (difference: ${difference})",
                    field='line_items'
                )
        except (ValueError, TypeError, Decimal.InvalidOperation) as e:
            logger.warning(f"Error validating line items math: {e}")


def _validate_dates(invoice: Invoice, result: ValidationResult):
    """Validate date logic"""

    if not invoice.extracted_json:
        return

    data = invoice.extracted_json
    today = datetime.now().date()

    # Invoice date validation
    if data.get('invoice_date'):
        try:
            invoice_date = datetime.fromisoformat(data['invoice_date']).date()

            # Check: not in future
            if invoice_date > today:
                result.add_issue(
                    type='future_date',
                    severity='high',
                    message=f"Invoice date ({invoice_date}) is in the future",
                    field='invoice_date'
                )

            # Check: not too old (>1 year)
            if invoice_date < today - timedelta(days=365):
                result.add_issue(
                    type='old_invoice',
                    severity='medium',
                    message=f"Invoice is over 1 year old ({invoice_date})",
                    field='invoice_date'
                )
        except (ValueError, TypeError) as e:
            result.add_issue(
                type='invalid_date_format',
                severity='high',
                message=f"Invalid date format: {data['invoice_date']}",
                field='invoice_date'
            )

    # Due date validation
    if data.get('due_date') and data.get('invoice_date'):
        try:
            invoice_date = datetime.fromisoformat(data['invoice_date']).date()
            due_date = datetime.fromisoformat(data['due_date']).date()

            # Check: due date after invoice date
            if due_date < invoice_date:
                result.add_issue(
                    type='invalid_due_date',
                    severity='high',
                    message=f"Due date ({due_date}) is before invoice date ({invoice_date})",
                    field='due_date'
                )

            # Check: overdue
            if due_date < today:
                days_overdue = (today - due_date).days
                result.add_issue(
                    type='overdue',
                    severity='medium',
                    message=f"Invoice is {days_overdue} days overdue (due: {due_date})",
                    field='due_date'
                )
        except (ValueError, TypeError):
            pass


def _validate_duplicates(invoice: Invoice, db: Session, result: ValidationResult):
    """Detect possible duplicate invoices"""

    if not invoice.extracted_json:
        return

    data = invoice.extracted_json

    # Search for similar invoices in last 90 days
    ninety_days_ago = datetime.now() - timedelta(days=90)

    # Check 1: Same vendor + invoice number
    if data.get('vendor_name') and data.get('invoice_number'):
        similar = db.query(Invoice).filter(
            Invoice.id != invoice.id,
            Invoice.organization_id == invoice.organization_id,
            Invoice.extracted_json['vendor_name'].astext == data['vendor_name'],
            Invoice.extracted_json['invoice_number'].astext == data['invoice_number'],
            Invoice.created_at >= ninety_days_ago,
            Invoice.status != 'rejected'
        ).first()

        if similar:
            result.add_issue(
                type='duplicate_invoice_number',
                severity='critical',
                message=f"Possible duplicate: Invoice #{data['invoice_number']} from {data['vendor_name']} already exists (ID: {similar.id})",
                field='invoice_number'
            )
            return  # Don't check further if exact duplicate found

    # Check 2: Same vendor + similar amount (within 5%)
    if data.get('vendor_name') and data.get('total_amount'):
        try:
            amount = Decimal(str(data['total_amount']))
            lower_bound = float(amount * Decimal('0.95'))
            upper_bound = float(amount * Decimal('1.05'))

            # Use raw SQL for JSONB numeric comparison
            similar = db.execute(text("""
                SELECT id, extracted_json->>'invoice_number' as inv_num,
                       (extracted_json->>'total_amount')::decimal as amount
                FROM invoices
                WHERE id != :invoice_id
                  AND organization_id = :org_id
                  AND extracted_json->>'vendor_name' = :vendor_name
                  AND (extracted_json->>'total_amount')::decimal BETWEEN :lower AND :upper
                  AND created_at >= :date_threshold
                  AND status != 'rejected'
                LIMIT 5
            """), {
                'invoice_id': invoice.id,
                'org_id': invoice.organization_id,
                'vendor_name': data['vendor_name'],
                'lower': lower_bound,
                'upper': upper_bound,
                'date_threshold': ninety_days_ago
            }).fetchall()

            if similar:
                for row in similar:
                    result.add_issue(
                        type='duplicate_amount',
                        severity='high',
                        message=f"Possible duplicate: Similar invoice from {data['vendor_name']} with amount ${row.amount} found (Invoice: {row.inv_num or 'N/A'})",
                        field='total_amount'
                    )
        except Exception as e:
            logger.warning(f"Error checking duplicate amounts: {e}")


def _validate_vendor(invoice: Invoice, db: Session, result: ValidationResult):
    """Validate vendor information"""

    if not invoice.extracted_json:
        return

    data = invoice.extracted_json

    # Check if vendor exists
    vendor_name = data.get('vendor_name')
    if vendor_name:
        vendor = db.query(Vendor).filter(
            Vendor.organization_id == invoice.organization_id,
            Vendor.name == vendor_name
        ).first()

        if not vendor:
            result.add_issue(
                type='new_vendor',
                severity='medium',
                message=f"New vendor: '{vendor_name}' is not in the system",
                field='vendor_name'
            )
        else:
            # Validate vendor details match
            if data.get('vendor_tax_id') and vendor.tax_id:
                if data['vendor_tax_id'] != vendor.tax_id:
                    result.add_issue(
                        type='vendor_tax_id_mismatch',
                        severity='high',
                        message=f"Tax ID mismatch: Invoice shows {data['vendor_tax_id']}, but vendor record has {vendor.tax_id}",
                        field='vendor_tax_id'
                    )


def _validate_amounts(invoice: Invoice, db: Session, result: ValidationResult):
    """Validate amounts are reasonable"""

    if not invoice.extracted_json:
        return

    data = invoice.extracted_json

    if not data.get('total_amount'):
        return

    try:
        amount = Decimal(str(data['total_amount']))

        # Check: amount is positive
        if amount <= 0:
            result.add_issue(
                type='invalid_amount',
                severity='critical',
                message=f"Invalid amount: ${amount}",
                field='total_amount'
            )
            return

        # Check: amount not unreasonably large
        if amount > Decimal('1000000'):  # $1M
            result.add_issue(
                type='unusually_large',
                severity='high',
                message=f"Unusually large amount: ${amount:,.2f} - Please verify this is correct",
                field='total_amount'
            )

        # Check against vendor history (anomaly detection)
        vendor_name = data.get('vendor_name')
        if vendor_name:
            vendor = db.query(Vendor).filter(
                Vendor.organization_id == invoice.organization_id,
                Vendor.name == vendor_name
            ).first()

            if vendor and vendor.average_invoice_amount:
                avg = Decimal(str(vendor.average_invoice_amount))
                variance = abs(amount - avg) / avg

                if variance > Decimal('0.5'):  # 50% variance
                    result.add_issue(
                        type='amount_anomaly',
                        severity='medium',
                        message=f"Amount anomaly: This invoice is ${amount:,.2f}, but this vendor's average is ${avg:,.2f} ({variance*100:.0f}% difference)",
                        field='total_amount'
                    )
    except (ValueError, TypeError, Decimal.InvalidOperation) as e:
        logger.warning(f"Error validating amounts: {e}")


def _validate_line_items(invoice: Invoice, result: ValidationResult):
    """Validate line items"""

    if not invoice.extracted_json:
        return

    data = invoice.extracted_json
    line_items = data.get('line_items', [])

    if not line_items:
        result.add_issue(
            type='missing_line_items',
            severity='low',
            message="No line items found",
            field='line_items'
        )
        return

    for idx, item in enumerate(line_items):
        # Check required fields in line item
        if not item.get('description'):
            result.add_issue(
                type='missing_line_item_field',
                severity='medium',
                message=f"Line item {idx+1}: Missing description",
                field='line_items'
            )

        # Check math in line item
        try:
            if all(key in item for key in ['quantity', 'unit_price', 'amount']):
                calculated = Decimal(str(item['quantity'])) * Decimal(str(item['unit_price']))
                actual = Decimal(str(item['amount']))

                if abs(calculated - actual) > Decimal('0.01'):
                    result.add_issue(
                        type='line_item_math_error',
                        severity='medium',
                        message=f"Line item {idx+1}: {item['quantity']} × ${item['unit_price']} = ${calculated}, but shows ${actual}",
                        field='line_items'
                    )
        except (ValueError, TypeError, Decimal.InvalidOperation) as e:
            logger.warning(f"Error validating line item {idx+1} math: {e}")


def _validate_confidence_scores(invoice: Invoice, result: ValidationResult):
    """Validate AI confidence scores"""

    if invoice.overall_confidence is None:
        return

    confidence = float(invoice.overall_confidence)

    # Low overall confidence
    if confidence < 0.70:
        result.add_issue(
            type='very_low_confidence',
            severity='high',
            message=f"Very low AI confidence ({confidence:.0%}) - Manual review strongly recommended",
            field='overall_confidence'
        )
    elif confidence < 0.85:
        result.add_issue(
            type='low_confidence',
            severity='medium',
            message=f"Low AI confidence ({confidence:.0%}) - Please verify extracted data",
            field='overall_confidence'
        )

    # Check per-field confidence for critical fields
    if invoice.per_field_confidence:
        critical_fields = ['total_amount', 'vendor_name', 'invoice_number']

        for field in critical_fields:
            field_confidence = invoice.per_field_confidence.get(field)
            if field_confidence and field_confidence < 0.80:
                result.add_issue(
                    type='low_field_confidence',
                    severity='medium',
                    message=f"Low confidence for {field}: {field_confidence:.0%}",
                    field=field
                )
