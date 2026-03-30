from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from apps.hostel.models import Block

from .models import WardenProfile
from .utils import is_admin, role_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect("dashboard")
        messages.error(request, "Invalid username or password.")
    return render(request, "accounts/login.html")


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


@login_required
def profile_view(request):
    warden_profile = getattr(request.user, "warden_profile", None)
    return render(
        request,
        "accounts/profile.html",
        {
            "warden_profile": warden_profile,
        },
    )


# ─── Warden Management (Admin only) ───────────────────────────────────────────


@login_required
@role_required("admin")
def warden_list(request):
    wardens = WardenProfile.objects.select_related("user").prefetch_related("blocks").all()
    return render(request, "accounts/warden_list.html", {"wardens": wardens})


@login_required
@role_required("admin")
def warden_add(request):
    blocks = Block.objects.filter(is_active=True)
    if request.method == "POST":
        d = request.POST
        # Validate uniqueness
        if User.objects.filter(username=d["username"]).exists():
            messages.error(request, "Username already taken.")
            return render(
                request, "accounts/warden_form.html", {"blocks": blocks, "title": "Add Warden"}
            )

        user = User.objects.create_user(
            username=d["username"],
            password=d["password"],
            first_name=d["first_name"],
            last_name=d["last_name"],
            email=d.get("email", ""),
        )
        wp = WardenProfile.objects.create(
            user=user,
            phone=d.get("phone", ""),
            employee_id=d.get("employee_id", ""),
        )
        selected_blocks = d.getlist("blocks")
        wp.blocks.set(selected_blocks)

        # Also update the Block.warden_name / warden_phone for display
        for blk in wp.blocks.all():
            blk.warden_name = user.get_full_name()
            blk.warden_phone = wp.phone
            blk.save()

        messages.success(request, f"Warden {user.get_full_name()} created successfully!")
        return redirect("warden_list")
    return render(
        request,
        "accounts/warden_form.html",
        {"blocks": blocks, "title": "Add Warden", "action": "Create"},
    )


@login_required
@role_required("admin")
def warden_edit(request, pk):
    wp = get_object_or_404(WardenProfile, pk=pk)
    blocks = Block.objects.filter(is_active=True)
    if request.method == "POST":
        d = request.POST
        wp.user.first_name = d["first_name"]
        wp.user.last_name = d["last_name"]
        wp.user.email = d.get("email", "")
        if d.get("password"):
            wp.user.set_password(d["password"])
        wp.user.save()
        wp.phone = d.get("phone", "")
        wp.employee_id = d.get("employee_id", "")
        wp.is_active = "is_active" in d
        wp.save()
        selected_blocks = d.getlist("blocks")
        wp.blocks.set(selected_blocks)
        for blk in wp.blocks.all():
            blk.warden_name = wp.user.get_full_name()
            blk.warden_phone = wp.phone
            blk.save()
        messages.success(request, "Warden updated successfully!")
        return redirect("warden_list")
    return render(
        request,
        "accounts/warden_form.html",
        {
            "blocks": blocks,
            "wp": wp,
            "title": f"Edit Warden – {wp.user.get_full_name()}",
            "action": "Update",
        },
    )


@login_required
@role_required("admin")
def warden_delete(request, pk):
    wp = get_object_or_404(WardenProfile, pk=pk)
    if request.method == "POST":
        wp.user.delete()
        messages.success(request, "Warden removed.")
        return redirect("warden_list")
    return render(request, "accounts/warden_confirm_delete.html", {"wp": wp})
