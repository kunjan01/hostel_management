"""
Service layer for billing operations

This module contains business logic for generating bills, processing payments,
and managing billing-related operations. Separates concerns from views.
"""

import datetime
from decimal import Decimal
from typing import Dict, List, Tuple

from django.db.models import QuerySet
from django.utils import timezone

from apps.hostel.models import RoomAllocation, RoomBill
from apps.mess.models import MessBill, MessRegistration
from apps.students.models import Student


class BillGenerationService:
    """Service for generating bills for mess and hostel"""

    @staticmethod
    def generate_mess_bills(month: int, year: int) -> Dict[str, int]:
        """
        Generate mess bills for all active registrations

        Args:
            month: Month number (1-12)
            year: Year (e.g., 2024)

        Returns:
            Dictionary with count of created bills and errors
        """
        created_count = 0
        skipped_count = 0
        errors = []

        try:
            registrations = MessRegistration.objects.filter(is_active=True)

            for reg in registrations:
                try:
                    bill, created = MessBill.objects.get_or_create(
                        student=reg.student,
                        month=month,
                        year=year,
                        defaults={
                            "amount": reg.monthly_charge,
                            "status": "Pending",
                            "due_date": datetime.date(year, month, 25),
                        },
                    )
                    if created:
                        created_count += 1
                    else:
                        skipped_count += 1
                except Exception as e:
                    errors.append(f"Failed to create bill for {reg.student.name}: {str(e)}")

            return {
                "created": created_count,
                "skipped": skipped_count,
                "errors": errors,
                "status": "success",
            }
        except Exception as e:
            return {
                "created": 0,
                "skipped": 0,
                "errors": [str(e)],
                "status": "failed",
            }

    @staticmethod
    def generate_room_bills(month: int, year: int) -> Dict[str, int]:
        """
        Generate room bills for all active allocations

        Args:
            month: Month number (1-12)
            year: Year (e.g., 2024)

        Returns:
            Dictionary with count of created bills and errors
        """
        created_count = 0
        skipped_count = 0
        errors = []

        try:
            allocations = RoomAllocation.objects.filter(status="Active")

            for allocation in allocations:
                try:
                    bill, created = RoomBill.objects.get_or_create(
                        student=allocation.student,
                        month=month,
                        year=year,
                        defaults={
                            "room": allocation.room,
                            "room_rent": allocation.room.monthly_rent,
                            "status": "Pending",
                            "due_date": datetime.date(year, month, 25),
                        },
                    )
                    if created:
                        created_count += 1
                    else:
                        skipped_count += 1
                except Exception as e:
                    errors.append(
                        f"Failed to create room bill for {allocation.student.name}: {str(e)}"
                    )

            return {
                "created": created_count,
                "skipped": skipped_count,
                "errors": errors,
                "status": "success",
            }
        except Exception as e:
            return {
                "created": 0,
                "skipped": 0,
                "errors": [str(e)],
                "status": "failed",
            }

    @staticmethod
    def generate_all_bills(month: int, year: int) -> Dict[str, any]:
        """
        Generate both mess and room bills for a specific month/year

        Args:
            month: Month number (1-12)
            year: Year (e.g., 2024)

        Returns:
            Combined results from mess and room bill generation
        """
        mess_result = BillGenerationService.generate_mess_bills(month, year)
        room_result = BillGenerationService.generate_room_bills(month, year)

        return {
            "month": month,
            "year": year,
            "mess_bills": mess_result,
            "room_bills": room_result,
            "total_created": mess_result["created"] + room_result["created"],
            "total_skipped": mess_result["skipped"] + room_result["skipped"],
            "all_errors": mess_result["errors"] + room_result["errors"],
            "status": "success" if not (mess_result["errors"] or room_result["errors"]) else "partial",
        }


class BillPaymentService:
    """Service for processing bill payments"""

    @staticmethod
    def mark_bill_paid(bill_id: int, bill_type: str = "mess") -> Tuple[bool, str]:
        """
        Mark a bill as paid

        Args:
            bill_id: ID of the bill
            bill_type: Type of bill ('mess' or 'room')

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if bill_type == "mess":
                bill = MessBill.objects.get(id=bill_id)
            elif bill_type == "room":
                bill = RoomBill.objects.get(id=bill_id)
            else:
                return False, "Invalid bill type"

            bill.status = "Paid"
            bill.paid_date = timezone.now().date()
            bill.save(update_fields=["status", "paid_date"])

            return True, f"{bill_type.capitalize()} bill marked as paid"
        except MessBill.DoesNotExist:
            return False, "Mess bill not found"
        except RoomBill.DoesNotExist:
            return False, "Room bill not found"
        except Exception as e:
            return False, f"Error marking bill as paid: {str(e)}"

    @staticmethod
    def mark_bill_pending(bill_id: int, bill_type: str = "mess") -> Tuple[bool, str]:
        """
        Mark a bill as pending (revert from paid)

        Args:
            bill_id: ID of the bill
            bill_type: Type of bill ('mess' or 'room')

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if bill_type == "mess":
                bill = MessBill.objects.get(id=bill_id)
            elif bill_type == "room":
                bill = RoomBill.objects.get(id=bill_id)
            else:
                return False, "Invalid bill type"

            bill.status = "Pending"
            bill.paid_date = None
            bill.save(update_fields=["status", "paid_date"])

            return True, f"{bill_type.capitalize()} bill marked as pending"
        except MessBill.DoesNotExist:
            return False, "Mess bill not found"
        except RoomBill.DoesNotExist:
            return False, "Room bill not found"
        except Exception as e:
            return False, f"Error marking bill as pending: {str(e)}"

    @staticmethod
    def bulk_mark_paid(bill_ids: List[int], bill_type: str = "mess") -> Dict[str, any]:
        """
        Mark multiple bills as paid

        Args:
            bill_ids: List of bill IDs
            bill_type: Type of bill ('mess' or 'room')

        Returns:
            Dictionary with success count and errors
        """
        success_count = 0
        errors = []

        if bill_type not in ["mess", "room"]:
            return {"success": 0, "errors": ["Invalid bill type"]}

        Model = MessBill if bill_type == "mess" else RoomBill

        try:
            for bill_id in bill_ids:
                try:
                    bill = Model.objects.get(id=bill_id)
                    bill.status = "Paid"
                    bill.paid_date = timezone.now().date()
                    bill.save(update_fields=["status", "paid_date"])
                    success_count += 1
                except Model.DoesNotExist:
                    errors.append(f"Bill ID {bill_id} not found")
                except Exception as e:
                    errors.append(f"Error processing bill {bill_id}: {str(e)}")

            return {
                "success": success_count,
                "failed": len(bill_ids) - success_count,
                "errors": errors,
            }
        except Exception as e:
            return {
                "success": 0,
                "failed": len(bill_ids),
                "errors": [str(e)],
            }


class BillQueryService:
    """Service for querying and filtering bills"""

    @staticmethod
    def get_pending_bills(student: Student = None) -> QuerySet:
        """Get all pending bills"""
        query = MessBill.objects.filter(status="Pending")
        if student:
            query = query.filter(student=student)
        return query.select_related("student").order_by("due_date")

    @staticmethod
    def get_overdue_bills(student: Student = None) -> QuerySet:
        """Get overdue bills (due_date has passed)"""
        today = timezone.now().date()
        query = MessBill.objects.filter(status="Pending", due_date__lt=today)
        if student:
            query = query.filter(student=student)
        return query.select_related("student").order_by("due_date")

    @staticmethod
    def get_bills_for_month(month: int, year: int, student: Student = None) -> Dict[str, QuerySet]:
        """Get mess and room bills for a specific month/year"""
        filters = {"month": month, "year": year}

        if student:
            filters["student"] = student

        return {
            "mess_bills": MessBill.objects.filter(**filters).select_related("student"),
            "room_bills": RoomBill.objects.filter(**filters).select_related("student"),
        }

    @staticmethod
    def get_student_bill_summary(student: Student) -> Dict[str, any]:
        """Get summary of all bills for a student"""
        mess_bills = MessBill.objects.filter(student=student)
        room_bills = RoomBill.objects.filter(student=student)

        mess_pending = mess_bills.filter(status="Pending").count()
        mess_paid = mess_bills.filter(status="Paid").count()
        mess_total = mess_bills.aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

        room_pending = room_bills.filter(status="Pending").count()
        room_paid = room_bills.filter(status="Paid").count()
        room_total = room_bills.aggregate(total=models.Sum("room_rent"))["total"] or Decimal("0")

        return {
            "student": student,
            "mess": {
                "pending": mess_pending,
                "paid": mess_paid,
                "total_amount": mess_total,
            },
            "room": {
                "pending": room_pending,
                "paid": room_paid,
                "total_amount": room_total,
            },
            "overall_pending": mess_pending + room_pending,
            "overall_paid": mess_paid + room_paid,
        }


# Import at bottom to avoid circular imports
from django.db import models
