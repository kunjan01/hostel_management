# Hostel Management System - Complete Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Getting Started](#getting-started)
3. [Project Structure](#project-structure)
4. [Installation & Setup](#installation--setup)
5. [Running the Project](#running-the-project)
6. [Database & Models](#database--models)
7. [API Endpoints](#api-endpoints)
8. [Celery Background Tasks](#celery-background-tasks)
9. [Docker Deployment](#docker-deployment)
10. [Testing](#testing)
11. [Admin Panel](#admin-panel)
12. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Hostel Management System** is a comprehensive Django REST Framework application for managing hostel operations including:
- 👥 Student management and room allocations
- 🏠 Hostel block and room management
- 🍽️ Mess billing system with meal plans
- 📝 Complaint management system
- ⚡ Celery background tasks for notifications
- 🔐 JWT authentication for API security
- 📊 RESTful API with Swagger documentation
- 🐳 Docker containerization for easy deployment

**Tech Stack:**
- Backend: Django 4.2.11
- API: Django REST Framework 3.15.0
- Database: PostgreSQL 15
- Cache/Broker: Redis 7
- Task Queue: Celery 5.3.4
- Web Server: Gunicorn + Nginx
- Container: Docker & Docker Compose

---

## Getting Started

### Quick Start (Docker - Recommended)
```bash
cd hostel_management
docker-compose up -d
```
Access at: `http://localhost`

### Quick Start (Local Development)
```bash
cd hostel_management
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Access at: `http://localhost:8000`

---

## Project Structure

```
hostel_management/
├── apps/                          # Django applications
│   ├── accounts/                  # User & authentication
│   │   ├── models.py             # User models
│   │   ├── views.py              # Login/logout views
│   │   ├── serializers.py        # User serializers
│   │   └── urls.py
│   ├── hostel/                    # Hostel & room management
│   │   ├── models.py             # Block, Room, RoomAllocation
│   │   ├── views.py              # Hostel views
│   │   ├── serializers.py        # Hostel serializers
│   │   └── urls.py
│   ├── mess/                      # Mess management
│   │   ├── models.py             # MessBill, MessMenu, Registration
│   │   ├── views.py              # Mess views
│   │   ├── tasks.py              # Celery tasks for billing
│   │   └── urls.py
│   ├── students/                  # Student management
│   │   ├── models.py             # Student model
│   │   ├── views.py              # Student CRU operations
│   │   └── urls.py
│   ├── complaints/                # Complaint management
│   │   ├── models.py             # Complaint model
│   │   ├── views.py              # Complaint views
│   │   └── urls.py
│   ├── dashboard/                 # Dashboard & analytics
│   │   ├── views.py              # Dashboard view + health check
│   │   └── urls.py
│   ├── api/                       # API viewsets & serializers
│   │   ├── serializers.py        # API serializers
│   │   ├── viewsets.py           # API viewsets
│   │   ├── urls.py               # API routing
│   │   ├── tests.py              # API tests
│   │   └── test_celery_tasks.py  # Celery task tests
│
├── hostel_management/             # Django project settings
│   ├── settings.py               # Development settings
│   ├── settings_production.py    # Production settings (for Docker)
│   ├── urls.py                   # Main URL routing
│   ├── wsgi.py                   # Production WSGI app
│   ├── asgi.py                   # Production ASGI app
│   └── celery.py                 # Celery configuration
│
├── templates/                     # HTML templates
│   ├── base.html                 # Base template
│   ├── accounts/                 # Login, profile templates
│   ├── hostel/                   # Room allocation templates
│   ├── mess/                     # Billing templates
│   ├── students/                 # Student templates
│   ├── complaints/               # Complaint templates
│   └── dashboard/                # Dashboard templates
│
├── static/                        # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
│
├── Dockerfile                     # Docker image definition
├── docker-compose.yml            # Docker services orchestration
├── nginx.conf                    # Production nginx config (SSL)
├── nginx_testing.conf            # Testing nginx config (HTTP only)
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables
├── .env.example                  # Environment template
├── manage.py                     # Django management script
├── db.sqlite3                    # Development database
└── README.md                     # This file

```

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- Docker & Docker Compose (for containerized setup)
- PostgreSQL 12+ (for production)
- Redis (for caching & Celery broker)

### Local Development Setup

1. **Clone repository**
```bash
git clone <repo-url>
cd hostel_management
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

8. **Run development server**
```bash
python manage.py runserver
```

---

## Running the Project

### Development (Local)
```bash
# Terminal 1: Django development server
python manage.py runserver

# Terminal 2: Celery worker (in another terminal)
celery -A hostel_management worker -l info

# Terminal 3: Celery beat scheduler
celery -A hostel_management beat -l info
```

### Production (Docker - Recommended)
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
docker-compose logs -f celery_worker

# Stop services
docker-compose down
```

### Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Django Admin | `http://localhost/admin/` | Manage database |
| API Root | `http://localhost/api/` | API endpoint |
| Swagger UI | `http://localhost/api/docs/` | API documentation |
| ReDoc | `http://localhost/api/redoc/` | Alternative API docs |
| Health Check | `http://localhost/health/` | Service status |

---

## Database & Models

### Core Models

**User (Django built-in)**
- Extends Django's User model
- Used by Warden, Superuser, Student accounts

**Student**
```python
- registration_no: Unique ID
- user: ForeignKey(User)
- phone: Contact number
- is_active: Status
- room_allocation: One-to-one with RoomAllocation
```

**Block**
```python
- name: Block identifier (A, B, C, etc)
- floor_count: Number of floors
- warden: ForeignKey(User) - Warden assigned
- is_active: Operational status
```

**Room**
```python
- room_no: Room identifier
- block: ForeignKey(Block)
- capacity: Max occupants
- status: Available/Occupied
- assigned_to_warden: ForeignKey(User)
```

**RoomAllocation**
```python
- student: ForeignKey(Student)
- room: ForeignKey(Room)
- allocated_date: Assignment date
- vacate_date: Checkout date (if any)
- status: Active/Vacated
```

**MessBill**
```python
- student: ForeignKey(Student)
- month: Billing month
- amount: Bill amount
- status: Pending/Paid
```

**Complaint**
```python
- student: ForeignKey(Student)
- title: Issue title
- description: Issue details
- category: Type of complaint
- status: Pending/Resolved
- created_at: Report time
```

---

## API Endpoints

### Authentication
```
POST   /api/auth/login/          - Get JWT token
POST   /api/auth/logout/         - Logout user
POST   /api/auth/refresh/        - Refresh JWT token
```

### Students
```
GET    /api/students/            - List all students
POST   /api/students/            - Create new student
GET    /api/students/{id}/       - Get student details
PUT    /api/students/{id}/       - Update student
DELETE /api/students/{id}/       - Delete student
```

### Hostel Management
```
GET    /api/blocks/              - List all blocks
POST   /api/blocks/              - Create new block
GET    /api/blocks/{id}/         - Get block details
PUT    /api/blocks/{id}/         - Update block

GET    /api/rooms/               - List all rooms
POST   /api/rooms/               - Create new room
GET    /api/rooms/{id}/          - Get room details
PUT    /api/rooms/{id}/          - Update room

GET    /api/allocations/         - List room allocations
POST   /api/allocations/         - Create allocation
GET    /api/allocations/{id}/    - Get allocation
PUT    /api/allocations/{id}/    - Update allocation
```

### Mess Management
```
GET    /api/bills/               - List mess bills
POST   /api/bills/               - Create bill
GET    /api/bills/{id}/          - Get bill details
PUT    /api/bills/{id}/          - Update bill status

GET    /api/menu/                - View mess menu
POST   /api/menu/                - Update menu
```

### Complaints
```
GET    /api/complaints/          - List complaints
POST   /api/complaints/          - File complaint
GET    /api/complaints/{id}/     - Get complaint details
PUT    /api/complaints/{id}/     - Update complaint status
```

---

## Celery Background Tasks

### Configured Tasks

**Email Notifications**
```python
send_email_task.py
- Send room allocation confirmations
- Send account activation emails
- Send bill reminders
```

**Billing Tasks**
```python
generate_bill.py
- Auto-generate monthly mess bills
- Calculate charges
- Send payment reminders
```

**Scheduled Jobs (Django Celery Beat)**
```
Every month: Generate mess bills
Every day: Send payment reminders
Every week: Send activity digest
```

### Running Tasks

**Local Development**
```bash
# Worker
celery -A hostel_management worker -l info

# Beat Scheduler
celery -A hostel_management beat -l info

# Monitor tasks
celery -A hostel_management events
```

**Docker**
```bash
# Already running in containers
docker-compose ps  # Check status
docker logs hostel_celery_worker
docker logs hostel_celery_beat
```

---

## Docker Deployment

### Services

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache & Message Broker |
| Django | 8000 | Application server |
| Nginx | 80 | Web server |
| Celery Worker | - | Background tasks |
| Celery Beat | - | Task scheduler |

### Environment Variables (.env)

```bash
# Django Configuration
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=hostel_management
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Execute command in container
docker exec hostel_web python manage.py createsuperuser

# Rebuild images
docker-compose build --no-cache

# View running containers
docker-compose ps
```

---

## Testing

### Run Tests Locally

```bash
# All tests
pytest

# Specific test file
pytest apps/api/tests.py

# With coverage
pytest --cov=apps --cov-report=html

# Specific test class
pytest apps/api/tests.py::StudentAPITests

# Specific test method
pytest apps/api/tests.py::StudentAPITests::test_list_students
```

### Test Files

```
apps/api/tests.py              - API endpoint tests
apps/api/test_celery_tasks.py  - Celery task tests
apps/hostel/tests.py           - Hostel app tests
apps/mess/tests.py             - Mess management tests
apps/students/tests.py         - Student tests
```

### Running in Docker

```bash
docker exec hostel_web pytest
docker exec hostel_web pytest --cov=apps
```

---

## Admin Panel

### Access Admin
```
URL: http://localhost/admin/
Username: admin
Password: admin123
```

### Admin Capabilities

- ✅ Manage users, students, wardens
- ✅ Create/edit hostel blocks and rooms
- ✅ Manage room allocations
- ✅ Generate mess bills
- ✅ View complaints and feedback
- ✅ Configure site settings
- ✅ View Celery task results
- ✅ Manage periodic tasks

---

## Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Kill process using port
# Linux/Mac:
lsof -ti:80 | xargs kill -9

# Windows:
netstat -ano | findstr :80
taskkill /PID <PID> /F
```

**Database Connection Error**
```bash
# Check PostgreSQL is running
docker-compose logs db

# Verify credentials in .env
# Restart database
docker-compose restart db
```

**Celery Tasks Not Running**
```bash
# Check worker is running
docker-compose ps hostel_celery_worker

# View worker logs
docker logs hostel_celery_worker -f

# Restart worker
docker-compose restart celery_worker
```

**Migrations Not Applied**
```bash
# Apply migrations
docker exec hostel_web python manage.py migrate

# Check migration status
docker exec hostel_web python manage.py migrate --plan
```

**Static Files Not Loading**
```bash
# Collect static files
docker exec hostel_web python manage.py collectstatic --noinput

# Check volume mount in docker-compose.yml
```

### Reset Everything

```bash
# Container reset
docker-compose down -v

# Full restart
docker-compose up -d --build
```

---

## Development Workflow

### Creating New Features

1. **Create migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

2. **Add API endpoints**
- Create serializer in `apps/api/serializers.py`
- Create viewset in `apps/api/viewsets.py`
- Register in `apps/api/urls.py`

3. **Write tests**
- Add tests in respective `test_*.py` files
- Run: `pytest`

4. **Create templates** (if needed)
```bash
templates/<app_name>/<template_name>.html
```

### Deployment Checklist

- [ ] Update `settings_production.py`
- [ ] Set environment variables in `.env`
- [ ] Generate SSL certificates
- [ ] Run migrations: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Configure Nginx SSL
- [ ] Set up automated backups
- [ ] Configure email notifications
- [ ] Test all API endpoints
- [ ] Test background tasks
- [ ] Set up monitoring/logging

---

## Support & Documentation

- **Status Page**: `/health/`
- **API Docs**: `/api/docs/`
- **Admin Panel**: `/admin/`
- **GitHub**: [Repository Link]
- **Issues**: Report via GitHub Issues

**Last Updated**: March 30, 2026
**Version**: 3.0 (Production Ready)
