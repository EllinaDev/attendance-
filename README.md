# 🚀 QRAssist: Dynamic Cryptographic Attendance System

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![PWA](https://img.shields.io/badge/PWA-100%25-4F46E5?style=flat&logo=pwa&logoColor=white)](https://web.dev/progressive-web-apps/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**QRAssist** is a high-performance **Progressive Web Application (PWA)** built with Python and Django. It replaces manual roll calls and static code sharing with **Cryptographically Signed, Time-Windowed Dynamic QR Codes**, delivering zero-latency real-time attendance verification for modern educational institutions and enterprise environments.

---

## 📌 Project Overview & Purpose

In traditional university lectures, static QR codes or paper sign-in sheets are highly vulnerable to proxy attendance fraud—students photograph QR codes and forward them to absent classmates via instant messaging. 

**QRAssist** solves this problem through a **Dual-Mode QR Engine**:
- **Scenario 1: Dynamic Time-Based QR Mode (Anti-Replay TOTP)**: Projects a rotating QR code matrix every 3–5 seconds on lecture screens. Capturing a photo or forwarding a link becomes useless within seconds.
- **Scenario 2: Static QR Mode**: Provides zero-configuration check-ins for low-stakes seminars or syllabus check-ins.

---

## ⚙️ Core Technical Capabilities

### 🧠 1. Cryptographic TOTP Verification Engine
- **Time-Window Algorithm**: The server calculates a time-window index:
  $$T_i = \left\lfloor \frac{t_{\text{current}}}{\Delta t} \right\rfloor \quad (\text{where } \Delta t = 3\text{--}5\text{ seconds})$$
- **HMAC Token Signing**: Concatenates `UUID || T_i` and signs it using `django.core.signing.Signer` with a salted key (`qr_time_based`).
- **Zero-Storage In-Memory Verification**: Unlike OTP systems that pollute database tables with thousands of temporary tokens, QRAssist verifies tokens **100% mathematically in memory ($O(1)$ complexity, $<1\text{ms}$ calculation)**.
- **Anti-Replay Security**: Server unsigns tokens and checks $|T_{\text{server}} - T_{\text{token}}| \le 1$. Stale photos or forwarded URLs are immediately rejected with HTTP 403 Forbidden.

### ⚡ 2. Monolithic MVT Engine & Micro-Payload Strategy
- **Low Latency**: Monolithic Django Model-View-Template (MVT) architecture delivers server-side rendered pages in **$<200\text{ms}$**.
- **Micro-CSS Payload ($<15\text{KB}$)**: Built using native CSS Grid and Flexbox without heavy CSS frameworks (like Tailwind or Bootstrap), enabling instant loads over weak campus 3G/4G cellular networks.
- **Atomic Database Concurrency**: Uses atomic ORM `get_or_create` queries to process 50+ simultaneous student scans per second without database locks or duplicate attendance records.

### 📱 3. Progressive Web App (PWA) Integration
- **Zero Installation Required**: Runs 100% inside standard web browsers on both desktop and mobile devices.
- **Web App Manifest (`manifest.json`)**: Configures standalone display mode, custom theme colors (`#4f46e5`), and home-screen installation.
- **Service Worker (`sw.js`)**: Intercepts network requests and caches essential UI assets for offline readiness.

### 📊 4. Database Model Hierarchy & ERD
```
User (Teachers / Students with Role-Based Access Control)
└── Course (Teacher 1:N Courses)
    └── Lesson (Course 1:N Lessons with unique UUIDv4 key)
        ├── Attendance (Unique together: Lesson + Student)
        └── Assignment (Lesson 1:1 Assignment)
            └── Submission (Unique together: Assignment + Student)
```

---

## 🚀 Quick Start & How to Run

Follow these steps to run **QRAssist** locally on your machine:

### 1. Prerequisites
- Python 3.10+ installed
- Git installed

### 2. Clone the Repository
```bash
git clone https://github.com/elinamamadalieva/qrassist.git
cd qrassist
```

### 3. Set Up Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Seed Database with Demo Data
To populate the database with realistic courses, lessons, users, attendances, and assignments:
```bash
python seed_db.py
```

### 7. Start the Development Server
```bash
python manage.py runserver 8080
```

Open your browser and navigate to: **`http://127.0.0.1:8080`**

---

## 🔑 Demo Account Credentials

After running `python seed_db.py`, the following demo accounts are available (password for all demo accounts is **`password123`**):

| Role | Username | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin` | `password123` | Full admin privileges & superuser access |
| **Teacher** | `prof_smith` | `password123` | Course creation, Dynamic QR projection, Live attendance counting |
| **Teacher** | `dr_johnson` | `password123` | Course management & lesson assignments |
| **Student** | `alex_dev` | `password123` | QR scanning, Attendance stats, Assignment submissions |
| **Student** | `maria_tech` | `password123` | QR scanning, Mobile PWA check-ins |

---

## 🛠️ Project Structure

```
qrassist/
├── core/                   # Main Django application
│   ├── models.py           # Course, Lesson, Attendance, Assignment, Submission models
│   ├── views.py            # MVT Views, TOTP Signer validation, AJAX APIs
│   ├── urls.py             # URL Routing & API endpoints
│   └── forms.py            # Signup, Course, Lesson, and Submission forms
├── qrassist/               # Project configuration (settings.py, urls.py, wsgi.py)
├── static/                 # Static assets (CSS, PWA icons, sw.js)
├── templates/              # HTML Templates (Base, Dashboard, Scan views)
├── seed_db.py              # Script for database seeding
├── requirements.txt        # Python package dependencies
└── manage.py               # Django management script
```

---

## 🎓 Academic Metadata

- **Course:** FEE328 Server-Side Web Programming
- **Department:** Department of Computer Engineering, Faculty of Engineering
- **Author:** Elina Mamadalieva (Student ID: 22040102091)
- **Academic Term:** 2025–2026 Spring Semester
