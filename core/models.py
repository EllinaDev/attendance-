import uuid
from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    QR_MODES = [
        ('static', 'Static QR'),
        ('time_based', 'Time-Based Dynamic QR'),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    date = models.DateField()
    qr_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_mode = models.CharField(max_length=20, choices=QR_MODES, default='static')
    refresh_interval = models.PositiveIntegerField(null=True, blank=True, help_text='Seconds between QR refreshes (time_based mode)')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.course.title} ({self.date})"

class Attendance(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        if self.student:
            return f"{self.student.username} attended {self.lesson.title}"
        return f"Anonymous Student attended {self.lesson.title}"

class Assignment(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='assignment')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assignment for {self.lesson.title}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignment.title}"


