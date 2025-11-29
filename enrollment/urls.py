from django.urls import path
from . import views

app_name = 'enrollment'

urlpatterns = [
    # Learning URLs
    path('my-learning/', views.my_learning, name='my_learning'),
    path('daily-classes/', views.daily_classes, name='daily_classes'),
    
    # Wishlist URLs
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:course_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:course_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Certificate URLs
    path('certificate/<int:certificate_id>/', views.view_certificate, name='view_certificate'),
    path('certificate/<int:certificate_id>/download/', views.download_certificate, name='download_certificate'),
    
    # Free enrollment (for free courses)
    path('enroll-free/<int:course_id>/', views.enroll_free_course, name='enroll_free'),
]