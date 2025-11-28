from django.contrib import admin
from .models import Enrollment, LectureProgress, Wishlist, Certificate

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