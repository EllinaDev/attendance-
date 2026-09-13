from django.contrib import admin
from .models import Course, Lesson, Attendance, Assignment, Submission

admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Attendance)
admin.site.register(Assignment)
admin.site.register(Submission)
