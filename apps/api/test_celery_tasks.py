"""
Unit tests for Celery background tasks

Run tests with: pytest apps/api/test_celery_tasks.py -v
Or with coverage: pytest apps/api/test_celery_tasks.py --cov=apps.api.tasks
"""

import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from unittest.mock import patch, MagicMock
from celery.result import EagerResult

from apps.api.tasks import (
    generate_mess_bills_task,
    generate_room_bills_task,
    send_overdue_bill_reminders_task,
    send_payment_reminder_task,
    send_overdue_reminder_email,
    send_payment_reminder_email,
    send_bill_generated_email,
    cleanup_old_results_task,
    test_task,
)
from apps.mess.models import MessBill
from apps.hostel.models import RoomBill
from apps.students.models import Student


pytestmark = pytest.mark.django_db


class TestBillingTasks:
    """Test automatic bill generation tasks"""
    
    def test_generate_mess_bills_task(self):
        """Test mess bill generation task"""
        with patch('apps.api.tasks.BillService') as mock_service:
            mock_instance = MagicMock()
            mock_instance.generate_mess_bills.return_value = {
                'created': 5,
                'skipped': 2,
            }
            mock_service.return_value = mock_instance
            
            result = generate_mess_bills_task()
            
            assert result['status'] == 'success'
            assert result['bill_count'] == 5
            mock_instance.generate_mess_bills.assert_called_once()
    
    def test_generate_mess_bills_task_error(self):
        """Test mess bill generation with error"""
        with patch('apps.api.tasks.BillService') as mock_service:
            mock_instance = MagicMock()
            mock_instance.generate_mess_bills.side_effect = Exception("DB Error")
            mock_service.return_value = mock_instance
            
            result = generate_mess_bills_task()
            
            assert result['status'] == 'error'
            assert 'DB Error' in result['message']
    
    def test_generate_room_bills_task(self):
        """Test room bill generation task"""
        with patch('apps.api.tasks.BillService') as mock_service:
            mock_instance = MagicMock()
            mock_instance.generate_room_bills.return_value = {
                'created': 10,
                'skipped': 1,
            }
            mock_service.return_value = mock_instance
            
            result = generate_room_bills_task()
            
            assert result['status'] == 'success'
            assert result['bill_count'] == 10
            mock_instance.generate_room_bills.assert_called_once()


class TestNotificationTasks:
    """Test email notification tasks"""
    
    @patch('apps.api.tasks.send_mail')
    def test_send_overdue_reminder_email(self, mock_send_mail, student_factory):
        """Test sending overdue reminder email"""
        student = student_factory()
        
        result = send_overdue_reminder_email(student.id)
        
        assert result['status'] == 'success'
        assert result['student'] == student.name
        mock_send_mail.assert_called_once()
        
        # Verify email details
        call_args = mock_send_mail.call_args
        assert 'Overdue' in call_args[1]['subject']
        assert student.email in call_args[1]['recipient_list']
    
    @patch('apps.api.tasks.send_mail')
    def test_send_payment_reminder_email(self, mock_send_mail, student_factory):
        """Test sending payment reminder email"""
        student = student_factory()
        
        result = send_payment_reminder_email(student.id)
        
        assert result['status'] == 'success'
        assert result['student'] == student.name
        mock_send_mail.assert_called_once()
        
        # Verify email details
        call_args = mock_send_mail.call_args
        assert 'Billing' in call_args[1]['subject']
        assert student.email in call_args[1]['recipient_list']
    
    @patch('apps.api.tasks.send_mail')
    def test_send_bill_generated_email(self, mock_send_mail, student_factory, mess_bill_factory):
        """Test bill generated notification email"""
        student = student_factory()
        bill = mess_bill_factory(student=student, month=3, year=2024)
        
        result = send_bill_generated_email(student.id, 'mess', 3, 2024)
        
        assert result['status'] == 'success'
        assert result['student'] == student.name
        mock_send_mail.assert_called_once()
    
    @patch('apps.api.tasks.send_mail')
    def test_send_overdue_reminder_email_not_found(self, mock_send_mail):
        """Test sending email for non-existent student"""
        result = send_overdue_reminder_email(9999)
        
        assert result['status'] == 'error'
        mock_send_mail.assert_not_called()
    
    def test_send_overdue_bill_reminders_task(self, student_factory, mess_bill_factory):
        """Test overdue reminders collection task"""
        student1 = student_factory()
        student2 = student_factory()
        
        # Create overdue bills
        threshold_date = timezone.now().date() - timedelta(days=8)
        mess_bill_factory(
            student=student1,
            status='Pending',
            due_date=threshold_date
        )
        mess_bill_factory(
            student=student2,
            status='Pending',
            due_date=threshold_date
        )
        
        with patch('apps.api.tasks.send_overdue_reminder_email') as mock_task:
            result = send_overdue_bill_reminders_task()
            
            assert result['status'] == 'success'
            assert result['reminders_sent'] >= 0
    
    def test_send_payment_reminder_task(self):
        """Test payment reminder collection task"""
        with patch('apps.api.tasks.send_payment_reminder_email') as mock_task:
            result = send_payment_reminder_task()
            
            assert result['status'] == 'success'
            assert 'reminders_sent' in result


class TestMaintenanceTasks:
    """Test maintenance and cleanup tasks"""
    
    def test_cleanup_old_results_task(self):
        """Test cleanup of old task results"""
        with patch('apps.api.tasks.TaskResult.objects.filter') as mock_filter:
            mock_queryset = MagicMock()
            mock_filter.return_value = mock_queryset
            mock_queryset.delete.return_value = (5, {'django_celery_results.TaskResult': 5})
            
            result = cleanup_old_results_task()
            
            assert result['status'] == 'success'
            assert result['deleted'] == 5
    
    def test_cleanup_old_results_task_error(self):
        """Test cleanup task error handling"""
        with patch('apps.api.tasks.TaskResult') as mock_model:
            mock_model.objects.filter.side_effect = Exception("DB Error")
            
            result = cleanup_old_results_task()
            
            assert result['status'] == 'error'
            assert 'DB Error' in result['message']


class TestDebugTasks:
    """Test debug and utility tasks"""
    
    def test_task(self):
        """Test simple test task"""
        result = test_task(message="Test message")
        
        assert result['status'] == 'success'
        assert result['message'] == "Test message"
    
    def test_task_default_message(self):
        """Test task with default message"""
        result = test_task()
        
        assert result['status'] == 'success'
        assert 'Hello from Celery' in result['message']


class TestTaskScheduling:
    """Test task scheduling configuration"""
    
    def test_celery_beat_schedule_exists(self):
        """Verify beat schedule is configured"""
        from hostel_management.celery import app
        
        assert hasattr(app.conf, 'beat_schedule')
        schedule = app.conf.beat_schedule
        
        # Verify key scheduled tasks
        assert 'generate_monthly_mess_bills' in schedule
        assert 'generate_monthly_room_bills' in schedule
        assert 'send_overdue_reminders' in schedule
        assert 'send_payment_reminders' in schedule
    
    def test_scheduled_task_config(self):
        """Verify scheduled task configuration"""
        from hostel_management.celery import app
        
        schedule = app.conf.beat_schedule
        
        # Check mess bills task
        mess_task = schedule['generate_monthly_mess_bills']
        assert mess_task['task'] == 'apps.api.tasks.generate_mess_bills_task'
        assert 'schedule' in mess_task
        assert mess_task['options']['queue'] == 'default'


class TestTaskIntegration:
    """Integration tests for task workflows"""
    
    @patch('apps.api.tasks.BillService')
    @patch('apps.api.tasks.send_mail')
    def test_bill_generation_workflow(self, mock_mail, mock_service):
        """Test complete billing workflow"""
        # Setup
        mock_service_instance = MagicMock()
        mock_service_instance.generate_mess_bills.return_value = {'created': 5, 'skipped': 0}
        mock_service.return_value = mock_service_instance
        
        # Generate bills
        result = generate_mess_bills_task()
        assert result['status'] == 'success'
        
        # Verify service was called
        mock_service_instance.generate_mess_bills.assert_called_once()
    
    def test_multiple_tasks_independent(self):
        """Verify tasks can run independently"""
        results = []
        
        # Run multiple tasks
        result1 = test_task("Task 1")
        result2 = test_task("Task 2")
        result3 = test_task("Task 3")
        
        assert result1['message'] == "Task 1"
        assert result2['message'] == "Task 2"
        assert result3['message'] == "Task 3"


# ========================
# Pytest Fixtures
# ========================

@pytest.fixture
def student_factory():
    """Factory for creating test students"""
    from apps.students.models import Student
    
    def create_student(**kwargs):
        data = {
            'enrollment_no': f'ENC{Student.objects.count() + 1:03d}',
            'name': f'Test Student {Student.objects.count() + 1}',
            'email': f'student{Student.objects.count() + 1}@test.com',
            'phone': '9876543210',
            'gender': 'M',
            'date_of_birth': datetime(2000, 1, 1),
            'city': 'Test City',
            'state': 'Test State',
            'branch': 'CSE',
            'course': 'BTech',
            'year': 2,
        }
        data.update(kwargs)
        return Student.objects.create(**data)
    
    return create_student


@pytest.fixture
def mess_bill_factory():
    """Factory for creating test mess bills"""
    from apps.mess.models import MessBill
    
    def create_bill(**kwargs):
        if 'student' not in kwargs:
            from django.contrib.auth.models import User
            user = User.objects.create_user('testuser', 'test@test.com', 'password')
            from apps.students.models import Student
            kwargs['student'] = Student.objects.create(
                enrollment_no='TEST001',
                name='Test',
                email='test@test.com',
                phone='9876543210',
                user=user,
            )
        
        data = {
            'month': timezone.now().month,
            'year': timezone.now().year,
            'amount': 5000.00,
            'status': 'Pending',
            'due_date': timezone.now().date() + timedelta(days=15),
        }
        data.update(kwargs)
        return MessBill.objects.create(**data)
    
    return create_bill


# ========================
# Running the Tests
# ========================

# To run these tests:
# pytest apps/api/test_celery_tasks.py -v
# 
# With coverage:
# pytest apps/api/test_celery_tasks.py --cov=apps.api.tasks --cov-report=html
#
# Run specific test:
# pytest apps/api/test_celery_tasks.py::TestBillingTasks::test_generate_mess_bills_task -v
