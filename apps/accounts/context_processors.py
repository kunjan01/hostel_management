"""
Injects user_role and warden_blocks into every template context.
Add to settings TEMPLATES > OPTIONS > context_processors.
"""

from .utils import get_user_role, get_warden_blocks, is_admin, is_warden


def user_role(request):
    if not request.user.is_authenticated:
        return {}
    role = get_user_role(request.user)
    ctx = {"user_role": role, "is_admin_user": is_admin(request.user)}
    if role == "warden":
        ctx["warden_blocks"] = get_warden_blocks(request.user)
    return ctx
