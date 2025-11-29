from django.contrib import admin
from .models import (
    Cart, CartItem, Order, OrderItem, Coupon, 
    Announcement, PaymentConfig, PaymentTransaction
)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'course', 'added_at']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['course', 'price']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'final_amount', 'payment_status', 'payment_method', 'verified_by', 'created_at']
    list_filter = ['payment_status', 'payment_method', 'verified_by', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'transaction_id']
    readonly_fields = ['order_number', 'verified_by', 'verified_at', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'payment_status')
        }),
        ('Payment Details', {
            'fields': ('total_amount', 'discount_amount', 'final_amount', 'payment_method', 'transaction_id', 'razorpay_payment_id', 'razorpay_order_id')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verified_at', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'course', 'price']

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'is_active', 'used_count', 'usage_limit']
    list_filter = ['discount_type', 'is_active']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['course', 'instructor', 'title', 'created_at']
    search_fields = ['course__title', 'title']

@admin.register(PaymentConfig)
class PaymentConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'upi_id', 'is_razorpay_test_mode', 'updated_at']
    
    fieldsets = (
        ('UPI Configuration', {
            'fields': ('upi_qr_code', 'upi_id')
        }),
        ('Razorpay Configuration', {
            'fields': ('razorpay_key_id', 'razorpay_key_secret', 'is_razorpay_test_mode')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one config instance
        return not PaymentConfig.objects.exists()

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id',
        'get_order_user',
        'order', 
        'payment_method', 
        'amount', 
        'status',
        'screenshot_thumbnail',
        'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = [
        'transaction_id', 
        'razorpay_order_id', 
        'razorpay_payment_id',
        'upi_transaction_ref',
        'order__user__username',
        'order__user__email'
    ]
    readonly_fields = ['created_at', 'updated_at', 'screenshot_preview']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('order', 'transaction_id', 'payment_method', 'amount', 'status')
        }),
        ('Razorpay Details', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'),
            'classes': ('collapse',)
        }),
        ('UPI Details', {
            'fields': ('upi_transaction_ref', 'payment_screenshot', 'screenshot_preview'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_payment', 'reject_payment']
    
    def get_order_user(self, obj):
        """Display the user who made the order"""
        return obj.order.user.username
    get_order_user.short_description = 'User'
    get_order_user.admin_order_field = 'order__user__username'
    
    def screenshot_thumbnail(self, obj):
        """Display thumbnail of payment screenshot in list view"""
        if obj.payment_screenshot:
            from django.utils.html import format_html
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" width="50" height="50" style="object-fit: cover;" /></a>',
                obj.payment_screenshot.url,
                obj.payment_screenshot.url
            )
        return '-'
    screenshot_thumbnail.short_description = 'Screenshot'
    
    def screenshot_preview(self, obj):
        """Display full-size payment screenshot in detail view"""
        if obj.payment_screenshot:
            from django.utils.html import format_html
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width: 500px; max-height: 500px;" /></a>',
                obj.payment_screenshot.url,
                obj.payment_screenshot.url
            )
        return 'No screenshot uploaded'
    screenshot_preview.short_description = 'Payment Screenshot'
    
    def approve_payment(self, request, queryset):
        """Approve pending UPI payments"""
        from django.utils import timezone
        from .emails import send_payment_approved_email
        
        approved_count = 0
        for transaction in queryset.filter(status='pending'):
            transaction.status = 'success'
            transaction.save()
            
            # Update order
            order = transaction.order
            order.payment_status = 'completed'
            order.verified_by = request.user
            order.verified_at = timezone.now()
            order.save()
            
            # Complete enrollment
            from enrollment.models import Enrollment
            for item in order.items.all():
                Enrollment.objects.get_or_create(
                    user=order.user,
                    course=item.course
                )
                # Update course stats
                item.course.total_enrollments += 1
                item.course.save()
            
            # Send approval email
            send_payment_approved_email(order)
            approved_count += 1
        
        self.message_user(request, f'{approved_count} payment(s) approved successfully. Notification emails sent.')
    approve_payment.short_description = 'Approve selected payments'
    
    def reject_payment(self, request, queryset):
        """Reject pending payments"""
        from django.utils import timezone
        from .emails import send_payment_rejected_email
        
        rejected_count = 0
        for transaction in queryset.filter(status='pending'):
            transaction.status = 'failed'
            transaction.save()
            
            # Update order
            order = transaction.order
            order.payment_status = 'failed'
            order.verified_by = request.user
            order.verified_at = timezone.now()
            # You can add a rejection reason interface here if needed
            order.save()
            
            # Send rejection email
            send_payment_rejected_email(order, order.rejection_reason)
            rejected_count += 1
        
        self.message_user(request, f'{rejected_count} payment(s) rejected. Notification emails sent.')
    reject_payment.short_description = 'Reject selected payments'