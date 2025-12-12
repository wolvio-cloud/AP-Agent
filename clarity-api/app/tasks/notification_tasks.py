"""
Background Tasks for Notifications

Handles asynchronous email and notification sending.
"""

from app.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name='app.tasks.notifications.send_email')
def send_email_task(to_email: str, subject: str, body: str, cc: list = None):
    """
    Send email notification

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (HTML supported)
        cc: Optional list of CC recipients

    Returns:
        dict with send status

    TODO: Integrate with SendGrid/AWS SES for production
    """
    logger.info(f"[MOCK] Sending email to {to_email}: {subject}")
    logger.info(f"[MOCK] Body: {body[:100]}...")

    # TODO: Replace with real email service
    # Example with SendGrid:
    # from sendgrid import SendGridAPIClient
    # from sendgrid.helpers.mail import Mail
    #
    # message = Mail(
    #     from_email='noreply@clarityap.com',
    #     to_emails=to_email,
    #     subject=subject,
    #     html_content=body
    # )
    # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    # response = sg.send(message)

    return {
        'status': 'sent',
        'to': to_email,
        'subject': subject
    }


@celery_app.task(name='app.tasks.notifications.send_approval_request')
def send_approval_request_task(invoice_id: str, approver_email: str, approver_name: str = None):
    """
    Send approval request notification

    Args:
        invoice_id: UUID of invoice needing approval
        approver_email: Email of approver
        approver_name: Optional name of approver
    """
    subject = f"Invoice Approval Required - {invoice_id[:8]}"

    body = f"""
    <html>
    <body>
        <h2>Invoice Approval Required</h2>
        <p>Hello {approver_name or 'there'},</p>
        <p>An invoice requires your approval in Clarity AP.</p>
        <p><strong>Invoice ID:</strong> {invoice_id}</p>
        <p>
            <a href="https://app.clarityap.com/invoices/{invoice_id}"
               style="background-color: #3b82f6; color: white; padding: 10px 20px;
                      text-decoration: none; border-radius: 5px;">
                Review Invoice
            </a>
        </p>
        <p>Please log in to Clarity AP to review and approve this invoice.</p>
        <p>Thank you!</p>
    </body>
    </html>
    """

    return send_email_task.delay(approver_email, subject, body)


@celery_app.task(name='app.tasks.notifications.send_extraction_complete')
def send_extraction_complete_task(user_email: str, invoice_id: str, confidence: float, requires_review: bool):
    """
    Notify user that invoice extraction is complete

    Args:
        user_email: User who uploaded the invoice
        invoice_id: UUID of processed invoice
        confidence: Overall confidence score
        requires_review: Whether invoice needs review
    """
    subject = "Invoice Processing Complete"

    if requires_review:
        body = f"""
        <html>
        <body>
            <h2>Invoice Needs Review</h2>
            <p>Your invoice has been processed but requires review due to low confidence ({confidence:.0%}).</p>
            <p><strong>Invoice ID:</strong> {invoice_id}</p>
            <p>
                <a href="https://app.clarityap.com/invoices/{invoice_id}">
                    Review Invoice
                </a>
            </p>
        </body>
        </html>
        """
    else:
        body = f"""
        <html>
        <body>
            <h2>Invoice Successfully Processed</h2>
            <p>Your invoice has been successfully extracted with {confidence:.0%} confidence.</p>
            <p><strong>Invoice ID:</strong> {invoice_id}</p>
            <p>
                <a href="https://app.clarityap.com/invoices/{invoice_id}">
                    View Invoice
                </a>
            </p>
        </body>
        </html>
        """

    return send_email_task.delay(user_email, subject, body)


@celery_app.task(name='app.tasks.notifications.send_invoice_approved')
def send_invoice_approved_task(user_email: str, invoice_id: str, approver_name: str):
    """
    Notify that invoice has been approved

    Args:
        user_email: User to notify
        invoice_id: UUID of approved invoice
        approver_name: Name of person who approved
    """
    subject = "Invoice Approved"

    body = f"""
    <html>
    <body>
        <h2>Invoice Approved</h2>
        <p>Your invoice has been approved by {approver_name}.</p>
        <p><strong>Invoice ID:</strong> {invoice_id}</p>
        <p>
            <a href="https://app.clarityap.com/invoices/{invoice_id}">
                View Invoice
            </a>
        </p>
    </body>
    </html>
    """

    return send_email_task.delay(user_email, subject, body)


@celery_app.task(name='app.tasks.notifications.send_invoice_rejected')
def send_invoice_rejected_task(user_email: str, invoice_id: str, rejector_name: str, notes: str = None):
    """
    Notify that invoice has been rejected

    Args:
        user_email: User to notify
        invoice_id: UUID of rejected invoice
        rejector_name: Name of person who rejected
        notes: Optional rejection notes
    """
    subject = "Invoice Rejected"

    notes_html = f"<p><strong>Notes:</strong> {notes}</p>" if notes else ""

    body = f"""
    <html>
    <body>
        <h2>Invoice Rejected</h2>
        <p>Your invoice has been rejected by {rejector_name}.</p>
        <p><strong>Invoice ID:</strong> {invoice_id}</p>
        {notes_html}
        <p>
            <a href="https://app.clarityap.com/invoices/{invoice_id}">
                View Invoice
            </a>
        </p>
    </body>
    </html>
    """

    return send_email_task.delay(user_email, subject, body)
