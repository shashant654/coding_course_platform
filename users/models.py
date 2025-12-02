from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import random
import string
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_instructor = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)  # NEW FIELD
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'users'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    profession = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    class Meta:
        db_table = 'user_profiles'


class TwoFactorAuth(models.Model):
    """Store 2FA verification codes and status"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor')
    verification_code = models.CharField(max_length=6)
    code_created_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    failed_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'two_factor_auth'
    
    def __str__(self):
        return f"{self.user.username} - 2FA"
    
    @staticmethod
    def generate_code():
        """Generate a random 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def create_new_code(self):
        """Create a new verification code"""
        self.verification_code = self.generate_code()
        self.code_created_at = timezone.now()
        self.is_verified = False
        self.save()
        return self.verification_code
    
    def is_code_valid(self):
        """Check if code is still valid (10 minutes expiry)"""
        expiry_time = self.code_created_at + timedelta(minutes=10)
        return timezone.now() < expiry_time
    
    def verify_code(self, entered_code):
        """Verify the entered code"""
        # Check if account is locked
        if self.locked_until and timezone.now() < self.locked_until:
            remaining_time = (self.locked_until - timezone.now()).seconds // 60
            return False, f"Account locked. Try again in {remaining_time} minutes."
        
        # Check if code is expired
        if not self.is_code_valid():
            return False, "Verification code has expired. Please request a new one."
        
        # Verify code
        if self.verification_code == entered_code:
            self.is_verified = True
            self.failed_attempts = 0
            self.locked_until = None
            self.save()
            return True, "Verification successful!"
        else:
            self.failed_attempts += 1
            
            # Lock account after 5 failed attempts
            if self.failed_attempts >= 5:
                self.locked_until = timezone.now() + timedelta(minutes=30)
                self.save()
                return False, "Too many failed attempts. Account locked for 30 minutes."
            
            self.save()
            remaining_attempts = 5 - self.failed_attempts
            return False, f"Invalid code. {remaining_attempts} attempts remaining."