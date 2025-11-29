"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from courses.models import Course, Category
from django.db.models import Count, Avg

def home(request):
    """Homepage view with featured courses"""
    
    # Get featured courses
    featured_courses = Course.objects.filter(
        is_published=True,
        is_featured=True
    ).select_related('instructor', 'category').annotate(
        student_count=Count('enrollments'),
        avg_rating=Avg('reviews__rating')
    )[:4]
    
    # Get all active categories
    categories = Category.objects.filter(is_active=True)[:8]
    
    # Get popular courses (by enrollment)
    popular_courses = Course.objects.filter(
        is_published=True
    ).select_related('instructor', 'category').annotate(
        student_count=Count('enrollments'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-total_enrollments')[:8]
    
    # Get newest courses
    newest_courses = Course.objects.filter(
        is_published=True
    ).select_related('instructor', 'category').annotate(
        student_count=Count('enrollments'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-created_at')[:8]
    
    context = {
        'featured_courses': featured_courses,
        'categories': categories,
        'popular_courses': popular_courses,
        'newest_courses': newest_courses,
    }
    
    return render(request, 'home/index.html', context)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Updated to use the new home view
    path('users/', include('users.urls')),
    path('courses/', include('courses.urls')),
    path('enrollment/', include('enrollment.urls')),
    path('payments/', include('payments.urls')),
    path('reviews/', include('reviews.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)