from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_payment_approved_email(order):
    """Send email notification when payment is approved with invoice details"""
    import logging
    logger = logging.getLogger(__name__)
    
    subject = f'Payment Approved - {order.order_number}'
    
    print(f"\n{'='*60}")
    print(f"📧 EMAIL DEBUG: Starting email composition")
    print(f"Order: {order.order_number}")
    print(f"User Email: {order.user.email}")
    print(f"{'='*60}\n")
    
    logger.info(f"Starting email composition for order {order.order_number}")
    
    # Get course names
    course_names = [item.course.title for item in order.items.all()]
    print(f"📚 Courses: {course_names}")
    
    # Get or create invoice
    invoice = None
    if hasattr(order, 'invoice'):
        invoice = order.invoice
        print(f"📄 Invoice found: {invoice.invoice_number}")
        logger.info(f"Invoice {invoice.invoice_number} found for order {order.order_number}")
    else:
        print(f"⚠️  No invoice found for order {order.order_number}")
        logger.warning(f"No invoice found for order {order.order_number}")
    
    # Build invoice section
    invoice_html = ""
    if invoice:
        item_rows = ""
        for idx, item in enumerate(order.items.all(), 1):
            item_rows += f"""
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; text-align: left;">{idx}. {item.course.title}</td>
                <td style="padding: 10px; text-align: right;">₹{item.price}</td>
            </tr>
            """
        
        invoice_html = f"""
        <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; border-bottom: 2px solid #4CAF50; padding-bottom: 10px;">Invoice Details</h3>
            
            <div style="margin-bottom: 20px;">
                <p><strong>Invoice Number:</strong> {invoice.invoice_number}</p>
                <p><strong>Invoice Date:</strong> {invoice.invoice_date.strftime('%d %B %Y')}</p>
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
                <thead>
                    <tr style="background-color: #f0f0f0; border-bottom: 2px solid #ddd;">
                        <th style="padding: 10px; text-align: left; font-weight: bold;">Course</th>
                        <th style="padding: 10px; text-align: right; font-weight: bold;">Price</th>
                    </tr>
                </thead>
                <tbody>
                    {item_rows}
                </tbody>
            </table>
            
            <div style="background-color: #e8f5e9; padding: 15px; border-radius: 3px; text-align: right;">
                <p style="margin: 5px 0;"><strong>Subtotal:</strong> ₹{invoice.subtotal}</p>
                {f'<p style="margin: 5px 0; color: #4CAF50;"><strong>Discount:</strong> -₹{invoice.discount_amount}</p>' if invoice.discount_amount > 0 else ''}
                {f'<p style="margin: 5px 0;"><strong>Tax:</strong> ₹{invoice.tax_amount}</p>' if invoice.tax_amount > 0 else ''}
                <p style="margin: 10px 0; font-size: 16px; border-top: 2px solid #4CAF50; padding-top: 10px;">
                    <strong>Total Amount Paid:</strong> ₹{invoice.total_amount}
                </p>
            </div>
        </div>
        """
    else:
        print(f"⚠️  Skipping invoice section - no invoice available")
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4CAF50;">Payment Approved! 🎉</h2>
            
            <p>Dear {order.user.get_full_name() or order.user.username},</p>
            
            <p>Great news! Your payment has been verified and approved.</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Order Details</h3>
                <p><strong>Order Number:</strong> {order.order_number}</p>
                <p><strong>Amount Paid:</strong> ₹{order.final_amount}</p>
                <p><strong>Payment Status:</strong> <span style="color: #4CAF50;">Completed</span></p>
                <p><strong>Payment Method:</strong> {order.payment_method.upper() if order.payment_method else 'N/A'}</p>
            </div>
            
            {invoice_html}
            
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Enrolled Courses</h3>
                <ul style="margin: 10px 0; padding-left: 20px;">
                    {''.join([f'<li style="margin: 8px 0;">{course}</li>' for course in course_names])}
                </ul>
            </div>
            
            <p>You can now access your enrolled courses from your learning dashboard.</p>
            
            <div style="margin: 30px 0;">
                <a href="{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/enrollment/my-learning/" 
                   style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Go to My Learning
                </a>
            </div>
            
            <p>Happy Learning!</p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            
            <p style="font-size: 12px; color: #666;">
                <strong>Invoice Details:</strong> Please keep this email for your records. Your invoice has been generated and can be downloaded from your order history.<br>
                If you have any questions, please contact our support team.<br>
                This is an automated email, please do not reply directly.
            </p>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    print(f"\n📝 Email Configuration:")
    print(f"  FROM: {settings.DEFAULT_FROM_EMAIL}")
    print(f"  TO: {order.user.email}")
    print(f"  SUBJECT: {subject}")
    print(f"  HOST: {settings.EMAIL_HOST}")
    print(f"  PORT: {settings.EMAIL_PORT}")
    print(f"  USE_SSL: {settings.EMAIL_USE_SSL}")
    print(f"  USE_TLS: {settings.EMAIL_USE_TLS}")
    
    try:
        print(f"\n📤 Attempting to send email...")
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"✅ Email sent successfully!")
        logger.info(f"Email sent successfully to {order.user.email} for order {order.order_number}")
        return True
    except Exception as e:
        print(f"❌ Email sending failed!")
        print(f"Exception Type: {type(e).__name__}")
        print(f"Exception Message: {str(e)}")
        print(f"Full Error: {repr(e)}")
        logger.error(f"Email sending failed for {order.user.email}: {str(e)}", exc_info=True)
        return False


def send_payment_rejected_email(order, reason=""):
    """Send email notification when payment is rejected"""
    subject = f'Payment Verification Issue - {order.order_number}'
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #f44336;">Payment Verification Issue</h2>
            
            <p>Dear {order.user.get_full_name() or order.user.username},</p>
            
            <p>We were unable to verify your payment for the following order:</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Order Details</h3>
                <p><strong>Order Number:</strong> {order.order_number}</p>
                <p><strong>Amount:</strong> ₹{order.final_amount}</p>
                <p><strong>Status:</strong> <span style="color: #f44336;">Verification Failed</span></p>
            </div>
            
            {f'''
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <h3 style="margin-top: 0;">Reason</h3>
                <p>{reason}</p>
            </div>
            ''' if reason else ''}
            
            <p>Please contact our support team with your order number and payment details for assistance.</p>
            
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0;">What to do next?</h3>
                <ul style="margin: 10px 0; padding-left: 20px;">
                    <li style="margin: 8px 0;">Check if your payment was actually deducted from your account</li>
                    <li style="margin: 8px 0;">Keep your payment screenshot/transaction ID ready</li>
                    <li style="margin: 8px 0;">Contact support with your order number: <strong>{order.order_number}</strong></li>
                </ul>
            </div>
            
            <div style="margin: 30px 0;">
                <a href="mailto:support@codelearn.com" 
                   style="background-color: #2196F3; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Contact Support
                </a>
            </div>
            
            <p>We apologize for any inconvenience.</p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            
            <p style="font-size: 12px; color: #666;">
                Support Email: support@codelearn.com<br>
                This is an automated email, please do not reply directly.
            </p>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def create_invoice_for_order(order):
    """Create an invoice for an order"""
    from .models import Invoice
    
    # Check if invoice already exists
    if hasattr(order, 'invoice'):
        return order.invoice
    
    # Create new invoice
    invoice = Invoice.objects.create(
        order=order,
        invoice_number=Invoice.generate_invoice_number(),
        subtotal=order.total_amount,
        discount_amount=order.discount_amount,
        tax_amount=0,  # Set tax if applicable
        total_amount=order.final_amount,
        notes="Payment verified and invoice generated"
    )
    
    return invoice