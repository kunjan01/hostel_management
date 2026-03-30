"""
Background tasks for Hostel Management System

These tasks are executed asynchronously using Celery and Redis.
They handle billing, notifications, and maintenance operations.

Task Categories:
    - Billing: Automatic bill generation
    - Notifications: Email alerts and reminders
    - Maintenance: Cleanup and reporting
"""

from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from .serializers import StudentBillSummarySerializer
from apps.services.billing_service import BillGenerationService
from apps.students.models import Student
from apps.mess.models import MessBill, MessRegistration
from apps.hostel.models import RoomBill, RoomAllocation
import logging

logger = logging.getLogger(__name__)


# ========================
# BILLING TASKS
# ========================

@shared_task(name='apps.api.tasks.generate_mess_bills_task', queue='default')
def generate_mess_bills_task():
    """
    Automatically generate mess bills for the current month.
    
    This task:
    - Generates bills for all registered mess students
    - Runs on the 1st of every month at 00:00
    - Returns summary of created and skipped bills
    
    Returns:
        dict: Status of bill generation
    """
    try:
        logger.info("Starting automatic mess bill generation task")
        service = BillGenerationService()
        
        today = timezone.now()
        result = service.generate_mess_bills(month=today.month, year=today.year)
        
        logger.info(f"Mess bills generated: {result['created']}, Skipped: {result['skipped']}")
        return {
            'status': 'success',
            'message': f"Generated {result['created']} mess bills, skipped {result['skipped']}",
            'bill_count': result['created'],
        }
    except Exception as e:
        logger.error(f"Error in generate_mess_bills_task: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': f"Failed to generate mess bills: {str(e)}",
        }


@shared_task(name='apps.api.tasks.generate_room_bills_task', queue='default')
def generate_room_bills_task():
    """
    Automatically generate room bills for the current month.
    
    This task:
    - Generates room rent bills for all allocated students
    - Runs on the 1st of every month at 00:30
    - Returns summary of created and skipped bills
    
    Returns:
        dict: Status of bill generation
    """
    try:
        logger.info("Starting automatic room bill generation task")
        service = BillGenerationService()
        
        today = timezone.now()
        result = service.generate_room_bills(month=today.month, year=today.year)
        
        logger.info(f"Room bills generated: {result['created']}, Skipped: {result['skipped']}")
        return {
            'status': 'success',
            'message': f"Generated {result['created']} room bills, skipped {result['skipped']}",
            'bill_count': result['created'],
        }
    except Exception as e:
        logger.error(f"Error in generate_room_bills_task: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': f"Failed to generate room bills: {str(e)}",
        }


# ========================
# NOTIFICATION TASKS
# ========================

@shared_task(name='apps.api.tasks.send_overdue_bill_reminders_task', queue='default')
def send_overdue_bill_reminders_task():
    """
    Send email reminders for overdue bills.
    
    This task:
    - Finds all students with overdue bills (overdue > 7 days)
    - Sends personalized email reminders
    - Runs every day at 09:00 AM
    - Tracks email delivery status
    
    Returns:
        dict: Count of reminders sent and any errors
    """
    try:
        logger.info("Starting overdue bill reminders task")
        
        # Get date threshold (7 days ago)
        threshold_date = timezone.now().date() - timedelta(days=7)
        
        # Find overdue bills
        overdue_mess_bills = MessBill.objects.filter(
            status='Pending',
            due_date__lt=threshold_date
        ).select_related('student', 'student__user')
        
        overdue_room_bills = RoomBill.objects.filter(
            status='Pending',
            due_date__lt=threshold_date
        ).select_related('student', 'student__user')
        
        # Collect unique students with overdue bills
        student_ids = set()
        student_ids.update(overdue_mess_bills.values_list('student_id', flat=True))
        student_ids.update(overdue_room_bills.values_list('student_id', flat=True))
        
        reminders_sent = 0
        for student_id in student_ids:
            try:
                student = Student.objects.get(id=student_id)
                send_overdue_reminder_email.delay(student_id)
                reminders_sent += 1
            except Exception as e:
                logger.error(f"Error sending reminder to student {student_id}: {str(e)}")
        
        logger.info(f"Overdue reminders task completed. Sent: {reminders_sent}")
        return {
            'status': 'success',
            'reminders_sent': reminders_sent,
        }
    except Exception as e:
        logger.error(f"Error in send_overdue_bill_reminders_task: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e),
        }


@shared_task(name='apps.api.tasks.send_payment_reminder_task', queue='default')
def send_payment_reminder_task():
    """
    Send payment reminders on the 15th of every month.
    
    This task:
    - Sends reminders to students with pending bills
    - Includes bill summaries
    - Provides payment instructions
    - Runs on 15th of every month at 10:00 AM
    
    Returns:
        dict: Count of reminders sent
    """
    try:
        logger.info("Starting payment reminder task")
        
        # Get students with pending bills
        students_with_bills = Student.objects.filter(
            messregistration__isnull=False
        ).distinct()
        
        reminders_sent = 0
        for student in students_with_bills[:100]:  # Limit to 100 at a time
            try:
                pending_count = MessBill.objects.filter(
                    student=student,
                    status='Pending'
                ).count()
                
                if pending_count > 0:
                    send_payment_reminder_email.delay(student.id)
                    reminders_sent += 1
            except Exception as e:
                logger.error(f"Error sending payment reminder to {student.id}: {str(e)}")
        
        logger.info(f"Payment reminders sent: {reminders_sent}")
        return {
            'status': 'success',
            'reminders_sent': reminders_sent,
        }
    except Exception as e:
        logger.error(f"Error in send_payment_reminder_task: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e),
        }


@shared_task(name='apps.api.tasks.send_overdue_reminder_email', queue='default')
def send_overdue_reminder_email(student_id):
    """
    Send overdue bill reminder email to a specific student.
    
    A lightweight task called by the main reminder task.
    """
    try:
        student = Student.objects.get(id=student_id)
        
        # Get bill summary
        serializer = StudentBillSummarySerializer(
            {'student': student}
        )
        summary = serializer.data
        
        # Prepare email context
        context = {
            'student_name': student.name,
            'enrollment_no': student.enrollment_no,
            'overdue_days': 7,
            'bill_summary': summary.get('bill_summary', {}),
            'contact_email': 'hostel@example.com',
        }
        
        # Send email
        subject = f'Overdue Bill Reminder - {student.name}'
        html_message = render_to_string('emails/overdue_reminder.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email='noreply@hostelmanagement.com',
            recipient_list=[student.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Overdue reminder sent to {student.email}")
        return {'status': 'success', 'student': student.name}
    
    except Exception as e:
        logger.error(f"Error sending overdue reminder email: {str(e)}", exc_info=True)
        return {'status': 'error', 'message': str(e)}


@shared_task(name='apps.api.tasks.send_payment_reminder_email', queue='default')
def send_payment_reminder_email(student_id):
    """
    Send payment reminder email to a specific student.
    """
    try:
        student = Student.objects.get(id=student_id)
        
        # Get pending bills
        mess_bills = MessBill.objects.filter(
            student=student,
            status='Pending'
        )[:5]
        
        room_bills = RoomBill.objects.filter(
            student=student,
            status='Pending'
        )[:5]
        
        context = {
            'student_name': student.name,
            'enrollment_no': student.enrollment_no,
            'mess_bills_count': mess_bills.count(),
            'room_bills_count': room_bills.count(),
            'total_pending': sum(b.amount for b in mess_bills) + sum(b.amount for b in room_bills),
            'contact_email': 'hostel@example.com',
            'payment_portal_url': 'http://localhost:8000/payments/',
        }
        
        # Send email
        subject = f'Monthly Billing Reminder - {student.name}'
        html_message = render_to_string('emails/payment_reminder.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email='noreply@hostelmanagement.com',
            recipient_list=[student.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Payment reminder sent to {student.email}")
        return {'status': 'success', 'student': student.name}
    
    except Exception as e:
        logger.error(f"Error sending payment reminder email: {str(e)}", exc_info=True)
        return {'status': 'error', 'message': str(e)}


@shared_task(name='apps.api.tasks.send_bill_generated_email', queue='default', bind=True)
def send_bill_generated_email(self, student_id, bill_type, month, year):
    """
    Send notification email when a bill is generated.
    
    This task:
    - Notifies student of new bill
    - Includes bill details
    - Provides payment link
    
    Args:
        student_id: ID of the student
        bill_type: 'mess' or 'room'
        month: Month number
        year: Year
    """
    try:
        student = Student.objects.get(id=student_id)
        
        # Get the bill based on type
        if bill_type == 'mess':
            bill = MessBill.objects.filter(
                student=student,
                month=month,
                year=year
            ).first()
        else:
            bill = RoomBill.objects.filter(
                student=student,
                month=month,
                year=year
            ).first()
        
        if not bill:
            logger.warning(f"Bill not found for student {student_id}, type {bill_type}")
            return {'status': 'error', 'message': 'Bill not found'}
        
        month_name = datetime(year, month, 1).strftime('%B')
        
        context = {
            'student_name': student.name,
            'bill_type': bill_type.title(),
            'month': month_name,
            'year': year,
            'amount': bill.amount,
            'due_date': bill.due_date,
            'bill_id': bill.id,
            'contact_email': 'hostel@example.com',
        }
        
        # Send email
        subject = f'{bill_type.title()} Bill Generated - {month_name} {year}'
        html_message = render_to_string('emails/bill_generated.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email='noreply@hostelmanagement.com',
            recipient_list=[student.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Bill generated email sent to {student.email}")
        return {'status': 'success', 'student': student.name}
    
    except Exception as e:
        logger.error(f"Error sending bill generated email: {str(e)}", exc_info=True)
        # Retry up to 3 times with exponential backoff
        self.retry(exc=e, countdown=60, max_retries=3)


# ========================
# MAINTENANCE TASKS
# ========================

@shared_task(name='apps.api.tasks.cleanup_old_results_task', queue='default')
def cleanup_old_results_task():
    """
    Cleanup and delete old task results from database.
    
    This task:
    - Deletes task results older than 7 days
    - Frees up database space
    - Runs weekly on Sunday at 02:00 AM
    
    Returns:
        dict: Count of deleted records
    """
    try:
        logger.info("Starting cleanup of old task results")
        
        # Import here to avoid circular imports
        from django_celery_results.models import TaskResult
        
        # Calculate date threshold (7 days ago)
        threshold_date = timezone.now() - timedelta(days=7)
        
        # Delete old results
        deleted_count, _ = TaskResult.objects.filter(
            date_done__lt=threshold_date
        ).delete()
        
        logger.info(f"Deleted {deleted_count} old task results")
        return {
            'status': 'success',
            'deleted': deleted_count,
        }
    except Exception as e:
        logger.error(f"Error in cleanup_old_results_task: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e),
        }


@shared_task(name='apps.api.tasks.send_admin_report_task', queue='default')
def send_admin_report_task():
    """
    Send daily admin report with hostel statistics.
    
    This task:
    - Collects hostel statistics
    - Generates summary report
    - Sends to admin email
    - Useful for monitoring system health
    
    Returns:
        dict: Status of report generation
    """
    try:
        logger.info("Generating admin report")
        
        from apps.hostel.models import Block, Room, RoomAllocation
        
        stats = {
            'total_students': Student.objects.count(),
            'total_blocks': Block.objects.count(),
            'total_rooms': Room.objects.count(),
            'occupied_rooms': RoomAllocation.objects.filter(status='Active').count(),
            'pending_bills': MessBill.objects.filter(status='Pending').count(),
            'overdue_bills': MessBill.objects.filter(
                status='Pending',
                due_date__lt=timezone.now().date()
            ).count(),
        }
        
        context = {
            'date': timezone.now().strftime('%Y-%m-%d'),
            'stats': stats,
        }
        
        # Send email to admin
        subject = f"Hostel Management System - Daily Report"
        html_message = render_to_string('emails/admin_report.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email='noreply@hostelmanagement.com',
            recipient_list=['admin@hostelmanagement.com'],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info("Admin report sent successfully")
        return {'status': 'success', 'stats': stats}
    
    except Exception as e:
        logger.error(f"Error in send_admin_report_task: {str(e)}", exc_info=True)
        return {'status': 'error', 'message': str(e)}


# ========================
# DEBUG TASK
# ========================

@shared_task(name='apps.api.tasks.test_task', queue='default')
def test_task(message="Hello from Celery!"):
    """
    Simple test task to verify Celery is working.
    
    Run this to test your Celery setup:
        from celery import current_app
        current_app.send_task('apps.api.tasks.test_task')
    """
    logger.info(f"Test task executed with message: {message}")
    return {'status': 'success', 'message': message}
