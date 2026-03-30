from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import WardenProfile


class WardenProfileInline(admin.StackedInline):
    model = WardenProfile
    can_delete = True
    verbose_name_plural = "Warden Profile"
    filter_horizontal = ["blocks"]


class CustomUserAdmin(UserAdmin):
    inlines = [WardenProfileInline]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(WardenProfile)
class WardenProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "employee_id", "phone", "is_active", "created_at"]
    list_filter = ["is_active"]
    filter_horizontal = ["blocks"]
    search_fields = ["user__username", "user__first_name", "employee_id"]
