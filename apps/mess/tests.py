"""
Unit tests for billing services

Tests for BillGenerationService, BillPaymentService, and BillQueryService
"""

import datetime
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from apps.hostel.models import Block, Room, RoomAllocation, RoomBill
from apps.services.billing_service import (
    BillGenerationService,
    BillPaymentService,
    BillQueryService,
)
from apps.students.models import Student

from .models import MessBill, MessMenu, MessRegistration


@pytest.fixture
def student_user():
    """Create a test student user"""
    user = User.objects.create_user(username="student1", password="testpass123")
    return user


@pytest.fixture
def test_student(student_user):
    """Create a test student"""
    return Student.objects.create(
        user=student_user,
        enrollment_no="ENC001",
        name="John Doe",
        email="john@example.com",
        phone="9876543210",
        gender="M",
        date_of_birth="2000-01-15",
        blood_group="O+",
        course="BTech",
        year=2,
        branch="Computer Science",
        address="123 Main St",
        city="Mumbai",
        state="Maharashtra",
        parent_name="Jane Doe",
        parent_phone="9876543211",
    )


@pytest.fixture
def test_block():
    """Create a test block"""
    return Block.objects.create(
        name="Block A",
        block_type="Boys",
        floors=3,
        warden_name="Mr. Kumar",
        warden_phone="9876543210",
    )


@pytest.fixture
def test_room(test_block):
    """Create a test room"""
    return Room.objects.create(
        block=test_block,
        room_number="A101",
        floor=1,
        room_type="Double",
        capacity=2,
        monthly_rent=Decimal("3000.00"),
        status="Available",
    )


@pytest.fixture
def mess_registration(test_student):
    """Create a mess registration"""
    return MessRegistration.objects.create(
        student=test_student,
        plan="Full",
        monthly_charge=Decimal("3500.00"),
        is_active=True,
    )


@pytest.fixture
def room_allocation(test_student, test_room):
    """Create a room allocation"""
    return RoomAllocation.objects.create(
        student=test_student,
        room=test_room,
        status="Active",
    )


@pytest.mark.django_db
class TestBillGenerationService:
    """Test cases for BillGenerationService"""

    def test_generate_mess_bills(self, mess_registration):
        """Test generating mess bills"""
        result = BillGenerationService.generate_mess_bills(3, 2024)

        assert result["status"] == "success"
        assert result["created"] == 1
        assert result["skipped"] == 0

    def test_generate_mess_bills_duplicate(self, mess_registration):
        """Test generating mess bills twice"""
        result1 = BillGenerationService.generate_mess_bills(3, 2024)
        assert result1["created"] == 1

        result2 = BillGenerationService.generate_mess_bills(3, 2024)
        assert result2["created"] == 0
        assert result2["skipped"] == 1

    def test_generate_room_bills(self, room_allocation):
        """Test generating room bills"""
        result = BillGenerationService.generate_room_bills(3, 2024)

        assert result["status"] == "success"
        assert result["created"] == 1

    def test_generate_all_bills(self, mess_registration, room_allocation):
        """Test generating both bills"""
        result = BillGenerationService.generate_all_bills(3, 2024)

        assert result["status"] == "success"
        assert result["total_created"] == 2


@pytest.mark.django_db
class TestBillPaymentService:
    """Test cases for BillPaymentService"""

    def test_mark_mess_bill_paid(self, mess_registration):
        """Test marking a mess bill as paid"""
        BillGenerationService.generate_mess_bills(3, 2024)
        bill = MessBill.objects.first()

        success, message = BillPaymentService.mark_bill_paid(bill.id, bill_type="mess")

        assert success is True
        bill.refresh_from_db()
        assert bill.status == "Paid"

    def test_mark_bill_pending(self, mess_registration):
        """Test marking bill as pending"""
        BillGenerationService.generate_mess_bills(3, 2024)
        bill = MessBill.objects.first()

        BillPaymentService.mark_bill_paid(bill.id, bill_type="mess")
        success, msg = BillPaymentService.mark_bill_pending(bill.id, bill_type="mess")

        assert success is True
        bill.refresh_from_db()
        assert bill.status == "Pending"

    def test_bulk_mark_paid(self, mess_registration):
        """Test bulk marking bills as paid"""
        for month in range(1, 4):
            BillGenerationService.generate_mess_bills(month, 2024)

        bills = MessBill.objects.all()
        bill_ids = [b.id for b in bills]

        result = BillPaymentService.bulk_mark_paid(bill_ids, bill_type="mess")

        assert result["success"] == 3
        assert result["failed"] == 0


@pytest.mark.django_db
class TestCustomManagers:
    """Test cases for custom model managers"""

    def test_messbill_pending_manager(self, mess_registration):
        """Test MessBill.objects.pending()"""
        BillGenerationService.generate_mess_bills(3, 2024)
        pending_bills = MessBill.objects.pending()

        assert pending_bills.count() == 1

    def test_messbill_for_student_manager(self, mess_registration, test_student):
        """Test MessBill.objects.for_student()"""
        BillGenerationService.generate_mess_bills(3, 2024)
        student_bills = MessBill.objects.for_student(test_student)

        assert student_bills.count() == 1

    def test_messbill_for_month_manager(self, mess_registration):
        """Test MessBill.objects.for_month()"""
        for month in range(1, 4):
            BillGenerationService.generate_mess_bills(month, 2024)

        march_bills = MessBill.objects.for_month(3, 2024)
        assert march_bills.count() == 1
