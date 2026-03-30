from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["enrollment_no", "name", "email", "phone", "course", "year", "is_active"]
    list_filter = ["course", "year", "gender", "is_active"]
    search_fields = ["name", "enrollment_no", "email"]
