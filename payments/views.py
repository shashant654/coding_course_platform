from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_POST
from decimal import Decimal
import json
from .models import Cart, CartItem, Order, OrderItem, Coupon
from courses.models import Course
from enrollment.models import Enrollment

try:
    import razorpay
except ImportError:
    razorpay = None


@login_required
def view_cart(request):
    """Display shopping cart"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('course', 'course__instructor')
    
    # Calculate totals
    subtotal = cart.get_total()
    discount = Decimal('0.00')
    
    # Check for applied coupon in session
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid():
                if coupon.discount_type == 'percentage':
                    discount = subtotal * (coupon.discount_value / 100)
                else:
                    discount = coupon.discount_value
        except Coupon.DoesNotExist:
            del request.session['coupon_code']
    
    total = subtotal - discount
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
        'coupon_code': coupon_code,
    }
    return render(request, 'payments/cart.html', context)


@login_required
def add_to_cart(request, course_id):
    """Add course to cart"""
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    # Check if already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('courses:course_detail', slug=course.slug)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if already in cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, course=course)
    
    if created:
        messages.success(request, f'{course.title} added to cart.')
    else:
        messages.info(request, f'{course.title} is already in your cart.')
    
    return redirect('payments:cart')


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    course_title = cart_item.course.title
    cart_item.delete()
    
    messages.success(request, f'{course_title} removed from cart.')
    return redirect('payments:cart')


@login_required
def clear_cart(request):
    """Clear all items from cart"""
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        cart.items.all().delete()
        messages.success(request, 'Cart cleared successfully.')
    
    return redirect('payments:cart')


@login_required
def checkout(request):
    """Checkout page"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.select_related('course')
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('payments:cart')
    
    # Calculate totals
    subtotal = cart.get_total()
    discount = Decimal('0.00')
    coupon = None
    
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid():
                if coupon.discount_type == 'percentage':
                    discount = subtotal * (coupon.discount_value / 100)
                else:
                    discount = coupon.discount_value
        except Coupon.DoesNotExist:
            pass
    
    total = subtotal - discount
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
        'coupon': coupon,
    }
    return render(request, 'payments/checkout.html', context)


@login_required
@transaction.atomic
def process_payment(request):
    """Process payment and create order"""
    if request.method != 'POST':
        return redirect('payments:checkout')
    
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.select_related('course')
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('payments:cart')
    
    # Calculate totals
    subtotal = cart.get_total()
    discount = Decimal('0.00')
    coupon = None
    
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid():
                if coupon.discount_type == 'percentage':
                    discount = subtotal * (coupon.discount_value / 100)
                else:
                    discount = coupon.discount_value
        except Coupon.DoesNotExist:
            pass
    
    final_amount = subtotal - discount
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        total_amount=subtotal,
        discount_amount=discount,
        final_amount=final_amount,
        payment_method='card',  # This should come from payment gateway
        payment_status='completed'  # In real app, this depends on payment gateway
    )
    
    # Create order items and enrollments
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            course=item.course,
            price=item.course.get_actual_price()
        )
        
        # Create enrollment
        Enrollment.objects.create(
            user=request.user,
            course=item.course
        )
        
        # Update course enrollment count
        item.course.total_enrollments += 1
        item.course.save()
    
    # Update coupon usage
    if coupon:
        coupon.used_count += 1
        coupon.save()
        del request.session['coupon_code']
    
    # Clear cart
    cart.items.all().delete()
    
    messages.success(request, 'Payment successful! You can now access your courses.')
    return redirect('payments:payment_success', order_number=order.order_number)


@login_required
def payment_success(request, order_number):
    """Payment success page - handles both completed and pending payments"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = order.items.select_related('course')
    
    # Get payment transaction if exists (for UPI payments)
    payment_txn = None
    if order.payment_method == 'upi':
        from .models import PaymentTransaction
        payment_txn = PaymentTransaction.objects.filter(order=order).first()
    
    context = {
        'order': order,
        'order_items': order_items,
        'payment_txn': payment_txn,
    }
    return render(request, 'payments/payment_success.html', context)


@login_required
def payment_cancel(request):
    """Payment cancelled page"""
    return render(request, 'payments/payment_cancel.html')


@login_required
def apply_coupon(request):
    """Apply coupon code"""
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip().upper()
        
        try:
            coupon = Coupon.objects.get(code=code)
            
            if not coupon.is_valid():
                messages.error(request, 'This coupon is not valid or has expired.')
            else:
                request.session['coupon_code'] = code
                messages.success(request, f'Coupon "{code}" applied successfully!')
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code.')
    
    return redirect('payments:cart')


@login_required
def remove_coupon(request):
    """Remove applied coupon"""
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
        messages.success(request, 'Coupon removed.')
    
    return redirect('payments:cart')


@login_required
def order_history(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__course')
    
    context = {
        'orders': orders,
    }
    return render(request, 'payments/order_history.html', context)


@login_required
def order_detail(request, order_number):
    """Display order details"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = order.items.select_related('course')
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'payments/order_detail.html', context)


@login_required
def buy_now(request, course_id):
    """Direct purchase - skip cart"""
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    # Check if already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('courses:course_detail', slug=course.slug)
    
    # Clear cart and add only this course
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()
    CartItem.objects.create(cart=cart, course=course)
    
    return redirect('payments:checkout')


@login_required
@require_POST
def create_razorpay_order(request):
    """Create a Razorpay order"""
    if not razorpay:
        return JsonResponse({'error': 'Razorpay is not configured'}, status=400)
    
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('course')
        
        if not cart_items.exists():
            return JsonResponse({'error': 'Cart is empty'}, status=400)
        
        # Calculate total
        subtotal = cart.get_total()
        discount = Decimal('0.00')
        
        coupon_code = request.session.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.is_valid():
                    if coupon.discount_type == 'percentage':
                        discount = subtotal * (coupon.discount_value / 100)
                    else:
                        discount = coupon.discount_value
            except Coupon.DoesNotExist:
                pass
        
        final_amount = subtotal - discount
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(
            'YOUR_RAZORPAY_KEY_ID',  # Replace with your key
            'YOUR_RAZORPAY_KEY_SECRET'  # Replace with your secret
        ))
        
        # Create order
        razorpay_order = client.order.create(data={
            'amount': int(final_amount * 100),  # Amount in paise
            'currency': 'INR',
            'notes': {
                'user_id': request.user.id,
                'user_email': request.user.email
            }
        })
        
        return JsonResponse({
            'order_id': razorpay_order['id'],
            'amount': final_amount,
            'currency': 'INR'
        })
    
    except Cart.DoesNotExist:
        return JsonResponse({'error': 'Cart not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def verify_razorpay_payment(request):
    """Verify Razorpay payment"""
    if not razorpay:
        return JsonResponse({'error': 'Razorpay is not configured'}, status=400)
    
    try:
        data = json.loads(request.body)
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(
            'YOUR_RAZORPAY_KEY_ID',  # Replace with your key
            'YOUR_RAZORPAY_KEY_SECRET'  # Replace with your secret
        ))
        
        # Verify signature
        client.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })
        
        # Payment verified - create order and enrollments
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('course')
        
        subtotal = cart.get_total()
        discount = Decimal('0.00')
        coupon = None
        
        coupon_code = request.session.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.is_valid():
                    if coupon.discount_type == 'percentage':
                        discount = subtotal * (coupon.discount_value / 100)
                    else:
                        discount = coupon.discount_value
            except Coupon.DoesNotExist:
                pass
        
        final_amount = subtotal - discount
        
        # Create order
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total_amount=subtotal,
                discount_amount=discount,
                final_amount=final_amount,
                payment_method='razorpay',
                payment_status='completed',
                razorpay_payment_id=data['razorpay_payment_id'],
                razorpay_order_id=data['razorpay_order_id']
            )
            
            # Create order items and enrollments
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    course=item.course,
                    price=item.course.get_actual_price()
                )
                
                # Create enrollment
                Enrollment.objects.create(
                    user=request.user,
                    course=item.course
                )
                
                # Update course enrollment count
                item.course.total_enrollments += 1
                item.course.save()
            
            # Create invoice
            from .models import Invoice
            Invoice.objects.create(
                order=order,
                invoice_number=Invoice.generate_invoice_number(),
                subtotal=subtotal,
                discount_amount=discount,
                tax_amount=0,
                total_amount=final_amount,
                notes="Razorpay payment verified automatically"
            )
            
            # Update coupon usage
            if coupon:
                coupon.used_count += 1
                coupon.save()
                if 'coupon_code' in request.session:
                    del request.session['coupon_code']
            
            # Clear cart
            cart.items.all().delete()
            
            # Send payment approved email
            from .emails import send_payment_approved_email
            send_payment_approved_email(order)
        
        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'message': 'Payment verified successfully'
        })
    
    except razorpay.BadRequestError:
        return JsonResponse({'error': 'Invalid payment details'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def upi_payment(request):
    """UPI Payment Page"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.select_related('course')
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('payments:cart')
    
    # Calculate totals
    subtotal = cart.get_total()
    discount = Decimal('0.00')
    coupon = None
    
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid():
                if coupon.discount_type == 'percentage':
                    discount = subtotal * (coupon.discount_value / 100)
                else:
                    discount = coupon.discount_value
        except Coupon.DoesNotExist:
            pass
    
    total = subtotal - discount
    
    # Handle form submission (POST request)
    if request.method == 'POST':
        transaction_ref = request.POST.get('transaction_ref', '').strip()
        payment_screenshot = request.FILES.get('payment_screenshot')
        
        if not transaction_ref:
            messages.error(request, 'Please enter the transaction reference/UTR number.')
            # Get payment configuration for re-rendering
            from .models import PaymentConfig
            payment_config = PaymentConfig.get_config()
            
            context = {
                'cart_items': cart_items,
                'subtotal': subtotal,
                'discount': discount,
                'total': total,
                'coupon': coupon,
                'payment_config': payment_config,
            }
            return render(request, 'payments/upi_payment.html', context)
        
        # Create order with pending payment status
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total_amount=subtotal,
                discount_amount=discount,
                final_amount=total,
                payment_method='upi',
                payment_status='pending'
            )
            
            # Create payment transaction record
            from .models import PaymentTransaction
            payment_txn = PaymentTransaction.objects.create(
                order=order,
                transaction_id=transaction_ref,
                payment_method='upi',
                amount=total,
                status='pending',
                upi_transaction_ref=transaction_ref,
                payment_screenshot=payment_screenshot
            )
            
            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    course=item.course,
                    price=item.course.get_actual_price()
                )
            
            # Update coupon usage if applied
            if coupon:
                coupon.used_count += 1
                coupon.save()
                if 'coupon_code' in request.session:
                    del request.session['coupon_code']
            
            # Clear cart
            cart.items.all().delete()
        
        messages.success(request, 'Payment details submitted successfully! Your payment will be verified within 24 hours.')
        return redirect('payments:payment_success', order_number=order.order_number)
    
    # GET request - display payment form
    from .models import PaymentConfig
    payment_config = PaymentConfig.get_config()
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
        'coupon': coupon,
        'payment_config': payment_config,
    }
    return render(request, 'payments/upi_payment.html', context)