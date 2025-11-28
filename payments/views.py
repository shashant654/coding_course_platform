from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import Cart, CartItem, Order, OrderItem, Coupon
from courses.models import Course
from enrollment.models import Enrollment


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
    """Payment success page"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = order.items.select_related('course')
    
    context = {
        'order': order,
        'order_items': order_items,
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