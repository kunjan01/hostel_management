from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from apps.accounts.utils import get_warden_blocks, is_admin
from apps.complaints.models import Complaint
from apps.hostel.models import Block, Room, RoomAllocation
from apps.mess.models import MessBill, MessRegistration
from apps.students.models import Student


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for Docker/load balancers"""
    return JsonResponse({"status": "healthy"}, status=200)


@login_required
def dashboard(request):
    user = request.user

    if is_admin(user):
        # ── Admin: sees everything ──────────────────────────────────────────
        total_students = Student.objects.filter(is_active=True).count()
        total_rooms = Room.objects.count()
        available_rooms = Room.objects.filter(status="Available").count()
        occupied_rooms = Room.objects.filter(status="Occupied").count()
        total_blocks = Block.objects.filter(is_active=True).count()
        active_allocs = RoomAllocation.objects.filter(status="Active").count()
        mess_registered = MessRegistration.objects.filter(is_active=True).count()
        pending_bills = MessBill.objects.filter(status="Pending").count()
        pending_complaints = Complaint.objects.filter(status="Pending").count()
        recent_students = Student.objects.filter(is_active=True).order_by("-created_at")[:5]
        recent_complaints = Complaint.objects.order_by("-created_at")[:5]
    else:
        # ── Warden: scoped to assigned blocks ──────────────────────────────
        my_blocks = get_warden_blocks(user)
        my_rooms = Room.objects.filter(block__in=my_blocks)
        my_allocs = RoomAllocation.objects.filter(room__block__in=my_blocks, status="Active")
        student_ids = my_allocs.values_list("student_id", flat=True)

        total_students = student_ids.count()
        total_rooms = my_rooms.count()
        available_rooms = my_rooms.filter(status="Available").count()
        occupied_rooms = my_rooms.filter(status="Occupied").count()
        total_blocks = my_blocks.count()
        active_allocs = my_allocs.count()
        mess_registered = MessRegistration.objects.filter(
            student_id__in=student_ids, is_active=True
        ).count()
        pending_bills = MessBill.objects.filter(
            student_id__in=student_ids, status="Pending"
        ).count()
        pending_complaints = Complaint.objects.filter(
            student_id__in=student_ids, status="Pending"
        ).count()
        recent_students = Student.objects.filter(id__in=student_ids).order_by("-created_at")[:5]
        recent_complaints = Complaint.objects.filter(student_id__in=student_ids).order_by(
            "-created_at"
        )[:5]

    return render(
        request,
        "dashboard/index.html",
        {
            "total_students": total_students,
            "total_rooms": total_rooms,
            "available_rooms": available_rooms,
            "occupied_rooms": occupied_rooms,
            "total_blocks": total_blocks,
            "active_allocations": active_allocs,
            "mess_registered": mess_registered,
            "pending_bills": pending_bills,
            "pending_complaints": pending_complaints,
            "recent_students": recent_students,
            "recent_complaints": recent_complaints,
        },
    )
