from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages


def user_login(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'users/login.html')


def user_logout(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'Logout successful!')
    return redirect('home')


def register(request):
    """Handle user registration"""
    if request.method == 'POST':
        # TODO: Implement registration logic
        pass
    
    return render(request, 'users/register.html')


@login_required(login_url='users:login')
def profile(request):
    """Display user profile"""
    return render(request, 'users/profile.html')


@login_required(login_url='users:login')
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        # TODO: Implement profile update logic
        pass
    
    return render(request, 'users/edit_profile.html')


@login_required(login_url='users:login')
def user_dashboard(request):
    """Display user dashboard"""
    return render(request, 'users/dashboard.html')


@login_required(login_url='users:login')
def my_courses(request):
    """Display user's enrolled courses"""
    return render(request, 'users/my_courses.html')


@login_required(login_url='users:login')
def instructor_dashboard(request):
    """Display instructor dashboard"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    return render(request, 'users/instructor/dashboard.html')


@login_required(login_url='users:login')
def instructor_courses(request):
    """Display instructor's courses"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    return render(request, 'users/instructor/courses.html')


@login_required(login_url='users:login')
def instructor_analytics(request):
    """Display instructor analytics"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    return render(request, 'users/instructor/analytics.html')
