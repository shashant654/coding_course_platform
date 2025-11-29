from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_payment_approved_email(order):
    """Send email notification when payment is approved"""
    subject = f'Payment Approved - {order.order_number}'
    
    # Get course names
    course_names = [item.course.title for item in order.items.all()]
    
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
            </div>
            
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Enrolled Courses</h3>
                <ul>
                    {''.join([f'<li>{course}</li>' for course in course_names])}
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
                If you have any questions, please contact our support team.<br>
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
                <ul>
                    <li>Check if your payment was actually deducted from your account</li>
                    <li>Keep your payment screenshot/transaction ID ready</li>
                    <li>Contact support with your order number: <strong>{order.order_number}</strong></li>
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
