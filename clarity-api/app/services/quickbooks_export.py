"""
QuickBooks Export Service - MVP Version

Generates IIF (Intuit Interchange Format) files for manual import into QuickBooks.

For MVP: User downloads IIF file and imports manually into QuickBooks.
Later: OAuth integration for automatic sync.
"""

from typing import List, Dict
from datetime import datetime
import io


def generate_iif_file(invoices: List[Dict]) -> str:
    """
    Generate QuickBooks IIF file from invoices

    IIF Format:
    - Tab-delimited text file
    - Header row defines columns
    - Data rows follow

    Args:
        invoices: List of invoice dictionaries with extracted data

    Returns:
        IIF file content as string
    """

    lines = []

    # Header for Bills (Accounts Payable)
    lines.append("!TRNS\tTRNSID\tTRNSTYPE\tDATE\tACCNT\tNAME\tAMOUNT\tDOCNUM\tMEMO")
    lines.append("!SPL\tSPLID\tTRNSTYPE\tDATE\tACCNT\tAMOUNT\tDOCNUM\tMEMO")
    lines.append("!ENDTRNS")

    # Process each invoice
    for invoice in invoices:
        data = invoice.get('extracted_data', {})

        # Transaction header (Bill)
        trns_id = f"BILL-{invoice['id'][:8]}"
        date = data.get('invoice_date', datetime.now().strftime('%m/%d/%Y'))
        vendor = data.get('vendor_name', 'Unknown Vendor')
        total = data.get('total_amount', 0)
        invoice_num = data.get('invoice_number', 'N/A')
        memo = f"Invoice {invoice_num}"

        lines.append(f"TRNS\t{trns_id}\tBILL\t{date}\tAccounts Payable\t{vendor}\t{total}\t{invoice_num}\t{memo}")

        # Split lines (line items or single expense)
        line_items = data.get('line_items', [])

        if line_items:
            # Multiple line items
            for idx, item in enumerate(line_items):
                spl_id = f"{trns_id}-{idx}"
                description = item.get('description', 'Expense')
                amount = -float(item.get('amount', 0))  # Negative for expense
                gl_code = data.get('gl_account', '6000')  # Default to expense account

                lines.append(f"SPL\t{spl_id}\tBILL\t{date}\t{gl_code}\t{amount}\t{invoice_num}\t{description}")
        else:
            # Single expense line
            spl_id = f"{trns_id}-0"
            amount = -float(total)  # Negative for expense
            gl_code = data.get('gl_account', '6000')

            lines.append(f"SPL\t{spl_id}\tBILL\t{date}\t{gl_code}\t{amount}\t{invoice_num}\t{memo}")

        lines.append("ENDTRNS")

    return "\n".join(lines)


def generate_qbo_iif(invoice_data: Dict) -> str:
    """
    Generate IIF for a single invoice

    Args:
        invoice_data: Single invoice dictionary

    Returns:
        IIF file content
    """
    return generate_iif_file([invoice_data])


def validate_invoice_for_export(invoice_data: Dict) -> List[str]:
    """
    Validate invoice data before export

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    data = invoice_data.get('extracted_data', {})

    # Required fields
    if not data.get('vendor_name'):
        errors.append("Vendor name is required")

    if not data.get('invoice_number'):
        errors.append("Invoice number is required")

    if not data.get('total_amount') or data['total_amount'] <= 0:
        errors.append("Total amount must be greater than 0")

    if not data.get('invoice_date'):
        errors.append("Invoice date is required")

    return errors


# ============= CSV Export (Alternative) =============

def generate_csv_export(invoices: List[Dict]) -> str:
    """
    Generate CSV export as alternative to IIF

    Simpler format that can be imported into Excel/Google Sheets
    and then manually entered into QuickBooks
    """
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'Invoice Number',
        'Vendor',
        'Date',
        'Due Date',
        'Amount',
        'Tax',
        'Total',
        'GL Account',
        'Status'
    ])

    # Data rows
    for invoice in invoices:
        data = invoice.get('extracted_data', {})
        writer.writerow([
            data.get('invoice_number', ''),
            data.get('vendor_name', ''),
            data.get('invoice_date', ''),
            data.get('due_date', ''),
            data.get('subtotal', 0),
            data.get('tax_amount', 0),
            data.get('total_amount', 0),
            data.get('gl_account', '6000'),
            invoice.get('status', 'pending')
        ])

    return output.getvalue()
