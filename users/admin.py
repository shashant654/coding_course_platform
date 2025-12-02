from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, TwoFactorAuth

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_instructor', 'two_factor_enabled', 'is_staff']
    list_filter = ['is_instructor', 'two_factor_enabled', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'profile_picture', 'is_instructor', 'two_factor_enabled')}),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profession', 'created_at']
    search_fields = ['user__username', 'profession']


@admin.register(TwoFactorAuth)
class TwoFactorAuthAdmin(admin.ModelAdmin):
    list_display = ['user', 'verification_code', 'code_created_at', 'is_verified', 'failed_attempts', 'locked_until']
    list_filter = ['is_verified', 'code_created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['verification_code', 'code_created_at', 'is_verified', 'failed_attempts']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Verification Details', {
            'fields': ('verification_code', 'code_created_at', 'is_verified')
        }),
        ('Security', {
            'fields': ('failed_attempts', 'locked_until')
        }),
    )
    
    def has_add_permission(self, request):
        # Don't allow manual creation - should be auto-created
        return False