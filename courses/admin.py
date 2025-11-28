from django.contrib import admin
from .models import Category, Course, Section, Lecture

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