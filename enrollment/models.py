from django.db import models
from users.models import User
from courses.models import Course, Lecture

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    last_accessed = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
    class Meta:
        db_table = 'enrollments'
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']


class LectureProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lecture_progress')
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    watched_duration = models.PositiveIntegerField(default=0, help_text="Duration in seconds")
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.enrollment.user.username} - {self.lecture.title}"
    
    class Meta:
        db_table = 'lecture_progress'
        unique_together = ['enrollment', 'lecture']


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
    class Meta:
        db_table = 'wishlist'
        unique_together = ['user', 'course']


class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    certificate_number = models.CharField(max_length=50, unique=True)
    issued_date = models.DateTimeField(auto_now_add=True)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} Certificate"
    
    class Meta:
        db_table = 'certificates'
        unique_together = ['user', 'course']


class DailyClass(models.Model):
    """Google Meet classes for enrolled students"""
    date = models.DateField(help_text="Date when the class is scheduled")
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='daily_classes',
        help_text="Leave blank for classes available to all enrolled students"
    )
    title = models.CharField(max_length=200, help_text="Class title/topic")
    description = models.TextField(help_text="Class agenda and topics to be covered")
    meet_link = models.URLField(help_text="Google Meet link for the class")
    scheduled_time = models.TimeField(help_text="Scheduled start time")
    duration_minutes = models.PositiveIntegerField(default=60, help_text="Expected duration in minutes")
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide this class")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_classes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        course_name = self.course.title if self.course else "All Students"
        return f"{self.date} - {self.title} ({course_name})"
    
    class Meta:
        db_table = 'daily_classes'
        ordering = ['-date', '-scheduled_time']
        verbose_name = 'Daily Class'
        verbose_name_plural = 'Daily Classes'