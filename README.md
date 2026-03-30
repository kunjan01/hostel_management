# Hostel Management System

A comprehensive Django REST Framework application for managing hostel operations with background tasks, REST API, and Docker containerization.

## 🚀 Quick Start

### Docker (Recommended)
```bash
docker-compose up -d
```
Access: `http://localhost` | Admin: `http://localhost/admin/`

### Local Development
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 📚 Documentation

**Complete documentation** is in **[PROJECT_SETUP.md](./PROJECT_SETUP.md)**

## 🎯 Key Features

- 👥 Student & hostel management
- 🏠 Room allocation system
- 🍽️ Mess billing automation
- 📝 Complaint management
- ⚡ Background tasks with Celery
- 🔐 JWT authentication
- 📊 RESTful API with Swagger
- 🐳 Docker containerization

## 📍 Quick Links

| Service | URL |
|---------|-----|
| 🔑 Admin Panel | `http://localhost/admin/` |
| 📖 API Docs | `http://localhost/api/docs/` |
| 💚 Health Check | `http://localhost/health/` |

## 🔌 API Quick Reference

Get started with the API:

```bash
# 1. Get access token
curl -X POST http://localhost/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# 2. Use token to access API
curl -X GET http://localhost/api/students/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Available Endpoints:**
- `POST /api/token/` - Get JWT token
- `GET/POST /api/students/` - Student management
- `GET/POST /api/blocks/` - Hostel blocks
- `GET/POST /api/rooms/` - Room management
- `GET/POST /api/allocations/` - Room allocations
- `GET/POST /api/mess-bills/` - Mess billing
- `GET/POST /api/mess-registrations/` - Mess registration
- `GET/POST /api/mess-menu/` - Mess menu

📚 **Complete API examples:** [API_EXAMPLES.md](./API_EXAMPLES.md) with curl commands

### First Time Setup
After starting the application, create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
# Or locally:
python manage.py createsuperuser
```

Then login to Admin Panel with your new credentials.

## 🔧 Tech Stack

- Django 4.2.11 | REST Framework 3.15.0
- PostgreSQL 15 | Redis 7 | Celery 5.3.4
- Docker + Nginx | Gunicorn

---

**See [PROJECT_SETUP.md](./PROJECT_SETUP.md) for complete documentation → Installation, API, Database, Testing, Deployment**

**Status**: ✅ Production Ready | **Version**: 3.0
