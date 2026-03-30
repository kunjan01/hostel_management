from django.contrib import admin
from django.db.models import Count, Q, Sum
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import MessBill, MessMenu, MessRegistration


@admin.register(MessMenu)
class MessMenuAdmin(admin.ModelAdmin):
    """Admin for managing mess menu"""

    list_display = ["day", "meal", "items_preview", "timing"]
    list_filter = ["day", "meal"]
    search_fields = ["items", "timing"]
    list_editable = ["timing"]

    fieldsets = (
        (
            "Menu Information",
            {
                "fields": ("day", "meal"),
            },
        ),
        (
            "Details",
            {
                "fields": ("items", "timing"),
                "classes": ("wide",),
            },
        ),
    )

    def items_preview(self, obj):
        """Show preview of menu items"""
        preview = obj.items[:60] + ("..." if len(obj.items) > 60 else "")
        return preview

    items_preview.short_description = "Items Preview"

    class Meta:
        ordering = ["day", "meal"]


@admin.register(MessRegistration)
class MessRegistrationAdmin(admin.ModelAdmin):
    """Admin for mess registrations"""

    list_display = [
        "student_link",
        "plan_badge",
        "monthly_charge_display",
        "is_active_badge",
        "registration_date",
    ]
    list_filter = ["is_active", "plan", "registration_date"]
    search_fields = ["student__name", "student__enrollment_no", "student__email"]
    readonly_fields = ["registration_date", "student_info"]
    date_hierarchy = "registration_date"

    fieldsets = (
        (
            "Student Information",
            {
                "fields": ("student", "student_info"),
            },
        ),
        (
            "Mess Registration",
            {
                "fields": ("plan", "monthly_charge"),
                "classes": ("wide",),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active", "registration_date"),
            },
        ),
    )

    def student_link(self, obj):
        """Link to student detail"""
        url = reverse("admin:students_student_change", args=[obj.student.id])
        return format_html(
            '<a href="{}">{} ({})</a>', url, obj.student.name, obj.student.enrollment_no
        )

    student_link.short_description = "Student"

    def plan_badge(self, obj):
        """Display plan as badge"""
        colors = {"Full": "#0099ff", "Lunch_Dinner": "#ff9900", "Breakfast_Lunch": "#99ff00"}
        color = colors.get(obj.plan, "#cccccc")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_plan_display(),
        )

    plan_badge.short_description = "Plan"

    def monthly_charge_display(self, obj):
        """Format charge as currency"""
        return f"₹{obj.monthly_charge:,.2f}"

    monthly_charge_display.short_description = "Charge"

    def is_active_badge(self, obj):
        """Display active status as badge"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 12px; border-radius: 4px;">✓ Active</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 4px 12px; border-radius: 4px;">✗ Inactive</span>'
        )

    is_active_badge.short_description = "Status"

    def student_info(self, obj):
        """Display additional student info"""
        student = obj.student
        return (
            f"Email: {student.email}\nPhone: {student.phone}\nEnrollment: {student.enrollment_no}"
        )

    student_info.short_description = "Student Details"

    actions = ["mark_active", "mark_inactive"]

    def mark_active(self, request, queryset):
        """Bulk action to mark as active"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} registrations marked as active.")

    mark_active.short_description = "Mark selected as active"

    def mark_inactive(self, request, queryset):
        """Bulk action to mark as inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} registrations marked as inactive.")

    mark_inactive.short_description = "Mark selected as inactive"


@admin.register(MessBill)
class MessBillAdmin(admin.ModelAdmin):
    """Advanced admin for mess bills"""

    list_display = [
        "student_link",
        "month_year_display",
        "amount_display",
        "status_badge",
        "due_date_display",
        "paid_date_display",
    ]
    list_filter = ["status", "year", "month", "created_at"]
    search_fields = ["student__name", "student__enrollment_no", "student__email"]
    readonly_fields = ["created_at", "bill_summary", "student_info_display"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Bill Information",
            {
                "fields": ("student", "student_info_display"),
            },
        ),
        (
            "Billing Period",
            {
                "fields": ("month", "year"),
                "classes": ("wide",),
            },
        ),
        (
            "Payment Details",
            {
                "fields": ("amount", "status", "due_date", "paid_date"),
                "classes": ("wide",),
            },
        ),
        (
            "Additional Information",
            {
                "fields": ("remarks", "bill_summary"),
                "classes": ("collapse", "wide"),
            },
        ),
        (
            "Audit Information",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )

    def student_link(self, obj):
        """Link to student detail"""
        url = reverse("admin:students_student_change", args=[obj.student.id])
        return format_html('<a href="{}">{}</a>', url, obj.student.name)

    student_link.short_description = "Student"

    def month_year_display(self, obj):
        """Format month and year"""
        return f"{obj.get_month_display()} {obj.year}"

    month_year_display.short_description = "Period"

    def amount_display(self, obj):
        """Format amount as currency"""
        return f"₹{obj.amount:,.2f}"

    amount_display.short_description = "Amount"

    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {"Pending": "#ffc107", "Paid": "#28a745", "Overdue": "#dc3545"}
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def due_date_display(self, obj):
        """Format due date"""
        from datetime import date, timedelta

        today = date.today()
        if obj.status == "Paid":
            return "—"
        if obj.due_date < today:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ {}</span>', obj.due_date
            )
        days_remaining = (obj.due_date - today).days
        if days_remaining <= 3:
            return format_html(
                '<span style="color: orange; font-weight: bold;">⏰ {} ({} days)</span>',
                obj.due_date,
                days_remaining,
            )
        return obj.due_date

    due_date_display.short_description = "Due Date"

    def paid_date_display(self, obj):
        """Display paid date or dash"""
        return obj.paid_date if obj.paid_date else "—"

    paid_date_display.short_description = "Paid On"

    def bill_summary(self, obj):
        """Display bill summary"""
        return mark_safe(
            f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                <p><strong>Student:</strong> {obj.student.name} ({obj.student.enrollment_no})</p>
                <p><strong>Amount:</strong> ₹{obj.amount:,.2f}</p>
                <p><strong>Status:</strong> {obj.status}</p>
                <p><strong>Due Date:</strong> {obj.due_date}</p>
                <p><strong>Paid Date:</strong> {obj.paid_date if obj.paid_date else "—"}</p>
            </div>
        """
        )

    bill_summary.short_description = "Bill Summary"

    def student_info_display(self, obj):
        """Display student additional info"""
        student = obj.student
        return mark_safe(
            f"""
            <div style="background: #f0f8ff; padding: 10px; border-radius: 5px;">
                <p><strong>Name:</strong> {student.name}</p>
                <p><strong>Email:</strong> {student.email}</p>
                <p><strong>Phone:</strong> {student.phone}</p>
                <p><strong>Enrollment:</strong> {student.enrollment_no}</p>
            </div>
        """
        )

    student_info_display.short_description = "Student Info"

    actions = ["mark_paid", "mark_pending", "mark_overdue"]

    def mark_paid(self, request, queryset):
        """Mark bills as paid"""
        updated = queryset.update(status="Paid")
        self.message_user(request, f"{updated} bills marked as paid.")

    mark_paid.short_description = "Mark selected as paid"

    def mark_pending(self, request, queryset):
        """Mark bills as pending"""
        updated = queryset.update(status="Pending")
        self.message_user(request, f"{updated} bills marked as pending.")

    mark_pending.short_description = "Mark selected as pending"

    def mark_overdue(self, request, queryset):
        """Mark bills as overdue"""
        updated = queryset.update(status="Overdue")
        self.message_user(request, f"{updated} bills marked as overdue.")

    mark_overdue.short_description = "Mark selected as overdue"

    def changelist_view(self, request, extra_context=None):
        """Add statistics to changelist view"""
        extra_context = extra_context or {}
        stats = MessBill.objects.aggregate(
            total_bills=Count("id"),
            total_amount=Sum("amount"),
            paid_amount=Sum("amount", filter=Q(status="Paid")),
            pending_amount=Sum("amount", filter=Q(status="Pending")),
            overdue_amount=Sum("amount", filter=Q(status="Overdue")),
        )
        extra_context["bill_stats"] = stats
        return super().changelist_view(request, extra_context=extra_context)
