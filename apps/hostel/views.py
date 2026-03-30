import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.utils import get_warden_blocks, is_admin, role_required
from apps.students.models import Student

from .models import Block, Room, RoomAllocation


def _get_accessible_blocks(user):
    return Block.objects.filter(is_active=True) if is_admin(user) else get_warden_blocks(user)


@login_required
def block_list(request):
    blocks = _get_accessible_blocks(request.user)
    return render(request, "hostel/block_list.html", {"blocks": blocks})


@login_required
@role_required("admin")
def block_add(request):
    if request.method == "POST":
        d = request.POST
        Block.objects.create(
            name=d["name"],
            block_type=d["block_type"],
            floors=d["floors"],
            warden_name=d.get("warden_name", ""),
            warden_phone=d.get("warden_phone", ""),
            description=d.get("description", ""),
        )
        messages.success(request, "Block added successfully!")
        return redirect("block_list")
    return render(request, "hostel/block_form.html", {"title": "Add Block"})


@login_required
def block_detail(request, pk):
    block = get_object_or_404(Block, pk=pk)
    # Wardens can only view their own blocks
    if not is_admin(request.user):
        my_blocks = get_warden_blocks(request.user)
        if not my_blocks.filter(pk=pk).exists():
            messages.error(request, "Access denied: this block is not assigned to you.")
            return redirect("block_list")
    rooms = Room.objects.filter(block=block)
    return render(request, "hostel/block_detail.html", {"block": block, "rooms": rooms})


@login_required
def room_list(request):
    accessible_blocks = _get_accessible_blocks(request.user)
    block_id = request.GET.get("block")
    status = request.GET.get("status")
    rooms = Room.objects.filter(block__in=accessible_blocks)
    if block_id:
        rooms = rooms.filter(block_id=block_id)
    if status:
        rooms = rooms.filter(status=status)
    return render(
        request,
        "hostel/room_list.html",
        {
            "rooms": rooms,
            "blocks": accessible_blocks,
        },
    )


@login_required
def room_add(request):
    accessible_blocks = _get_accessible_blocks(request.user)
    if request.method == "POST":
        d = request.POST
        block = get_object_or_404(Block, pk=d["block"])
        # Warden can only add rooms to their blocks
        if not is_admin(request.user) and not accessible_blocks.filter(pk=block.pk).exists():
            messages.error(request, "Access denied.")
            return redirect("room_list")
        Room.objects.create(
            block=block,
            room_number=d["room_number"],
            floor=d["floor"],
            room_type=d["room_type"],
            capacity=d["capacity"],
            monthly_rent=d["monthly_rent"],
            has_ac="has_ac" in d,
            has_wifi="has_wifi" in d,
            has_attached_bathroom="has_attached_bathroom" in d,
        )
        messages.success(request, "Room added successfully!")
        return redirect("room_list")
    return render(
        request, "hostel/room_form.html", {"blocks": accessible_blocks, "title": "Add Room"}
    )


@login_required
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if not is_admin(request.user):
        my_blocks = get_warden_blocks(request.user)
        if not my_blocks.filter(pk=room.block_id).exists():
            messages.error(request, "Access denied.")
            return redirect("room_list")
    allocations = RoomAllocation.objects.filter(room=room).select_related("student")
    return render(request, "hostel/room_detail.html", {"room": room, "allocations": allocations})


@login_required
def allocate_room(request):
    accessible_blocks = _get_accessible_blocks(request.user)
    allocated_ids = RoomAllocation.objects.filter(status="Active").values_list(
        "student_id", flat=True
    )

    if is_admin(request.user):
        unallocated_students = Student.objects.filter(is_active=True).exclude(id__in=allocated_ids)
    else:
        # Warden: only students already in their block + any unallocated students
        unallocated_students = Student.objects.filter(is_active=True).exclude(id__in=allocated_ids)

    rooms = Room.objects.filter(block__in=accessible_blocks).exclude(status="Maintenance")

    if request.method == "POST":
        student = get_object_or_404(Student, pk=request.POST.get("student"))
        room = get_object_or_404(Room, pk=request.POST.get("room"))
        if not accessible_blocks.filter(pk=room.block_id).exists():
            messages.error(request, "You can only allocate rooms in your assigned blocks.")
        elif room.available_beds() <= 0:
            messages.error(request, "No beds available in this room!")
        elif RoomAllocation.objects.filter(student=student, status="Active").exists():
            messages.error(request, "Student already has an active room allocation!")
        else:
            RoomAllocation.objects.create(student=student, room=room)
            if room.available_beds() == 0:
                room.status = "Occupied"
                room.save()
            messages.success(request, f"Room allocated to {student.name}!")
            return redirect("allocation_list")

    return render(
        request,
        "hostel/allocate.html",
        {
            "students": unallocated_students,
            "rooms": rooms,
        },
    )


@login_required
def allocation_list(request):
    accessible_blocks = _get_accessible_blocks(request.user)
    allocations = RoomAllocation.objects.filter(
        status="Active", room__block__in=accessible_blocks
    ).select_related("student", "room__block")
    return render(request, "hostel/allocation_list.html", {"allocations": allocations})


@login_required
def vacate_room(request, pk):
    allocation = get_object_or_404(RoomAllocation, pk=pk)
    accessible_blocks = _get_accessible_blocks(request.user)
    if not accessible_blocks.filter(pk=allocation.room.block_id).exists():
        messages.error(request, "Access denied.")
        return redirect("allocation_list")
    if request.method == "POST":
        allocation.status = "Vacated"
        allocation.vacating_date = datetime.date.today()
        allocation.save()
        room = allocation.room
        if room.current_occupants() == 0:
            room.status = "Available"
            room.save()
        messages.success(request, f"Room vacated for {allocation.student.name}.")
        return redirect("allocation_list")
    return render(request, "hostel/vacate_confirm.html", {"allocation": allocation})
