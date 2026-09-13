import os
import django
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qrassist.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Course, Lesson, Attendance, Assignment, Submission

print("Seeding database...")

# Clear existing data
Submission.objects.all().delete()
Assignment.objects.all().delete()
Attendance.objects.all().delete()
Lesson.objects.all().delete()
Course.objects.all().delete()

# Create Users
def get_or_create_user(username, email, first_name, last_name, is_superuser=False):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'is_staff': is_superuser,
            'is_superuser': is_superuser
        }
    )
    user.set_password('password123')
    user.save()
    return user

admin_user = get_or_create_user('admin', 'admin@qrassist.io', 'System', 'Admin', is_superuser=True)
prof_smith = get_or_create_user('prof_smith', 'smith@university.edu', 'Prof. Alan', 'Turing')
dr_johnson = get_or_create_user('dr_johnson', 'johnson@university.edu', 'Dr. Katherine', 'Johnson')

students = [
    get_or_create_user('alex_dev', 'alex@student.edu', 'Alex', 'Rivera'),
    get_or_create_user('maria_tech', 'maria@student.edu', 'Maria', 'Chen'),
    get_or_create_user('sam_coder', 'sam@student.edu', 'Sam', 'Vance'),
    get_or_create_user('elena_m', 'elena@student.edu', 'Elena', 'Mamadal'),
    get_or_create_user('david_k', 'david@student.edu', 'David', 'Kim'),
    get_or_create_user('sophia_w', 'sophia@student.edu', 'Sophia', 'Williams'),
]

# Create Courses
c1 = Course.objects.create(
    title="CS 401: Dynamic Systems & Real-Time QR Architecture",
    description="Advanced study of dynamic cryptographic verification, time-based OTP protocols, and progressive Web Apps for automated attendance sync.",
    teacher=prof_smith
)

c2 = Course.objects.create(
    title="CS 502: High-Performance Distributed Systems",
    description="Deep dive into Raft consensus, vector clocks, asynchronous message brokers, and low-latency database replication.",
    teacher=dr_johnson
)

c3 = Course.objects.create(
    title="CS 305: Cryptographic Engineering & Network Protocols",
    description="Hands-on engineering of zero-trust authentication, HMAC token signatures, and replay attack mitigation strategies.",
    teacher=prof_smith
)

# Create Lessons
l1 = Lesson.objects.create(
    course=c1,
    title="Lecture 07: Cryptographic Salt & Dynamic QR Verification",
    date=datetime.date.today(),
    qr_mode='time_based',
    refresh_interval=5
)

l2 = Lesson.objects.create(
    course=c1,
    title="Lecture 06: Service Worker Caching & PWA Offline Sync",
    date=datetime.date.today() - datetime.timedelta(days=2),
    qr_mode='static'
)

l3 = Lesson.objects.create(
    course=c2,
    title="Lecture 04: Vector Clocks & Eventual Consistency",
    date=datetime.date.today() - datetime.timedelta(days=1),
    qr_mode='time_based',
    refresh_interval=8
)

l4 = Lesson.objects.create(
    course=c3,
    title="Lecture 03: Replay Attack Defense using Time Windows",
    date=datetime.date.today() - datetime.timedelta(days=3),
    qr_mode='static'
)

# Create Attendance records
for s in students[:5]:
    Attendance.objects.create(lesson=l1, student=s)

for s in students[1:4]:
    Attendance.objects.create(lesson=l2, student=s)

for s in students:
    Attendance.objects.create(lesson=l3, student=s)

for s in students[:3]:
    Attendance.objects.create(lesson=l4, student=s)

# Create Assignments
a1 = Assignment.objects.create(
    lesson=l1,
    title="Implementation of Dynamic Token Signing in Python",
    description="Write a Django middleware or utility function using `django.core.signing.Signer` that signs timestamp windows for 5-second QR rotation.",
    due_date=timezone.now() + datetime.timedelta(days=5)
)

a2 = Assignment.objects.create(
    lesson=l3,
    title="Distributed Consensus Benchmark Report",
    description="Analyze throughput vs latency trade-offs under high network concurrency when logging student attendance events.",
    due_date=timezone.now() + datetime.timedelta(days=7)
)

# Submissions
Submission.objects.create(
    assignment=a1,
    student=students[0],
    content="""def generate_time_token(uuid, interval=5):
    time_window = int(time.time() // interval)
    signer = Signer(salt='qr_time_based')
    return signer.sign(f"{uuid}:{time_window}")
"""
)

Submission.objects.create(
    assignment=a1,
    student=students[1],
    content="""# Verification algorithm logic
def verify_qr(token, interval=5):
    signer = Signer(salt='qr_time_based')
    unsigned = signer.unsign(token)
    curr_window = int(time.time() // interval)
    token_window = int(unsigned.split(':')[-1])
    return abs(curr_window - token_window) <= 1
"""
)

print(f"Successfully seeded database: {User.objects.count()} Users, {Course.objects.count()} Courses, {Lesson.objects.count()} Lessons, {Attendance.objects.count()} Attendances, {Assignment.objects.count()} Assignments!")
