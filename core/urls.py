from django.urls import path
from . import views

urlpatterns = [
    path('manifest.json', views.manifest, name='manifest'),
    path('sw.js', views.service_worker, name='service_worker'),
    path('', views.home, name='home'),
    path('login/', views.custom_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/course/<int:pk>/', views.student_course_detail, name='student_course_detail'),
    path('courses/', views.course_list, name='course_list'),
    path('course/create/', views.course_create, name='course_create'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('course/<int:pk>/delete/', views.course_delete, name='course_delete'),
    path('course/<int:course_pk>/lesson/create/', views.lesson_create, name='lesson_create'),
    path('lesson/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('qr/<uuid:uuid>/', views.generate_qr, name='generate_qr'),
    path('scan/<uuid:uuid>/', views.scan_qr, name='scan_qr'),
    path('scan/<uuid:uuid>/time/<str:token>/', views.scan_qr, {'mode': 'time'}, name='scan_time_qr'),
    path('api/lesson/<int:pk>/count/', views.get_attendance_count, name='get_attendance_count'),
    path('api/lesson/<int:pk>/set-mode/', views.set_lesson_mode, name='set_lesson_mode'),
    path('api/lesson/<int:pk>/attendance-list/', views.get_attendance_list, name='get_attendance_list'),
    path('assignment/<int:pk>/', views.assignment_detail, name='assignment_detail'),
]
