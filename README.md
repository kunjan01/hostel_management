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

**Credentials**: Username: `admin` | Password: `admin123`

## 🔧 Tech Stack

- Django 4.2.11 | REST Framework 3.15.0
- PostgreSQL 15 | Redis 7 | Celery 5.3.4
- Docker + Nginx | Gunicorn

---

**See [PROJECT_SETUP.md](./PROJECT_SETUP.md) for complete documentation → Installation, API, Database, Testing, Deployment**

**Status**: ✅ Production Ready | **Version**: 3.0
