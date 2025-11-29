from django.contrib import admin
from .models import Enrollment, LectureProgress, Wishlist, Certificate, DailyClass

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at', 'progress_percentage', 'is_completed']
    list_filter = ['is_completed', 'enrolled_at']
    search_fields = ['user__username', 'course__title']

@admin.register(LectureProgress)
class LectureProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lecture', 'is_completed']
    list_filter = ['is_completed']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'added_at']
    search_fields = ['user__username', 'course__title']

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'certificate_number', 'issued_date']
    search_fields = ['user__username', 'course__title', 'certificate_number']

@admin.register(DailyClass)
class DailyClassAdmin(admin.ModelAdmin):
    list_display = ['date', 'scheduled_time', 'title', 'course', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'date', 'course', 'created_by']
    search_fields = ['title', 'description', 'course__title']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Class Information', {
            'fields': ('title', 'description', 'course')
        }),
        ('Schedule', {
            'fields': ('date', 'scheduled_time', 'duration_minutes')
        }),
        ('Meeting Details', {
            'fields': ('meet_link',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Automatically set created_by to current admin user"""
        if not change:  # Only on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)