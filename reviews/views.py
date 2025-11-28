from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import Review
from courses.models import Course
from enrollment.models import Enrollment


@login_required
def add_review(request, slug):
    """Add or update review for a course"""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    # Check if user is enrolled
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, 'You must be enrolled in this course to leave a review.')
        return redirect('courses:course_detail', slug=slug)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if not rating or not comment:
            messages.error(request, 'Please provide both rating and comment.')
            return redirect('courses:course_detail', slug=slug)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except ValueError:
            messages.error(request, 'Invalid rating value.')
            return redirect('courses:course_detail', slug=slug)
        
        # Create or update review
        review, created = Review.objects.update_or_create(
            user=request.user,
            course=course,
            defaults={
                'rating': rating,
                'comment': comment,
            }
        )
        
        # Update course average rating
        avg_rating = course.reviews.filter(is_approved=True).aggregate(
            Avg('rating')
        )['rating__avg'] or 0
        course.average_rating = round(avg_rating, 2)
        course.save()
        
        if created:
            messages.success(request, 'Thank you for your review!')
        else:
            messages.success(request, 'Your review has been updated.')
        
        return redirect('courses:course_detail', slug=slug)
    
    # Check if user already reviewed
    existing_review = Review.objects.filter(user=request.user, course=course).first()
    
    context = {
        'course': course,
        'existing_review': existing_review,
    }
    return render(request, 'reviews/add_review.html', context)


@login_required
def edit_review(request, review_id):
    """Edit existing review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if not rating or not comment:
            messages.error(request, 'Please provide both rating and comment.')
            return redirect('reviews:edit_review', review_id=review_id)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except ValueError:
            messages.error(request, 'Invalid rating value.')
            return redirect('reviews:edit_review', review_id=review_id)
        
        review.rating = rating
        review.comment = comment
        review.save()
        
        # Update course average rating
        course = review.course
        avg_rating = course.reviews.filter(is_approved=True).aggregate(
            Avg('rating')
        )['rating__avg'] or 0
        course.average_rating = round(avg_rating, 2)
        course.save()
        
        messages.success(request, 'Review updated successfully.')
        return redirect('courses:course_detail', slug=course.slug)
    
    context = {
        'review': review,
    }
    return render(request, 'reviews/edit_review.html', context)


@login_required
def delete_review(request, review_id):
    """Delete review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    course = review.course
    
    if request.method == 'POST':
        review.delete()
        
        # Update course average rating
        avg_rating = course.reviews.filter(is_approved=True).aggregate(
            Avg('rating')
        )['rating__avg'] or 0
        course.average_rating = round(avg_rating, 2)
        course.save()
        
        messages.success(request, 'Review deleted successfully.')
        return redirect('courses:course_detail', slug=course.slug)
    
    context = {
        'review': review,
    }
    return render(request, 'reviews/delete_review_confirm.html', context)