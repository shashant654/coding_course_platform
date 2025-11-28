from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Wishlist, Certificate, Enrollment
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
    
    # Future implementation with reportlab:
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, landscape
    from io import BytesIO
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    
    # Draw certificate
    p.setFont("Helvetica-Bold", 36)
    p.drawCentredString(400, 500, "Certificate of Completion")
    
    p.setFont("Helvetica", 24)
    p.drawCentredString(400, 400, f"{certificate.user.get_full_name()}")
    
    p.setFont("Helvetica", 18)
    p.drawCentredString(400, 350, f"has successfully completed")
    p.drawCentredString(400, 300, f"{certificate.course.title}")
    
    p.setFont("Helvetica", 12)
    p.drawCentredString(400, 200, f"Certificate No: {certificate.certificate_number}")
    p.drawCentredString(400, 180, f"Date: {certificate.issued_date.strftime('%B %d, %Y')}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{certificate.certificate_number}.pdf"'
    
    return response
    """