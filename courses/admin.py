from django.contrib import admin
from .models import Category, Course, Section, Lecture, CallbackRequest

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active']

class SectionInline(admin.TabularInline):
    model = Section
    extra = 1

class LectureInline(admin.TabularInline):
    model = Lecture
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'price', 'is_published', 'is_featured', 'created_at']
    list_filter = ['is_published', 'is_featured', 'level', 'category']
    search_fields = ['title', 'instructor__username']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SectionInline]

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    inlines = [LectureInline]

@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'duration_minutes', 'is_preview', 'order']
    list_filter = ['is_preview']

@admin.register(CallbackRequest)
class CallbackRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'course', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'course']
    search_fields = ['name', 'email', 'phone', 'course__title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Requester Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Course', {
            'fields': ('course',)
        }),
        ('Status', {
            'fields': ('status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )