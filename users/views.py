from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import User, UserProfile
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
    user = request.user
    
    # Get or create UserProfile
    try:
        user_profile = user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        profile_picture = request.FILES.get('profile_picture')
        
        # Profile fields
        profession = request.POST.get('profession', '').strip()
        bio = request.POST.get('bio', '').strip()
        website = request.POST.get('website', '').strip()
        facebook = request.POST.get('facebook', '').strip()
        twitter = request.POST.get('twitter', '').strip()
        linkedin = request.POST.get('linkedin', '').strip()
        github = request.POST.get('github', '').strip()
        
        # Validation errors
        errors = []
        
        # Basic validation
        if not first_name:
            errors.append('First name is required.')
        if not last_name:
            errors.append('Last name is required.')
        
        # Bio length validation
        if len(bio) > 500:
            errors.append('Bio must not exceed 500 characters.')
        
        # URL validation for social links and website
        def validate_url(url, field_name):
            if url and not (url.startswith('http://') or url.startswith('https://')):
                return f'{field_name} must start with http:// or https://'
            return None
        
        url_error = validate_url(website, 'Website')
        if url_error:
            errors.append(url_error)
        
        url_error = validate_url(facebook, 'Facebook')
        if url_error:
            errors.append(url_error)
        
        url_error = validate_url(twitter, 'Twitter')
        if url_error:
            errors.append(url_error)
        
        url_error = validate_url(linkedin, 'LinkedIn')
        if url_error:
            errors.append(url_error)
        
        url_error = validate_url(github, 'GitHub')
        if url_error:
            errors.append(url_error)
        
        # Validate profile picture if provided
        if profile_picture:
            max_size = 5 * 1024 * 1024  # 5MB
            if profile_picture.size > max_size:
                errors.append('Profile picture must be less than 5MB.')
            
            # Check file extension
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
            file_extension = profile_picture.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                errors.append('Profile picture must be in JPG, PNG, or GIF format.')
        
        # If there are errors, display them
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'users/edit_profile.html', {
                'user': user,
                'user_profile': user_profile,
            })
        
        try:
            # Update User model
            user.first_name = first_name
            user.last_name = last_name
            user.phone_number = phone_number
            
            # Update profile picture if provided
            if profile_picture:
                user.profile_picture = profile_picture
            
            user.save()
            
            # Update UserProfile model
            user_profile.profession = profession
            user_profile.bio = bio
            user_profile.website = website
            user_profile.facebook = facebook
            user_profile.twitter = twitter
            user_profile.linkedin = linkedin
            user_profile.github = github
            user_profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
            return render(request, 'users/edit_profile.html', {
                'user': user,
                'user_profile': user_profile,
            })
    
    return render(request, 'users/edit_profile.html', {
        'user': user,
        'user_profile': user_profile,
    })


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
