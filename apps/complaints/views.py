import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.utils import get_warden_blocks, is_admin
from apps.students.models import Student

from .models import Complaint


def _complaint_qs(user):
    if is_admin(user):
        return Complaint.objects.all()
    from apps.hostel.models import RoomAllocation

    my_blocks = get_warden_blocks(user)
    student_ids = RoomAllocation.objects.filter(
        status="Active", room__block__in=my_blocks
    ).values_list("student_id", flat=True)
    return Complaint.objects.filter(student_id__in=student_ids)


@login_required
def complaint_list(request):
    status = request.GET.get("status", "")
    complaints = _complaint_qs(request.user)
    if status:
        complaints = complaints.filter(status=status)
    return render(
        request, "complaints/list.html", {"complaints": complaints, "status_filter": status}
    )


@login_required
def complaint_add(request):
    if is_admin(request.user):
        students = Student.objects.filter(is_active=True)
    else:
        from apps.hostel.models import RoomAllocation

        my_blocks = get_warden_blocks(request.user)
        student_ids = RoomAllocation.objects.filter(
            status="Active", room__block__in=my_blocks
        ).values_list("student_id", flat=True)
        students = Student.objects.filter(id__in=student_ids, is_active=True)

    if request.method == "POST":
        d = request.POST
        Complaint.objects.create(
            student_id=d["student"],
            category=d["category"],
            subject=d["subject"],
            description=d["description"],
            priority=d["priority"],
        )
        messages.success(request, "Complaint submitted!")
        return redirect("complaint_list")
    return render(request, "complaints/form.html", {"students": students})


@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if not is_admin(request.user):
        allowed = _complaint_qs(request.user)
        if not allowed.filter(pk=pk).exists():
            messages.error(request, "Access denied.")
            return redirect("complaint_list")
    if request.method == "POST":
        complaint.status = request.POST.get("status", complaint.status)
        complaint.admin_remarks = request.POST.get("admin_remarks", "")
        if complaint.status == "Resolved":
            complaint.resolved_at = datetime.datetime.now()
        complaint.save()
        messages.success(request, "Complaint updated!")
        return redirect("complaint_detail", pk=pk)
    return render(request, "complaints/detail.html", {"complaint": complaint})
