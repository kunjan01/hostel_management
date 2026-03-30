"""
Role helpers — import these in every view that needs role-aware filtering.

Usage:
    from apps.accounts.utils import is_admin, get_warden_blocks, role_required

    @login_required
    @role_required('admin')          # admin only
    def some_admin_view(request): ...

    @login_required
    def some_shared_view(request):
        if is_admin(request.user):
            qs = Room.objects.all()
        else:
            blocks = get_warden_blocks(request.user)
            qs = Room.objects.filter(block__in=blocks)
"""

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def is_admin(user):
    """True for superuser or staff."""
    return user.is_superuser or user.is_staff


def is_warden(user):
    return hasattr(user, "warden_profile") and user.warden_profile.is_active


def get_user_role(user):
    if is_admin(user):
        return "admin"
    if is_warden(user):
        return "warden"
    return "unknown"


def get_warden_blocks(user):
    """Returns queryset of blocks the warden manages."""
    if is_warden(user):
        return user.warden_profile.get_blocks()
    return None  # admin should not call this


def role_required(*roles):
    """Decorator: @role_required('admin') or @role_required('admin', 'warden')"""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            role = get_user_role(request.user)
            if role not in roles:
                messages.error(request, "You don't have permission to access that page.")
                return redirect("dashboard")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
