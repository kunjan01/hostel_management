import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, View

from apps.accounts.utils import get_warden_blocks, is_admin, role_required
from apps.hostel.models import RoomAllocation, RoomBill
from apps.services.billing_service import (
    BillGenerationService,
    BillPaymentService,
    BillQueryService,
)
from apps.students.models import Student

from .models import MessBill, MessMenu, MessRegistration


def _scoped_students(user):
    """Get students accessible to the current user"""
    if is_admin(user):
        return Student.objects.filter(is_active=True)
    from apps.hostel.models import RoomAllocation

    my_blocks = get_warden_blocks(user)
    student_ids = RoomAllocation.objects.filter(
        status="Active", room__block__in=my_blocks
    ).values_list("student_id", flat=True)
    return Student.objects.filter(id__in=student_ids, is_active=True)


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure only admins can access"""

    def test_func(self):
        return self.request.user.is_staff


class MenuView(LoginRequiredMixin, TemplateView):
    """Display mess menu for the week"""

    template_name = "mess/menu.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        meals = ["Breakfast", "Lunch", "Snacks", "Dinner"]

        menu_list = MessMenu.objects.all()
        menu_by_day = {}
        for day in days:
            menu_by_day[day] = {m.meal: m for m in menu_list if m.day == day}

        context.update({"menu_list": menu_list, "menu": menu_by_day, "days": days, "meals": meals})
        return context


class MenuUpdateView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Update mess menu"""

    template_name = "mess/menu_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        meals = ["Breakfast", "Lunch", "Snacks", "Dinner"]

        existing = {f"{m.day}_{m.meal}": m for m in MessMenu.objects.all()}
        context.update({"days": days, "meals": meals, "existing": existing})
        return context

    def post(self, request, *args, **kwargs):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        meals = ["Breakfast", "Lunch", "Snacks", "Dinner"]

        for day in days:
            for meal in meals:
                key = f"{day}_{meal}"
                items = request.POST.get(key, "")
                timing = request.POST.get(f"{key}_timing", "")
                if items:
                    MessMenu.objects.update_or_create(
                        day=day, meal=meal, defaults={"items": items, "timing": timing}
                    )

        messages.success(request, "Menu updated!")
        return redirect("mess_menu")


class RegistrationListView(LoginRequiredMixin, ListView):
    """List all mess registrations"""

    model = MessRegistration
    template_name = "mess/registration_list.html"
    context_object_name = "regs"
    paginate_by = 20

    def get_queryset(self):
        students = _scoped_students(self.request.user)
        return (
            MessRegistration.objects.filter(is_active=True, student__in=students)
            .select_related("student")
            .order_by("student__name")
        )


class RegisterStudentView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Register a student for mess"""

    template_name = "mess/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scoped = _scoped_students(self.request.user)
        registered_ids = MessRegistration.objects.filter(is_active=True).values_list(
            "student_id", flat=True
        )
        students = scoped.exclude(id__in=registered_ids)

        context["students"] = students
        return context

    def post(self, request, *args, **kwargs):
        student_id = request.POST.get("student")
        student = get_object_or_404(Student, pk=student_id)

        MessRegistration.objects.create(
            student=student,
            plan=request.POST.get("plan"),
            monthly_charge=request.POST.get("monthly_charge"),
        )

        messages.success(request, f"{student.name} registered for mess!")
        return redirect("registration_list")


class BillListView(LoginRequiredMixin, ListView):
    """Display bills for mess and hostel room"""

    model = MessBill
    template_name = "mess/bill_list.html"
    context_object_name = "bills"
    paginate_by = 25

    def get_queryset(self):
        """Get bills for current user (scoped) with optimized queries"""
        students = _scoped_students(self.request.user)
        return (
            MessBill.objects.filter(student__in=students)
            .select_related("student", "student__user")  # ✓ Optimize joins
            .order_by("-year", "-month")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = _scoped_students(self.request.user)

        # ✓ Optimized queries with select_related
        mess_bills = (
            MessBill.objects.filter(student__in=students)
            .select_related("student")
            .order_by("-year", "-month")
        )
        room_bills = (
            RoomBill.objects.filter(student__in=students)
            .select_related("student")
            .order_by("-year", "-month")
        )

        # Combine bills
        combined_bills = {}
        for bill in mess_bills:
            key = f"{bill.student_id}_{bill.year}_{bill.month}"
            if key not in combined_bills:
                combined_bills[key] = {
                    "student": bill.student,
                    "month": bill.month,
                    "year": bill.year,
                    "mess_bill": bill,
                    "room_bill": None,
                    "total": bill.amount,
                    "status": bill.status,
                }
            else:
                combined_bills[key]["mess_bill"] = bill
                combined_bills[key]["total"] += bill.amount

        for bill in room_bills:
            key = f"{bill.student_id}_{bill.year}_{bill.month}"
            if key not in combined_bills:
                combined_bills[key] = {
                    "student": bill.student,
                    "month": bill.month,
                    "year": bill.year,
                    "mess_bill": None,
                    "room_bill": bill,
                    "total": bill.room_rent,
                    "status": bill.status,
                }
            else:
                combined_bills[key]["room_bill"] = bill
                combined_bills[key]["total"] += bill.room_rent

        sorted_bills = sorted(
            combined_bills.values(), key=lambda x: (x["year"], x["month"]), reverse=True
        )
        context["bills"] = sorted_bills
        context["total_pending"] = sum(1 for b in sorted_bills if b["status"] == "Pending")

        return context


class GenerateBillView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Generate monthly bills for mess and hostel using service layer"""

    template_name = "mess/generate_bill.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {"months": MessBill.MONTH_CHOICES, "current_year": datetime.date.today().year}
        )
        return context

    def post(self, request, *args, **kwargs):
        month = int(request.POST.get("month"))
        year = int(request.POST.get("year"))

        # Use BillGenerationService to generate both mess and room bills
        result = BillGenerationService.generate_all_bills(month, year)

        # Construct success message
        success_msg = (
            f"Bills generated! Mess: {result['mess_bills']['created']}, "
            f"Room: {result['room_bills']['created']}, "
            f"Total: {result['total_created']}"
        )
        messages.success(request, success_msg)

        # Show any errors that occurred
        if result["all_errors"]:
            for error in result["all_errors"]:
                messages.warning(request, f"Warning: {error}")

        return redirect("bill_list")


class MarkBillPaidView(LoginRequiredMixin, View):
    """Mark mess bill as paid using service layer"""

    def post(self, request, pk):
        bill = get_object_or_404(MessBill, pk=pk)
        students = _scoped_students(request.user)

        if not students.filter(pk=bill.student_id).exists():
            messages.error(request, "Access denied.")
            return redirect("bill_list")

        # Use BillPaymentService
        success, message = BillPaymentService.mark_bill_paid(pk, bill_type="mess")
        if success:
            messages.success(request, f"{message} for {bill.student.name}.")
        else:
            messages.error(request, message)

        return redirect("bill_list")


class MarkRoomBillPaidView(LoginRequiredMixin, View):
    """Mark room bill as paid using service layer"""

    def post(self, request, pk):
        bill = get_object_or_404(RoomBill, pk=pk)
        students = _scoped_students(request.user)

        if not students.filter(pk=bill.student_id).exists():
            messages.error(request, "Access denied.")
            return redirect("bill_list")

        # Use BillPaymentService
        success, message = BillPaymentService.mark_bill_paid(pk, bill_type="room")
        if success:
            messages.success(request, f"{message} for {bill.student.name}.")
        else:
            messages.error(request, message)

        return redirect("bill_list")
