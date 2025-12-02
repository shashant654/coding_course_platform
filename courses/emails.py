from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_callback_request_email(callback_request):
    """Send admin notification email for callback request"""
    
    subject = f'🔔 New Callback Request - {callback_request.course.title}'
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px;">📞 New Callback Request</h1>
            </div>
            
            <!-- Main Content -->
            <div style="background-color: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; margin-top: 0;">Hello Admin,</p>
                
                <p>A new callback request has been submitted on your CodeLearn platform. Here are the details:</p>
                
                <!-- Request Details Section -->
                <div style="background-color: #e3f2fd; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 5px solid #2196F3;">
                    <h2 style="margin-top: 0; color: #1976D2;">📋 Requester Information</h2>
                    
                    <table style="width: 100%; margin: 15px 0;">
                        <tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 10px 0; font-weight: bold; width: 30%; color: #555;">Name:</td>
                            <td style="padding: 10px 0; color: #333;">{callback_request.name}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 10px 0; font-weight: bold; color: #555;">Email:</td>
                            <td style="padding: 10px 0; color: #333;">{callback_request.email}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 10px 0; font-weight: bold; color: #555;">Phone:</td>
                            <td style="padding: 10px 0; color: #333;">{callback_request.phone}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; font-weight: bold; color: #555;">Requested Date:</td>
                            <td style="padding: 10px 0; color: #333;">{callback_request.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
                        </tr>
                    </table>
                </div>
                
                <!-- Course Details Section -->
                <div style="background-color: #f1f8e9; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 5px solid #4CAF50;">
                    <h2 style="margin-top: 0; color: #33691e;">📚 Course Information</h2>
                    
                    <table style="width: 100%; margin: 15px 0;">
                        <tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 10px 0; font-weight: bold; width: 30%; color: #555;">Course:</td>
                            <td style="padding: 10px 0; color: #333;">{callback_request.course.title}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 10px 0; font-weight: bold; color: #555;">Instructor:</td>
                            <td style="padding: 10px 0; color: #333;">{callback_request.course.instructor.get_full_name() or callback_request.course.instructor.username}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; font-weight: bold; color: #555;">Price:</td>
                            <td style="padding: 10px 0; color: #333;">₹{callback_request.course.price}</td>
                        </tr>
                    </table>
                </div>
                
                <!-- Action Section -->
                <div style="background-color: #fff3e0; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 5px solid #ff9800;">
                    <h3 style="margin-top: 0; color: #e65100;">📌 Action Required</h3>
                    <p style="margin: 10px 0; color: #555;">
                        This callback request needs to be addressed. Please contact the person within 24 hours.
                    </p>
                    <p style="margin: 10px 0; color: #555;">
                        <strong>Status:</strong> <span style="background-color: #FFC107; padding: 4px 12px; border-radius: 4px; font-weight: bold;">Pending</span>
                    </p>
                </div>
                
                <!-- Admin Panel Link -->
                <div style="text-align: center; margin: 30px 0;">
                    <p style="margin: 10px 0; font-size: 14px; color: #666;">
                        You can manage this request in the admin panel:
                    </p>
                    <a href="{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/admin/courses/callbackrequest/" 
                       style="background-color: #667eea; color: white; padding: 12px 35px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 10px 0; font-weight: bold;">
                        View in Admin Panel
                    </a>
                </div>
                
                <!-- Support Section -->
                <div style="background-color: #f0f4ff; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin-top: 0; color: #333;">💡 Quick Tips</h3>
                    <ul style="margin: 10px 0; padding-left: 20px; color: #555;">
                        <li style="margin: 8px 0;">Update the status to 'Contacted' after reaching out</li>
                        <li style="margin: 8px 0;">Mark as 'Completed' once the callback is done</li>
                        <li style="margin: 8px 0;">Add notes about the interaction for future reference</li>
                    </ul>
                </div>
                
                <!-- Closing -->
                <p style="margin-top: 30px; color: #666;">Best Regards,<br><strong>CodeLearn System</strong></p>
                
                <!-- Footer -->
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center; margin: 15px 0;">
                    This is an automated notification email from CodeLearn Platform.<br>
                    © 2025 CodeLearn. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    print(f"\n{'='*60}")
    print(f"📞 CALLBACK REQUEST EMAIL: Starting email composition")
    print(f"Requester: {callback_request.name}")
    print(f"Email: {callback_request.email}")
    print(f"Phone: {callback_request.phone}")
    print(f"Course: {callback_request.course.title}")
    print(f"{'='*60}\n")
    
    print(f"📝 Email Configuration:")
    print(f"  FROM: {settings.DEFAULT_FROM_EMAIL}")
    print(f"  TO: {settings.DEFAULT_FROM_EMAIL}")
    print(f"  SUBJECT: {subject}")
    
    try:
        print(f"\n📤 Attempting to send callback notification email...")
        print(f"  Backend: {settings.EMAIL_BACKEND}")
        print(f"  SSL: {settings.EMAIL_USE_SSL}, TLS: {settings.EMAIL_USE_TLS}")
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],  # Send to admin email
            html_message=html_message,
            fail_silently=False,
        )
        print(f"✅ Callback notification email sent successfully!")
        logger.info(f"Callback notification email sent successfully for {callback_request.name}")
        return True
    except Exception as e:
        print(f"\n❌ Callback notification email sending failed!")
        print(f"Exception Type: {type(e).__name__}")
        print(f"Exception Message: {str(e)}")
        print(f"Full Error: {repr(e)}")
        logger.error(f"Callback notification email sending failed: {str(e)}", exc_info=True)
        return False
