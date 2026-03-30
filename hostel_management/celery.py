"""
Celery configuration for Hostel Management System

This module initializes Celery and configures it to work with Django.
Celery is used for background task processing and scheduled jobs.

Usage:
    - Start worker: celery -A hostel_management worker -l info
    - Start beat scheduler: celery -A hostel_management beat -l info
    - Or use: python manage.py celery worker
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hostel_management.settings')

app = Celery('hostel_management')

# Load config from Django settings, all celery configuration should have a `CELERY_` prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Configure periodic tasks (scheduled jobs)
app.conf.beat_schedule = {
    # Generate mess bills on the 1st of every month at 00:00 (midnight)
    'generate_monthly_mess_bills': {
        'task': 'apps.api.tasks.generate_mess_bills_task',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),  # 1st of month at midnight
        'options': {'queue': 'default'}
    },
    # Generate room bills on the 1st of every month at 00:30
    'generate_monthly_room_bills': {
        'task': 'apps.api.tasks.generate_room_bills_task',
        'schedule': crontab(day_of_month=1, hour=0, minute=30),  # 1st of month at 00:30
        'options': {'queue': 'default'}
    },
    # Send overdue bill reminders every day at 09:00 AM (admin work time)
    'send_overdue_reminders': {
        'task': 'apps.api.tasks.send_overdue_bill_reminders_task',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9:00 AM
        'options': {'queue': 'default'}
    },
    # Send payment reminders on 15th of every month at 10:00 AM
    'send_payment_reminders': {
        'task': 'apps.api.tasks.send_payment_reminder_task',
        'schedule': crontab(day_of_month=15, hour=10, minute=0),  # 15th at 10:00 AM
        'options': {'queue': 'default'}
    },
    # Cleanup old task results every Sunday at 02:00 AM
    'cleanup_old_results': {
        'task': 'apps.api.tasks.cleanup_old_results_task',
        'schedule': crontab(day_of_week=6, hour=2, minute=0),  # Sunday at 2:00 AM
        'options': {'queue': 'default'}
    },
}

# Celery Configuration (will be loaded from settings.py)
# Format: CELERY_BROKER_URL, CELERY_RESULT_BACKEND, etc.

@app.task(bind=True)
def debug_task(self):
    """
    Debug task - useful for testing Celery setup
    
    Run this to verify Celery is working:
        from celery import current_app
        current_app.send_task('hostel_management.celery.debug_task')
    """
    print(f'Request: {self.request!r}')
    return 'Celery is working!'
