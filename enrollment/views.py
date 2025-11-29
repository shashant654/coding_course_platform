from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db import models
from .models import Wishlist, Certificate, Enrollment, DailyClass
from courses.models import Course


@login_required
def wishlist(request):
    """Display user's wishlist"""
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('course', 'course__instructor').order_by('-added_at')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'enrollment/wishlist.html', context)


@login_required
def add_to_wishlist(request, course_id):
    """Add course to wishlist"""
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    # Check if already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('courses:course_detail', slug=course.slug)
    
    # Check if already in wishlist
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        course=course
    )
    
    if created:
        messages.success(request, f'{course.title} added to wishlist.')
    else:
        messages.info(request, f'{course.title} is already in your wishlist.')
    
    # Redirect back to the page they came from or course detail
    next_url = request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('courses:course_detail', slug=course.slug)


@login_required
def remove_from_wishlist(request, course_id):
    """Remove course from wishlist"""
    wishlist_item = get_object_or_404(
        Wishlist,
        user=request.user,
        course_id=course_id
    )
    course_title = wishlist_item.course.title
    wishlist_item.delete()
    
    messages.success(request, f'{course_title} removed from wishlist.')
    
    # Redirect back or to wishlist page
    next_url = request.META.get('HTTP_REFERER')
    if next_url and 'wishlist' not in next_url:
        return redirect(next_url)
    return redirect('enrollment:wishlist')


@login_required
def enroll_free_course(request, course_id):
    """Enroll in a free course directly"""
    course = get_object_or_404(Course, id=course_id, is_published=True, price=0)
    
    # Check if already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('courses:course_detail', slug=course.slug)
    
    # Create enrollment
    enrollment = Enrollment.objects.create(
        user=request.user,
        course=course
    )
    
    # Update course enrollment count
    course.total_enrollments += 1
    course.save()
    
    # Remove from wishlist if present
    Wishlist.objects.filter(user=request.user, course=course).delete()
    
    messages.success(request, f'Successfully enrolled in {course.title}!')
    return redirect('courses:course_player', slug=course.slug)


@login_required
def view_certificate(request, certificate_id):
    """View certificate"""
    certificate = get_object_or_404(
        Certificate,
        id=certificate_id,
        user=request.user
    )
    
    context = {
        'certificate': certificate,
    }
    return render(request, 'enrollment/certificate.html', context)


@login_required
def download_certificate(request, certificate_id):
    """Download certificate as PDF"""
    certificate = get_object_or_404(
        Certificate,
        id=certificate_id,
        user=request.user
    )
    
    # TODO: Implement PDF generation with reportlab
    # For now, just redirect to view
    messages.info(request, 'PDF download feature coming soon!')
    return redirect('enrollment:view_certificate', certificate_id=certificate_id)


@login_required
def my_learning(request):
    """Display user's enrolled courses"""
    enrollments = Enrollment.objects.filter(
        user=request.user
    ).select_related(
        'course', 
        'course__instructor',
        'course__category'
    ).order_by('-enrolled_at')
    
    context = {
        'enrollments': enrollments,
        'total_courses': enrollments.count(),
        'completed_courses': enrollments.filter(is_completed=True).count(),
    }
    return render(request, 'enrollment/my_learning.html', context)


@login_required
def daily_classes(request):
    """Display daily classes for enrolled students"""
    from django.utils import timezone
    from datetime import timedelta
    
    # Check if user has any enrollments
    has_enrollments = Enrollment.objects.filter(user=request.user).exists()
    
    if not has_enrollments:
        messages.warning(request, 'You need to enroll in at least one course to access daily classes.')
        return redirect('courses:course_list')
    
    # Get user's enrolled courses
    enrolled_course_ids = Enrollment.objects.filter(
        user=request.user
    ).values_list('course_id', flat=True)
    
    today = timezone.now().date()
    
    # Today's classes
    todays_classes = DailyClass.objects.filter(
        is_active=True,
        date=today
    ).filter(
        models.Q(course=None) |  # General classes for all students
        models.Q(course_id__in=enrolled_course_ids)  # Course-specific classes
    ).select_related('course', 'created_by').order_by('scheduled_time')
    
    # Upcoming classes (next 7 days)
    upcoming_classes = DailyClass.objects.filter(
        is_active=True,
        date__gt=today,
        date__lte=today + timedelta(days=7)
    ).filter(
        models.Q(course=None) |
        models.Q(course_id__in=enrolled_course_ids)
    ).select_related('course', 'created_by').order_by('date', 'scheduled_time')
    
    # Past classes (last 3 days for reference)
    past_classes = DailyClass.objects.filter(
        is_active=True,
        date__lt=today,
        date__gte=today - timedelta(days=3)
    ).filter(
        models.Q(course=None) |
        models.Q(course_id__in=enrolled_course_ids)
    ).select_related('course', 'created_by').order_by('-date', '-scheduled_time')
    
    context = {
        'todays_classes': todays_classes,
        'upcoming_classes': upcoming_classes,
        'past_classes': past_classes,
        'today': today,
    }
    return render(request, 'enrollment/daily_classes.html', context)