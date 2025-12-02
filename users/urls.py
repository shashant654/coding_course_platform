from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),

    # Two-Factor Authentication URLs
    path('2fa/setup-prompt/', views.setup_2fa_prompt, name='setup_2fa_prompt'),
    path('2fa/enable/', views.enable_2fa, name='enable_2fa'),
    path('2fa/skip/', views.setup_2fa_skip, name='setup_2fa_skip'),
    path('2fa/verify-setup/', views.verify_2fa_setup, name='verify_2fa_setup'),
    path('2fa/verify/', views.verify_2fa, name='verify_2fa'),
    path('2fa/resend/', views.resend_2fa_code, name='resend_2fa_code'),
    path('2fa/disable/', views.disable_2fa, name='disable_2fa'),
    
    # Profile URLs
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('my-courses/', views.my_courses, name='my_courses'),
    
    # Instructor URLs
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/courses/', views.instructor_courses, name='instructor_courses'),
    path('instructor/analytics/', views.instructor_analytics, name='instructor_analytics'),
    
    
    # Password Reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
]