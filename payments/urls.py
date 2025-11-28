from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Cart URLs
    path('cart/', views.view_cart, name='cart'),
    path('cart/add/<int:course_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    
    # Checkout URLs
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.process_payment, name='process_payment'),
    path('checkout/success/<str:order_number>/', views.payment_success, name='payment_success'),
    path('checkout/cancel/', views.payment_cancel, name='payment_cancel'),
    
    # Coupon URLs
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
    
    # Order URLs
    path('orders/', views.order_history, name='order_history'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    
    # Direct purchase (skip cart)
    path('buy-now/<int:course_id>/', views.buy_now, name='buy_now'),
]