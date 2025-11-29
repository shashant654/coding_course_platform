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

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'final_amount', 'payment_status', 'payment_method', 'created_at']
    list_filter = ['payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__username', 'transaction_id']
    readonly_fields = ['order_number', 'created_at', 'updated_at']

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
        'order', 
        'payment_method', 
        'amount', 
        'status', 
        'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = [
        'transaction_id', 
        'razorpay_order_id', 
        'razorpay_payment_id',
        'upi_transaction_ref'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('order', 'transaction_id', 'payment_method', 'amount', 'status')
        }),
        ('Razorpay Details', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'),
            'classes': ('collapse',)
        }),
        ('UPI Details', {
            'fields': ('upi_transaction_ref', 'payment_screenshot'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_payment', 'reject_payment']
    
    def approve_payment(self, request, queryset):
        """Approve pending UPI payments"""
        for transaction in queryset.filter(status='pending'):
            transaction.status = 'success'
            transaction.save()
            
            # Update order
            order = transaction.order
            order.payment_status = 'completed'
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
        
        self.message_user(request, f'{queryset.count()} payment(s) approved successfully.')
    approve_payment.short_description = 'Approve selected payments'
    
    def reject_payment(self, request, queryset):
        """Reject pending payments"""
        queryset.update(status='failed')
        self.message_user(request, f'{queryset.count()} payment(s) rejected.')
    reject_payment.short_description = 'Reject selected payments'