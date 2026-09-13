import json
import time
from pathlib import Path
from functools import wraps
import qrcode
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.signing import Signer
from django.views.decorators.csrf import csrf_exempt
from .models import Course, Lesson, Attendance, Assignment, Submission
from .forms import CourseForm, LessonForm, AssignmentForm, SubmissionForm, UserSignupForm

def teacher_required(view_func):
    @wraps(view_func)
    @login_required(login_url='/login/')
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser or request.session.get('role') == 'teacher':
            return view_func(request, *args, **kwargs)
        return redirect('student_dashboard')
    return wrapper

def student_required(view_func):
    @wraps(view_func)
    @login_required(login_url='/login/')
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser or request.session.get('role') == 'student':
            return view_func(request, *args, **kwargs)
        return redirect('dashboard')
    return wrapper

def home(request):
    return render(request, 'core/home.html')

def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session['role'] = request.POST.get('role', 'student')
            return redirect('student_dashboard')
    else:
        form = UserSignupForm()
    return render(request, 'registration/signup.html', {'form': form})

def custom_login(request):
    next_url = request.GET.get('next') or request.POST.get('next') or ''
    role = request.POST.get('role', 'student')
    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        request.session['role'] = role
        if next_url:
            return redirect(next_url)
        if role == 'teacher':
            return redirect('dashboard')
        return redirect('student_dashboard')
    form_errors = form.errors if request.method == 'POST' else None
    return render(request, 'registration/login.html', {
        'form': form, 'form_errors': form_errors, 'next': next_url
    })

@teacher_required
def dashboard(request):
    courses_teaching = Course.objects.filter(teacher=request.user)
    all_courses = None
    if request.user.is_superuser:
        all_courses = Course.objects.all().order_by('-created_at').select_related('teacher')
    return render(request, 'core/dashboard.html', {
        'courses_teaching': courses_teaching,
        'all_courses': all_courses,
    })

@student_required
def student_dashboard(request):
    attended_course_ids = Attendance.objects.filter(
        student=request.user
    ).values_list('lesson__course', flat=True).distinct()
    attended_courses = Course.objects.filter(
        pk__in=attended_course_ids
    ).order_by('-created_at').select_related('teacher')

    course_data = []
    for course in attended_courses:
        attended = Attendance.objects.filter(
            student=request.user, lesson__course=course
        ).count()
        total = course.lessons.count()
        course_data.append({'course': course, 'attended': attended, 'total': total})

    recent_attendances = Attendance.objects.filter(
        student=request.user
    ).select_related('lesson__course').order_by('-timestamp')[:20]

    return render(request, 'core/student_dashboard.html', {
        'course_data': course_data,
        'recent_attendances': recent_attendances,
    })

@student_required
def student_course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    lessons = course.lessons.all().order_by('-date').select_related('assignment')

    lesson_data = []
    for lesson in lessons:
        attended = lesson.attendances.filter(student=request.user).exists()
        lesson_data.append({
            'lesson': lesson,
            'attended': attended,
        })

    return render(request, 'core/student_course_detail.html', {
        'course': course,
        'lesson_data': lesson_data,
    })

@teacher_required
def course_list(request):
    courses = Course.objects.all().order_by('-created_at')
    return render(request, 'core/course_list.html', {'courses': courses})

@teacher_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            if request.user.is_superuser and request.POST.get('teacher'):
                course.teacher = get_object_or_404(User, pk=request.POST['teacher'])
            else:
                course.teacher = request.user
            course.save()
            return redirect('course_detail', pk=course.pk)
    else:
        form = CourseForm()
    teachers = None
    if request.user.is_superuser:
        teachers = User.objects.all().order_by('username')
    return render(request, 'core/course_form.html', {'form': form, 'teachers': teachers})

@teacher_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    lessons = course.lessons.all().order_by('-date')
    return render(request, 'core/course_detail.html', {'course': course, 'lessons': lessons})

@teacher_required
def lesson_create(request, course_pk):
    # Input Form 2
    course = get_object_or_404(Course, pk=course_pk)
    if course.teacher != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("Only the teacher can create lessons.")

    if request.method == 'POST':
        lesson_form = LessonForm(request.POST)
        assignment_form = AssignmentForm(request.POST)
        if lesson_form.is_valid() and assignment_form.is_valid():
            lesson = lesson_form.save(commit=False)
            lesson.course = course
            lesson.save()
            
            # create assignment if title provided
            if assignment_form.cleaned_data.get('title'):
                assignment = assignment_form.save(commit=False)
                assignment.lesson = lesson
                assignment.save()
            
            return redirect('lesson_detail', pk=lesson.pk)
    else:
        lesson_form = LessonForm()
        assignment_form = AssignmentForm()
    
    return render(request, 'core/lesson_form.html', {
        'course': course,
        'lesson_form': lesson_form,
        'assignment_form': assignment_form
    })

@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    attendances = lesson.attendances.all()
    user_attended = lesson.attendances.filter(student=request.user).exists()

    assignment = getattr(lesson, 'assignment', None)
    submission = None
    if assignment:
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()

    simulate_scan_url = _get_simulate_scan_url(request, lesson)
    is_teacher = request.user == lesson.course.teacher or request.user.is_superuser

    return render(request, 'core/lesson_detail.html', {
        'lesson': lesson,
        'attendances': attendances,
        'user_attended': user_attended,
        'assignment': assignment,
        'submission': submission,
        'host': request.get_host(),
        'simulate_scan_url': simulate_scan_url,
        'is_teacher': is_teacher,
    })

def generate_qr(request, uuid):
    lesson = get_object_or_404(Lesson, qr_uuid=uuid)

    if lesson.qr_mode == 'time_based':
        interval = lesson.refresh_interval or 5
        time_window = int(time.time() // interval)
        signer = Signer(salt='qr_time_based')
        signed = signer.sign(f"{uuid}:{time_window}")
        scan_url = request.build_absolute_uri(f"/scan/{uuid}/time/{signed}/")
    else:
        scan_url = request.build_absolute_uri(f"/scan/{uuid}/")

    img = qrcode.make(scan_url)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return HttpResponse(buffer.getvalue(), content_type="image/png")

def scan_qr(request, uuid, mode='static', token=None):
    lesson = get_object_or_404(Lesson, qr_uuid=uuid)

    if not request.user.is_authenticated:
        return redirect(f"/login/?next={request.get_full_path()}")

    if mode == 'time':
        signer = Signer(salt='qr_time_based')
        try:
            unsigned = signer.unsign(token)
            expected_prefix = f"{uuid}:"
            if not unsigned.startswith(expected_prefix):
                return render(request, 'core/scan_error.html', {
                    'title': 'Invalid QR Code',
                    'message': 'This QR code could not be verified.',
                    'hint': 'Scan the latest code on screen.',
                    'variant': 'error',
                    'lesson': lesson,
                })
            time_window = int(unsigned.split(":")[-1])
            interval = lesson.refresh_interval or 5
            current_window = int(time.time() // interval)
            if abs(current_window - time_window) > 1:
                return render(request, 'core/scan_error.html', {
                    'title': 'QR Code Expired',
                    'message': 'The QR code changes every %ds.' % interval,
                    'hint': 'Scan the current code shown on screen.',
                    'variant': 'error',
                    'lesson': lesson,
                })
        except Exception:
            return render(request, 'core/scan_error.html', {
                'title': 'Scan Failed',
                'message': 'Could not process the QR code.',
                'hint': 'Please scan the code on the teacher\'s screen.',
                'variant': 'error',
                'lesson': lesson,
            })

    _att, created = Attendance.objects.get_or_create(lesson=lesson, student=request.user)
    if not created:
        return render(request, 'core/scan_error.html', {
            'title': 'Already Checked In',
            'message': 'Your attendance was already recorded.',
            'hint': 'You may now close this page.',
            'variant': 'info',
            'lesson': lesson,
        })

    return render(request, 'core/scan_success.html', {'lesson': lesson})


def _get_simulate_scan_url(request, lesson):
    if lesson.qr_mode == 'time_based':
        interval = lesson.refresh_interval or 5
        time_window = int(time.time() // interval)
        signer = Signer(salt='qr_time_based')
        signed = signer.sign(f"{lesson.qr_uuid}:{time_window}")
        return f"/scan/{lesson.qr_uuid}/time/{signed}/"
    return f"/scan/{lesson.qr_uuid}/"

def get_attendance_count(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    count = lesson.attendances.count()
    return JsonResponse({'count': count})

@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.assignment = assignment
            sub.student = request.user
            sub.save()
            return redirect('lesson_detail', pk=assignment.lesson.pk)
    else:
        form = SubmissionForm(instance=submission)
        
    return render(request, 'core/assignment_detail.html', {
        'assignment': assignment,
        'form': form,
        'submission': submission
    })

def manifest(request):
    return JsonResponse({
        "name": "QRAssist",
        "short_name": "QRAssist",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#f3f4f6",
        "theme_color": "#4f46e5",
        "description": "QR-based attendance tracking",
        "icons": [
            {"src": "/static/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ]
    })

def service_worker(request):
    sw_path = Path(__file__).resolve().parent.parent / 'static' / 'sw.js'
    content = sw_path.read_text()
    return HttpResponse(content, content_type='application/javascript')

@teacher_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if course.teacher == request.user or request.user.is_superuser:
        course.delete()
    return redirect('course_list')

@csrf_exempt
@login_required
def set_lesson_mode(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    lesson = get_object_or_404(Lesson, pk=pk)
    if lesson.course.teacher != request.user and not request.user.is_superuser:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    data = json.loads(request.body)
    lesson.qr_mode = data.get('mode', 'static')
    lesson.refresh_interval = data.get('refresh_interval') or None
    lesson.save()

    return JsonResponse({
        'success': True,
        'mode': lesson.qr_mode,
        'refresh_interval': lesson.refresh_interval,
    })

@login_required
def get_attendance_list(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if lesson.course.teacher != request.user and not request.user.is_superuser:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    records = lesson.attendances.select_related('student').order_by('-timestamp')
    data = []
    for r in records:
        data.append({
            'username': r.student.username if r.student else 'Anonymous',
            'timestamp': r.timestamp.isoformat() if r.timestamp else '',
        })
    return JsonResponse({'attendances': data})
