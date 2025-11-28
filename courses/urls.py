from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Course listing and search
    path('', views.course_list, name='course_list'),
    path('search/', views.search_courses, name='search'),
    path('category/<slug:slug>/', views.category_courses, name='category_courses'),
    
    # Course detail and player
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/player/', views.course_player, name='course_player'),
    path('<slug:slug>/player/<int:lecture_id>/', views.course_player, name='course_player_lecture'),
    
    # AJAX endpoints
    path('ajax/update-progress/', views.update_lecture_progress, name='update_lecture_progress'),
    
    # Instructor - Course Management
    path('instructor/create/', views.create_course, name='create_course'),
    path('instructor/<slug:slug>/edit/', views.edit_course, name='edit_course'),
    path('instructor/<slug:slug>/delete/', views.delete_course, name='delete_course'),
    
    # Instructor - Section Management
    path('instructor/<slug:slug>/sections/', views.manage_sections, name='manage_sections'),
    path('instructor/<slug:slug>/sections/<int:section_id>/lectures/', views.manage_lectures, name='manage_lectures'),
]