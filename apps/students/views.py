from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.utils import get_warden_blocks, is_admin

from .models import Student


def _student_qs(user):
    """Return base student queryset scoped to the user's role."""
    if is_admin(user):
        return Student.objects.filter(is_active=True)
    # Warden: only students currently allocated in their blocks
    from apps.hostel.models import RoomAllocation

    my_blocks = get_warden_blocks(user)
    student_ids = RoomAllocation.objects.filter(
        status="Active", room__block__in=my_blocks
    ).values_list("student_id", flat=True)
    return Student.objects.filter(id__in=student_ids, is_active=True)


@login_required
def student_list(request):
    query = request.GET.get("q", "")
    students = _student_qs(request.user)
    if query:
        students = students.filter(
            Q(name__icontains=query) | Q(enrollment_no__icontains=query) | Q(email__icontains=query)
        )
    paginator = Paginator(students, 10)
    students = paginator.get_page(request.GET.get("page"))
    return render(request, "students/list.html", {"students": students, "query": query})


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    # Warden permission check
    if not is_admin(request.user):
        allowed_ids = _student_qs(request.user).values_list("id", flat=True)
        if student.pk not in list(allowed_ids):
            messages.error(request, "Access denied.")
            return redirect("student_list")
    from apps.hostel.models import RoomAllocation
    from apps.mess.models import MessBill, MessRegistration

    allocation = RoomAllocation.objects.filter(student=student, status="Active").first()
    mess_reg = MessRegistration.objects.filter(student=student).first()
    bills = MessBill.objects.filter(student=student)[:6]
    return render(
        request,
        "students/detail.html",
        {
            "student": student,
            "allocation": allocation,
            "mess_reg": mess_reg,
            "bills": bills,
        },
    )


@login_required
def student_add(request):
    # Both admin and warden can add students
    if request.method == "POST":
        data = request.POST
        try:
            student = Student(
                enrollment_no=data["enrollment_no"],
                name=data["name"],
                email=data["email"],
                phone=data["phone"],
                gender=data["gender"],
                date_of_birth=data["date_of_birth"],
                blood_group=data.get("blood_group", ""),
                course=data["course"],
                year=int(data["year"]),
                branch=data["branch"],
                address=data["address"],
                city=data["city"],
                state=data["state"],
                parent_name=data["parent_name"],
                parent_phone=data["parent_phone"],
                emergency_contact=data.get("emergency_contact", ""),
            )
            if "photo" in request.FILES:
                student.photo = request.FILES["photo"]
            student.save()
            messages.success(request, f"Student {student.name} added successfully!")
            return redirect("student_detail", pk=student.pk)
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(request, "students/form.html", {"title": "Add Student", "action": "Add"})


@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if not is_admin(request.user):
        allowed_ids = _student_qs(request.user).values_list("id", flat=True)
        if student.pk not in list(allowed_ids):
            messages.error(request, "Access denied.")
            return redirect("student_list")
    if request.method == "POST":
        d = request.POST
        try:
            student.name = d["name"]
            student.email = d["email"]
            student.phone = d["phone"]
            student.gender = d["gender"]
            student.date_of_birth = d["date_of_birth"]
            student.blood_group = d.get("blood_group", "")
            student.course = d["course"]
            student.year = int(d["year"])
            student.branch = d["branch"]
            student.address = d["address"]
            student.city = d["city"]
            student.state = d["state"]
            student.parent_name = d["parent_name"]
            student.parent_phone = d["parent_phone"]
            student.emergency_contact = d.get("emergency_contact", "")
            if "photo" in request.FILES:
                student.photo = request.FILES["photo"]
            student.save()
            messages.success(request, f"Student {student.name} updated!")
            return redirect("student_detail", pk=student.pk)
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(
        request,
        "students/form.html",
        {"title": "Edit Student", "action": "Update", "student": student},
    )


@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.is_active = False
        student.save()
        messages.success(request, f"Student {student.name} deactivated.")
        return redirect("student_list")
    return render(request, "students/confirm_delete.html", {"student": student})
