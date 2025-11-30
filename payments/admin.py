from django.contrib import admin
from .models import (
    Cart, CartItem, Order, OrderItem, Coupon, 
    Announcement, PaymentConfig, PaymentTransaction, Invoice
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
    
    def save_model(self, request, obj, form, change):
        """Override save to handle status changes and trigger email/invoice"""
        from django.db import transaction
        
        # Only for existing objects (change=True)
        should_process_approval = False
        should_process_rejection = False
        transaction_id = None
        
        if change:
            try:
                # Get the old instance from database
                old_obj = PaymentTransaction.objects.get(pk=obj.pk)
                old_status = old_obj.status
                new_status = obj.status
                transaction_id = obj.pk
                
                # Check if status changed
                if old_status != new_status:
                    if new_status == 'success' and obj.order.payment_status != 'completed':
                        should_process_approval = True
                    elif new_status == 'failed' and obj.order.payment_status != 'failed':
                        should_process_rejection = True
            except PaymentTransaction.DoesNotExist:
                pass
        
        # Save the model (within atomic transaction)
        super().save_model(request, obj, form, change)
        
        # Process approval/rejection in a NEW transaction after admin's atomic block completes
        # Use on_commit to ensure it runs after the admin transaction commits
        if should_process_approval:
            transaction.on_commit(
                lambda: self._process_payment_approval_async(request, transaction_id)
            )
        elif should_process_rejection:
            transaction.on_commit(
                lambda: self._process_payment_rejection_async(request, transaction_id)
            )
    
    def _process_payment_approval_async(self, request, transaction_id):
        """Async payment approval - runs after transaction commits"""
        from django.db import transaction as db_transaction
        
        # This runs in a completely new transaction, safe to do all queries
        with db_transaction.atomic():
            try:
                transaction_obj = PaymentTransaction.objects.get(pk=transaction_id)
                self._process_payment_approval(request, transaction_obj)
            except PaymentTransaction.DoesNotExist:
                print(f"❌ Transaction {transaction_id} not found")
    
    def _process_payment_rejection_async(self, request, transaction_id):
        """Async payment rejection - runs after transaction commits"""
        from django.db import transaction as db_transaction
        
        # This runs in a completely new transaction, safe to do all queries
        with db_transaction.atomic():
            try:
                transaction_obj = PaymentTransaction.objects.get(pk=transaction_id)
                self._process_payment_rejection(request, transaction_obj)
            except PaymentTransaction.DoesNotExist:
                print(f"❌ Transaction {transaction_id} not found")
    
    def _process_payment_approval(self, request, transaction):
        """Process payment approval - create enrollments, invoice, and send email"""
        from django.utils import timezone
        from .emails import send_payment_approved_email
        from enrollment.models import Enrollment
        import logging
        
        logger = logging.getLogger(__name__)
        
        order = transaction.order
        
        print(f"\n{'='*60}")
        print(f"🔍 DEBUG: Starting payment approval process")
        print(f"Order: {order.order_number}")
        print(f"User: {order.user.username} ({order.user.email})")
        print(f"{'='*60}\n")
        
        logger.info(f"Starting approval for order {order.order_number}")
        
        # Update order
        print(f"📝 Step 1: Updating order status...")
        order.payment_status = 'completed'
        order.verified_by = request.user
        order.verified_at = timezone.now()
        order.save()
        print(f"✅ Order status updated: {order.payment_status}")
        logger.info(f"Order {order.order_number} status updated to completed")
        
        # Create enrollments
        print(f"\n📝 Step 2: Creating enrollments...")
        for item in order.items.all():
            enrollment, created = Enrollment.objects.get_or_create(
                user=order.user,
                course=item.course
            )
            
            if created:
                item.course.total_enrollments += 1
                item.course.save()
                print(f"  ✅ New enrollment created: {item.course.title}")
                logger.info(f"Enrollment created for {order.user.username} in {item.course.title}")
            else:
                print(f"  ℹ️  Enrollment already exists: {item.course.title}")
                logger.info(f"Enrollment already exists for {order.user.username} in {item.course.title}")
        
        # Generate invoice if not exists
        print(f"\n📝 Step 3: Creating invoice...")
        if not hasattr(order, 'invoice'):
            try:
                invoice = Invoice.objects.create(
                    order=order,
                    invoice_number=Invoice.generate_invoice_number(),
                    subtotal=order.total_amount,
                    discount_amount=order.discount_amount,
                    tax_amount=0,
                    total_amount=order.final_amount,
                    notes=f"Payment verified by {request.user.get_full_name() or request.user.username}"
                )
                print(f"✅ Invoice created: {invoice.invoice_number}")
                logger.info(f"Invoice {invoice.invoice_number} created for order {order.order_number}")
            except Exception as e:
                print(f"❌ Error creating invoice: {str(e)}")
                logger.error(f"Error creating invoice for order {order.order_number}: {str(e)}")
        else:
            print(f"ℹ️  Invoice already exists")
            logger.info(f"Invoice already exists for order {order.order_number}")
        
        # Send email with invoice
        print(f"\n📝 Step 4: Sending email notification...")
        try:
            # Refresh order from database to get latest invoice
            order.refresh_from_db()
            
            print(f"📧 Email to: {order.user.email}")
            print(f"📧 User: {order.user.get_full_name() or order.user.username}")
            
            email_sent = send_payment_approved_email(order)
            
            if email_sent:
                print(f"✅ Email sent successfully!")
                logger.info(f"Email sent to {order.user.email} for order {order.order_number}")
            else:
                print(f"⚠️  Email sending returned False - check SMTP settings")
                logger.warning(f"Email sending returned False for order {order.order_number}")
                
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            print(f"Exception type: {type(e).__name__}")
            logger.error(f"Error sending email for order {order.order_number}: {str(e)}", exc_info=True)
        
        print(f"\n{'='*60}")
        print(f"✅ Payment approval process completed for {order.order_number}")
        print(f"{'='*60}\n")
    
    def _process_payment_rejection(self, request, transaction):
        """Process payment rejection - update order and send rejection email"""
        from django.utils import timezone
        from .emails import send_payment_rejected_email
        
        order = transaction.order
        
        # Update order
        order.payment_status = 'failed'
        order.verified_by = request.user
        order.verified_at = timezone.now()
        order.save()
        
        # Send rejection email
        send_payment_rejected_email(order, order.rejection_reason)
        
        print(f"✅ Payment rejection processed for order {order.order_number}")
        print(f"✅ Rejection email sent to {order.user.email}")
    
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
            
            # Only proceed if order was not already completed
            if order.payment_status != 'completed':
                order.payment_status = 'completed'
                order.verified_by = request.user
                order.verified_at = timezone.now()
                order.save()
                
                # Create enrollments and invoices
                from enrollment.models import Enrollment
                total_enrollment_increase = 0
                
                for item in order.items.all():
                    # Check if enrollment already exists
                    enrollment, created = Enrollment.objects.get_or_create(
                        user=order.user,
                        course=item.course
                    )
                    
                    # Only increment course enrollments if this is a new enrollment
                    if created:
                        item.course.total_enrollments += 1
                        item.course.save()
                        total_enrollment_increase += 1
                
                # Generate invoice if not already exists
                if not hasattr(order, 'invoice'):
                    Invoice.objects.create(
                        order=order,
                        invoice_number=Invoice.generate_invoice_number(),
                        subtotal=order.total_amount,
                        discount_amount=order.discount_amount,
                        tax_amount=0,  # Set tax if needed
                        total_amount=order.final_amount,
                        notes=f"Payment verified by {request.user.get_full_name() or request.user.username}"
                    )
                
                # Send approval email with invoice
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


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'get_order_user', 'total_amount', 'invoice_date', 'order__payment_status']
    list_filter = ['invoice_date', 'order__payment_status']
    search_fields = ['invoice_number', 'order__user__username', 'order__user__email', 'order__order_number']
    readonly_fields = ['invoice_number', 'invoice_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'order', 'invoice_date', 'due_date')
        }),
        ('Amount Details', {
            'fields': ('subtotal', 'discount_amount', 'tax_amount', 'total_amount')
        }),
        ('Additional Info', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_order_user(self, obj):
        """Display the user who made the order"""
        return obj.order.user.username
    get_order_user.short_description = 'User'
    get_order_user.admin_order_field = 'order__user__username'