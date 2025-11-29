from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Course, Category, Section, Lecture
from enrollment.models import Enrollment, LectureProgress
from reviews.models import Review




def course_list(request):
    """Display all published courses"""
    courses = Course.objects.filter(is_published=True).select_related(
        'instructor', 'category'
    ).annotate(
        student_count=Count('enrollments'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-created_at')
    
    # Filters
    level = request.GET.get('level')
    category = request.GET.get('category')
    price = request.GET.get('price')
    
    if level:
        courses = courses.filter(level=level)
    if category:
        courses = courses.filter(category__slug=category)
    if price == 'free':
        courses = courses.filter(price=0)
    elif price == 'paid':
        courses = courses.filter(price__gt=0)
    
    # Pagination
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_level': level,
        'selected_category': category,
        'selected_price': price,
    }
    return render(request, 'courses/course_list.html', context)


def search_courses(request):
    """Search courses"""
    query = request.GET.get('q', '')
    
    if query:
        courses = Course.objects.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(detailed_description__icontains=query) |
            Q(instructor__username__icontains=query) |
            Q(category__name__icontains=query),
            is_published=True
        ).select_related('instructor', 'category').annotate(
            student_count=Count('enrollments'),
            avg_rating=Avg('reviews__rating')
        ).distinct()
    else:
        courses = Course.objects.none()
    
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'total_results': courses.count(),
    }
    return render(request, 'courses/search_results.html', context)


def category_courses(request, slug):
    """Display courses by category"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    courses = Course.objects.filter(
        category=category, 
        is_published=True
    ).select_related('instructor').annotate(
        student_count=Count('enrollments'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-created_at')
    
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'courses/category_courses.html', context)


def course_detail(request, slug):
    """Display course detail page"""
    course = get_object_or_404(
        Course.objects.select_related('instructor', 'category'),
        slug=slug,
        is_published=True
    )
    
    # Get sections and lectures
    sections = course.sections.prefetch_related('lectures').order_by('order')
    
    # Get reviews
    reviews = course.reviews.filter(is_approved=True).select_related('user')[:10]
    
    # Check if user is enrolled
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    # Get related courses
    related_courses = Course.objects.filter(
        category=course.category,
        is_published=True
    ).exclude(id=course.id).annotate(
        student_count=Count('enrollments')
    )[:4]
    
    context = {
        'course': course,
        'sections': sections,
        'reviews': reviews,
        'is_enrolled': is_enrolled,
        'related_courses': related_courses,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def course_player(request, slug, lecture_id=None):
    """Course player for enrolled students"""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    # Check if user is enrolled
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
    except Enrollment.DoesNotExist:
        messages.error(request, 'You must enroll in this course to access it.')
        return redirect('courses:course_detail', slug=slug)
    
    # Get all sections and lectures
    sections = course.sections.prefetch_related('lectures').order_by('order')
    
    # Get current lecture
    if lecture_id:
        current_lecture = get_object_or_404(Lecture, id=lecture_id, section__course=course)
    else:
        # Get first lecture
        first_section = sections.first()
        if first_section and first_section.lectures.exists():
            current_lecture = first_section.lectures.first()
        else:
            messages.error(request, 'This course has no lectures yet.')
            return redirect('courses:course_detail', slug=slug)
    
    # Get or create lecture progress
    lecture_progress, created = LectureProgress.objects.get_or_create(
        enrollment=enrollment,
        lecture=current_lecture
    )
    
    # Get all lecture progress for sidebar
    all_progress = LectureProgress.objects.filter(enrollment=enrollment)
    completed_lecture_ids = set(all_progress.filter(is_completed=True).values_list('lecture_id', flat=True))
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'sections': sections,
        'current_lecture': current_lecture,
        'lecture_progress': lecture_progress,
        'completed_lecture_ids': completed_lecture_ids,
    }
    return render(request, 'courses/course_player.html', context)


@login_required
def update_lecture_progress(request):
    """AJAX endpoint to update lecture progress"""
    if request.method == 'POST':
        lecture_id = request.POST.get('lecture_id')
        is_completed = request.POST.get('is_completed') == 'true'
        
        try:
            lecture = Lecture.objects.get(id=lecture_id)
            enrollment = Enrollment.objects.get(
                user=request.user,
                course=lecture.section.course
            )
            
            progress, created = LectureProgress.objects.get_or_create(
                enrollment=enrollment,
                lecture=lecture
            )
            
            progress.is_completed = is_completed
            if is_completed:
                from django.utils import timezone
                progress.completed_at = timezone.now()
            progress.save()
            
            # Update enrollment progress
            total_lectures = lecture.section.course.sections.aggregate(
                total=Count('lectures')
            )['total'] or 1
            
            completed_lectures = LectureProgress.objects.filter(
                enrollment=enrollment,
                is_completed=True
            ).count()
            
            enrollment.progress_percentage = (completed_lectures / total_lectures) * 100
            enrollment.save()
            
            return JsonResponse({
                'success': True,
                'progress': enrollment.progress_percentage
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})


@login_required
def create_course(request):
    """Create new course (instructors only)"""
    if not request.user.is_instructor:
        messages.error(request, 'You must be an instructor to create courses.')
        return redirect('home')
    
    if request.method == 'POST':
        # Handle course creation
        # This will be implemented with forms
        pass
    
    return render(request, 'instructor/create_course.html')


@login_required
def edit_course(request, slug):
    """Edit course (instructors only)"""
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    
    if request.method == 'POST':
        # Handle course editing
        pass
    
    context = {'course': course}
    return render(request, 'instructor/edit_course.html', context)


@login_required
def delete_course(request, slug):
    """Delete course (instructors only)"""
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('users:instructor_courses')
    
    context = {'course': course}
    return render(request, 'instructor/delete_course_confirm.html', context)


@login_required
def manage_sections(request, slug):
    """Manage course sections"""
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    sections = course.sections.order_by('order')
    
    context = {
        'course': course,
        'sections': sections,
    }
    return render(request, 'instructor/manage_sections.html', context)


@login_required
def manage_lectures(request, slug, section_id):
    """Manage section lectures"""
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    section = get_object_or_404(Section, id=section_id, course=course)
    lectures = section.lectures.order_by('order')
    
    context = {
        'course': course,
        'section': section,
        'lectures': lectures,
    }
    return render(request, 'instructor/manage_lectures.html', context)