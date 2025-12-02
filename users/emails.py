from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_2fa_verification_email(user, verification_code):
    """Send 2FA verification code to user email"""
    
    subject = '🔐 Your Two-Factor Authentication Code'
    
    full_name = user.get_full_name() or user.username
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🔐 Verification Code</h1>
            </div>
            
            <!-- Main Content -->
            <div style="background-color: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; margin-top: 0;">Hi <strong>{full_name}</strong>,</p>
                
                <p>You requested a two-factor authentication code for your CodeLearn account. Use this code to complete your 2FA setup:</p>
                
                <!-- Code Display Section -->
                <div style="background-color: #fff3cd; padding: 25px; border-radius: 8px; margin: 30px 0; border-left: 5px solid #ff9800; text-align: center;">
                    <h2 style="color: #856404; margin-top: 0;">Your Verification Code</h2>
                    <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 15px 0;">
                        <p style="font-size: 14px; margin: 0 0 10px 0; color: #666;">Enter this code within <strong>10 minutes</strong>:</p>
                        <p style="font-size: 36px; font-weight: bold; color: #ff6b6b; letter-spacing: 3px; margin: 15px 0; font-family: 'Courier New', monospace;">
                            {verification_code}
                        </p>
                        <p style="font-size: 12px; color: #999; margin: 10px 0 0 0;">This code will expire in 10 minutes</p>
                    </div>
                </div>
                
                <!-- Security Notice -->
                <div style="background-color: #e3f2fd; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 5px solid #2196F3;">
                    <h3 style="margin-top: 0; color: #1976D2;">🔒 Security Notice</h3>
                    <ul style="margin: 10px 0; padding-left: 20px; color: #555;">
                        <li style="margin: 8px 0;">Never share this code with anyone</li>
                        <li style="margin: 8px 0;">CodeLearn staff will never ask for this code</li>
                        <li style="margin: 8px 0;">If you did not request this code, please ignore this email</li>
                    </ul>
                </div>
                
                <!-- Instructions -->
                <div style="background-color: #f1f8e9; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin-top: 0; color: #33691e;">📝 Next Steps</h3>
                    <ol style="margin: 10px 0; padding-left: 20px; color: #555;">
                        <li style="margin: 8px 0;">Return to the CodeLearn website</li>
                        <li style="margin: 8px 0;">Enter the code above in the verification field</li>
                        <li style="margin: 8px 0;">Complete your 2FA setup</li>
                    </ol>
                </div>
                
                <!-- Support Section -->
                <div style="background-color: #fff3e0; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 5px solid #ff9800;">
                    <h3 style="margin-top: 0; color: #e65100;">📞 Need Help?</h3>
                    <p style="margin: 10px 0;">If you're experiencing issues, please contact our support team at <strong>support@codelearn.com</strong></p>
                </div>
                
                <!-- Closing -->
                <p style="margin-top: 30px; color: #666;">Best Regards,<br><strong>The CodeLearn Security Team</strong></p>
                
                <!-- Footer -->
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center; margin: 15px 0;">
                    This is an automated security email. Please do not reply directly to this email.<br>
                    © 2025 CodeLearn. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    print(f"\n{'='*60}")
    print(f"🔐 2FA VERIFICATION EMAIL: Starting email composition")
    print(f"User: {user.username}")
    print(f"Email: {user.email}")
    print(f"Verification Code: {verification_code}")
    print(f"{'='*60}\n")
    
    print(f"📝 Email Configuration:")
    print(f"  FROM: {settings.DEFAULT_FROM_EMAIL}")
    print(f"  TO: {user.email}")
    print(f"  SUBJECT: {subject}")
    
    try:
        print(f"\n📤 Attempting to send 2FA verification email...")
        print(f"  Backend: {settings.EMAIL_BACKEND}")
        print(f"  SSL: {settings.EMAIL_USE_SSL}, TLS: {settings.EMAIL_USE_TLS}")
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"✅ 2FA verification email sent successfully!")
        logger.info(f"2FA verification email sent successfully to {user.email} for user {user.username}")
        return True
    except Exception as e:
        print(f"\n❌ 2FA verification email sending failed!")
        print(f"Exception Type: {type(e).__name__}")
        print(f"Exception Message: {str(e)}")
        print(f"Full Error: {repr(e)}")
        logger.error(f"2FA verification email sending failed for {user.email}: {str(e)}", exc_info=True)
        return False


def send_welcome_email(user):
    """Send welcome email to new user after successful registration"""
    
    subject = 'Welcome to CodeLearn! 🎉'
    
    full_name = user.get_full_name() or user.username
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to CodeLearn!</h1>
            </div>
            
            <!-- Main Content -->
            <div style="background-color: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; margin-top: 0;">Hi <strong>{full_name}</strong>,</p>
                
                <p>Welcome aboard! 🚀 We're thrilled to have you join our learning community. Your account has been successfully created, and you're all set to start your learning journey.</p>
                
                <!-- Getting Started Section -->
                <div style="background-color: #e3f2fd; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 5px solid #2196F3;">
                    <h2 style="margin-top: 0; color: #1976D2;">🎯 Getting Started</h2>
                    
                    <div style="margin: 15px 0;">
                        <h3 style="margin: 10px 0 5px 0; color: #333;">Account Information</h3>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li style="margin: 8px 0;"><strong>Username:</strong> {user.username}</li>
                            <li style="margin: 8px 0;"><strong>Email:</strong> {user.email}</li>
                        </ul>
                    </div>
                    
                    <p style="margin: 15px 0; color: #555;">You can now browse and enroll in courses to expand your skills and knowledge.</p>
                </div>
                
                <!-- Quick Links Section -->
                <div style="background-color: #f0f4ff; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h2 style="margin-top: 0; color: #333;">📚 What You Can Do Now</h2>
                    
                    <div style="margin: 15px 0;">
                        <h3 style="font-size: 14px; margin: 12px 0 8px 0; color: #333;">✓ Browse Courses</h3>
                        <p style="margin: 0; color: #666;">Explore our wide range of coding and development courses tailored for all skill levels.</p>
                    </div>
                    
                    <div style="margin: 15px 0;">
                        <h3 style="font-size: 14px; margin: 12px 0 8px 0; color: #333;">✓ Complete Your Profile</h3>
                        <p style="margin: 0; color: #666;">Add a profile picture and bio to personalize your learning experience.</p>
                    </div>
                    
                    <div style="margin: 15px 0;">
                        <h3 style="font-size: 14px; margin: 12px 0 8px 0; color: #333;">✓ Join Our Community</h3>
                        <p style="margin: 0; color: #666;">Connect with other learners and instructors to share knowledge and insights.</p>
                    </div>
                </div>
                
                <!-- CTA Buttons -->
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/courses/" 
                       style="background-color: #667eea; color: white; padding: 12px 35px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 0 10px 10px 0; font-weight: bold;">
                        Browse Courses
                    </a>
                    
                    <a href="{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/users/profile/" 
                       style="background-color: #764ba2; color: white; padding: 12px 35px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 0 10px 10px 0; font-weight: bold;">
                        Complete Profile
                    </a>
                </div>
                
                <!-- Support Section -->
                <div style="background-color: #fff3e0; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 5px solid #ff9800;">
                    <h3 style="margin-top: 0; color: #e65100;">📞 Need Help?</h3>
                    <p style="margin: 10px 0;">If you have any questions or encounter any issues, our support team is here to help. Feel free to contact us at <strong>support@codelearn.com</strong></p>
                </div>
                
                <!-- Best Practices -->
                <div style="background-color: #f1f8e9; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin-top: 0; color: #33691e;">💡 Pro Tips for Your Learning Journey</h3>
                    <ul style="margin: 10px 0; padding-left: 20px; color: #555;">
                        <li style="margin: 8px 0;">Set realistic learning goals and stick to a consistent schedule</li>
                        <li style="margin: 8px 0;">Take advantage of practice exercises to reinforce your learning</li>
                        <li style="margin: 8px 0;">Engage with course materials at your own pace</li>
                        <li style="margin: 8px 0;">Review course material regularly to maintain progress</li>
                    </ul>
                </div>
                
                <!-- Closing -->
                <p style="margin-top: 30px; color: #666;">We're excited to be part of your learning journey. Start exploring our courses today and unlock your potential!</p>
                
                <p style="margin: 20px 0;">Best Regards,<br><strong>The CodeLearn Team</strong></p>
                
                <!-- Footer -->
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center; margin: 15px 0;">
                    This is an automated welcome email. Please do not reply directly to this email.<br>
                    © 2025 CodeLearn. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    print(f"\n{'='*60}")
    print(f"📧 WELCOME EMAIL: Starting email composition")
    print(f"User: {user.username}")
    print(f"Email: {user.email}")
    print(f"{'='*60}\n")
    
    print(f"📝 Email Configuration:")
    print(f"  FROM: {settings.DEFAULT_FROM_EMAIL}")
    print(f"  TO: {user.email}")
    print(f"  SUBJECT: {subject}")
    
    try:
        print(f"\n📤 Attempting to send welcome email...")
        print(f"  Backend: {settings.EMAIL_BACKEND}")
        print(f"  SSL: {settings.EMAIL_USE_SSL}, TLS: {settings.EMAIL_USE_TLS}")
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"✅ Welcome email sent successfully!")
        logger.info(f"Welcome email sent successfully to {user.email} for user {user.username}")
        return True
    except Exception as e:
        print(f"\n❌ Welcome email sending failed!")
        print(f"Exception Type: {type(e).__name__}")
        print(f"Exception Message: {str(e)}")
        print(f"Full Error: {repr(e)}")
        logger.error(f"Welcome email sending failed for {user.email}: {str(e)}", exc_info=True)
        return False
