from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import User
from .emails import send_welcome_email
import re


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
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        terms = request.POST.get('terms')

        # print('here',username,email,first_name,last_name,password,terms)
        
        # Validation errors list
        errors = []
        
        # Username validation
        if not username:
            errors.append('Username is required.')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        elif len(username) > 150:
            errors.append('Username must be at most 150 characters long.')
        elif not re.match(r'^[\w.@+-]+$', username):
            errors.append('Username can only contain letters, numbers, and @/./+/- characters.')
        elif User.objects.filter(username=username).exists():
            errors.append('This username is already taken.')
        
        # Email validation
        if not email:
            errors.append('Email is required.')
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append('Please enter a valid email address.')
            
            if User.objects.filter(email=email).exists():
                errors.append('This email is already registered.')
        
        # Password validation
        if not password:
            errors.append('Password is required.')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        elif password != password_confirm:
            errors.append('Passwords do not match.')
        
        # Check password strength
        if password and len(password) >= 8:
            if not re.search(r'[A-Z]', password):
                errors.append('Password must contain at least one uppercase letter.')
            if not re.search(r'[a-z]', password):
                errors.append('Password must contain at least one lowercase letter.')
            if not re.search(r'[0-9]', password):
                errors.append('Password must contain at least one digit.')
        
        # Terms agreement validation
        if not terms:
            errors.append('You must agree to the Terms of Service and Privacy Policy.')
        
        # If there are errors, display them and redirect back to form
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'users/register.html', {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            })
        
        # Create new user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            
            # Send welcome email
            send_welcome_email(user)
            
            # Automatically log in the user after registration
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to CodeLearn. Check your email for a welcome message.')
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'users/register.html', {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            })
    
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
