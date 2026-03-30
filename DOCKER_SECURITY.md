# 🔒 Docker Security & Production Configuration

Complete guide to production-ready Docker deployment for Hostel Management System.

---

## 📋 Security Fixes Applied

### ✅ Issue 1: curl Installed in Runtime
- **Problem**: docker-compose.yml healthcheck used `curl` but it wasn't installed
- **Solution**: Added `curl` to Dockerfile runtime dependencies
- **Status**: ✅ FIXED

### ✅ Issue 2: Source Code Volume Mount Removed from Production
- **Problem**: `.:/app` mounted source code in container, allowing live edits
- **Solution**: Removed live volume mount; now commented as development-only
- **Risk**: In production, any changes to local disk immediately affect running container
- **Status**: ✅ FIXED - Volume mount is now commented out

### ✅ Issue 3: Celery Services Proper Health Dependencies
- **Problem**: Celery services didn't depend on healthy db/redis
- **Solution**: Updated `depends_on` to use health conditions:
  ```yaml
  depends_on:
    db:
      condition: service_healthy
    redis:
      condition: service_healthy
  ```
- **Status**: ✅ FIXED

### ✅ Issue 4: SECRET_KEY Validation Enforced
- **Problem**: If SECRET_KEY env var missing, app used weak default "change-me-in-production"
- **Solution**: Added validation in `settings_production.py` to FAIL if SECRET_KEY not set
- **Result**: App will crash on startup with clear error message
- **Status**: ✅ FIXED

### ✅ Issue 5: Database Password Consistency
- **Problem**: docker-compose.yml defaulted to "postgres" but .env.example showed "your-secure-password"
- **Solution**: Standardized all defaults to "your-secure-password"
- **Locations Fixed**:
  - `db.POSTGRES_PASSWORD`
  - Web service `DATABASE_URL`
  - celery_worker `DATABASE_URL`
  - celery_beat `DATABASE_URL`
- **Status**: ✅ FIXED

---

## 🚀 Production Deployment Guide

### Step 1: Create Production .env File

```bash
# On your production server
cd /opt/hostel_management
nano .env
```

Fill in all required values:

```env
# Core Settings
DEBUG=False
SECRET_KEY=your-super-secret-random-string-min-50-chars
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=hostel_management_prod
DB_USER=hostel_db_user
DB_PASSWORD=your-very-secure-password-min-20-chars
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Email (Change from Console to SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
EMAIL_USE_TLS=True

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Step 2: Build Production Image

```bash
docker-compose build
```

### Step 3: Start Services

```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f web

# Verify health
docker-compose ps
```

Expected output:
```
STATUS                  PORTS
Up 2 minutes (healthy)  0.0.0.0:5432->5432/tcp
Up 2 minutes (healthy)  0.0.0.0:6379->6379/tcp
Up 2 minutes (healthy)  0.0.0.0:8000->8000/tcp
Up 2 minutes            
Up 2 minutes            
Up 2 minutes (healthy)  0.0.0.0:80->80/tcp
```

### Step 4: Create Superuser (First Time Only)

```bash
docker-compose exec web python manage.py createsuperuser
```

### Step 5: Verify Deployment

```bash
# Test health endpoint
curl -f http://localhost/health/

# Test API
curl -X POST http://localhost/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# View admin panel
# Visit: http://yourdomain.com/admin/
```

---

## 🔐 Security Checklist

### Environment Variables
- [ ] `SECRET_KEY` is set and >50 characters
- [ ] `DB_PASSWORD` is set and >20 characters
- [ ] `EMAIL_HOST_PASSWORD` is app-specific (not main password)
- [ ] All credentials are in `.env` (never in code/git)
- [ ] `.env` file has proper permissions: `chmod 600 .env`

### Docker
- [ ] Image uses non-root user (`appuser`)
- [ ] Health checks are passing (all `Up ... (healthy)`)
- [ ] Source code volume mount is commented out (production only)
- [ ] Celery services depend on healthy db/redis

### Django
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] `SECURE_SSL_REDIRECT=True` if using HTTPS
- [ ] `SECRET_KEY` is randomly generated, not "change-me"

### Database
- [ ] PostgreSQL uses strong password
- [ ] Database has backups configured
- [ ] Migrations have run successfully

### Email
- [ ] Email backend is SMTP, not console
- [ ] SMTP credentials are correct
- [ ] Test email sending works

---

## 🛠️ Development Setup vs Production

### Development (docker-compose.yml)

```yaml
web:
  volumes:
    - .:/app              # Live code mounting for development
    - static_volume:/app/staticfiles
  environment:
    - DEBUG=True          # Show detailed errors
    - SECRET_KEY=...      # Can use development key
    - EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend  # Print emails
```

### Production (Same file, different .env)

```yaml
web:
  volumes:
    # Source code NOT mounted - uses image build only
    - static_volume:/app/staticfiles
  environment:
    - DEBUG=False         # Hide errors from users
    - SECRET_KEY=...      # Must be set securely
    - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend  # Send real emails
```

**Key Difference**: Remove the `.:/app` volume mount line in production by ensuring it's commented out.

---

## 📊 Health Check Status

All services have health checks:

### PostgreSQL
```bash
Command: pg_isready -U postgres
Interval: 10s | Timeout: 5s | Retries: 5
```

### Redis
```bash
Command: redis-cli ping
Interval: 10s | Timeout: 5s | Retries: 5
```

### Django Web
```bash
Command: curl -f http://localhost:8000/health/
Interval: 30s | Timeout: 10s | Retries: 3
```

### Nginx
```bash
Command: wget --quiet --tries=1 --spider http://localhost/health/
Interval: 30s | Timeout: 10s | Retries: 3
```

Monitor health:
```bash
# Watch health status in real-time
docker-compose ps --format "{{.Service}} - {{.Status}}"
```

---

## 🚨 Troubleshooting Production Issues

### Issue: SECRET_KEY Error on Startup
```
ValueError: ⚠️  CRITICAL: SECRET_KEY environment variable is not set.
```

**Solution**: Add `SECRET_KEY=<your-secret>` to `.env` file

### Issue: Database Connection Failed
```
operational error (psycopg2.OperationalError) could not connect to server
```

**Solution**: Verify database credentials in `.env`:
```bash
# Test connection manually
docker-compose exec db psql -U postgres -c "SELECT 1"
```

### Issue: Health Check Failing
```
web service restarting (exit code 1)
```

**Solution**: Check logs:
```bash
docker-compose logs web
```

### Issue: Email Not Sending
```
SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```

**Solutions**:
1. Use app-specific password (for Gmail)
2. Enable "Less secure app access" (deprecated)
3. Check `EMAIL_USE_TLS=True`

---

## 🔄 Updating Production

### Deploy New Code

```bash
# Stop current services
docker-compose down

# Update code (git pull)
git pull origin main

# Rebuild image
docker-compose build

# Start services
docker-compose up -d

# Apply migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check status
docker-compose ps
```

### Backup Database Before Updating

```bash
# Create backup
docker-compose exec db pg_dump -U postgres hostel_management_prod > backup-$(date +%Y%m%d).sql

# Restore from backup if needed
docker-compose exec -T db psql -U postgres hostel_management_prod < backup-20240115.sql
```

---

## 📈 Monitoring

### View Real-time Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web   # Django app
docker-compose logs -f db    # Database

# Last 100 lines
docker-compose logs --tail=100 celery_worker
```

### Check Resource Usage

```bash
# CPU and memory usage
docker stats
```

### Monitor Celery Tasks

```bash
# Check Celery status
docker-compose exec celery_worker celery -A hostel_management inspect active

# Purge failed tasks
docker-compose exec celery_worker celery -A hostel_management purge
```

---

## 🔐 SSL/HTTPS Setup (Beyond Scope)

For HTTPS production:
1. Obtain certificate from Let's Encrypt
2. Update nginx configuration
3. Mount certificates as volumes
4. Set `SECURE_SSL_REDIRECT=True`
5. Update ALLOWED_HOSTS to use HTTPS URLs

---

## ✅ Production Ready Checklist

- [ ] All environment variables set in `.env`
- [ ] `SECRET_KEY` is cryptographically secure
- [ ] Database password is strong
- [ ] Email SMTP credentials configured
- [ ] All health checks passing
- [ ] Source code volume mount commented out
- [ ] DEBUG=False
- [ ] SECURE_SSL_REDIRECT=True (if HTTPS)
- [ ] Backups configured
- [ ] Logging configured
- [ ] Monitoring setup
- [ ] SSL certificate obtained (if HTTPS)

---

**For more information see:**
- [Project Setup](./PROJECT_SETUP.md)
- [API Endpoints](./API_EXAMPLES.md)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Django Deployment](https://docs.djangoproject.com/en/4.2/howto/deployment/)
