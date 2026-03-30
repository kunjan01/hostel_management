from django.contrib import admin
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.html import format_html

from .models import Block, Room, RoomAllocation, RoomBill


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    """Admin for hostel blocks"""

    list_display = [
        "name_display",
        "block_type_badge",
        "floors",
        "warden_display",
        "occupancy_display",
        "is_active_badge",
    ]
    list_filter = ["block_type", "is_active", "created_at"]
    search_fields = ["name", "warden_name", "warden_phone"]
    readonly_fields = ["created_at", "block_statistics"]

    fieldsets = (
        (
            "Block Information",
            {
                "fields": ("name", "block_type", "floors"),
            },
        ),
        (
            "Warden Information",
            {
                "fields": ("warden_name", "warden_phone"),
                "classes": ("wide",),
            },
        ),
        (
            "Additional Details",
            {
                "fields": ("description", "is_active", "created_at", "block_statistics"),
                "classes": ("wide",),
            },
        ),
    )

    def name_display(self, obj):
        """Display block name with link"""
        url = reverse("admin:hostel_block_change", args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.name)

    name_display.short_description = "Block Name"

    def block_type_badge(self, obj):
        """Display type as badge"""
        colors = {"Boys": "#0099ff", "Girls": "#ff0099", "Mixed": "#99ff00"}
        color = colors.get(obj.block_type, "#cccccc")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 4px;">{}</span>',
            color,
            obj.block_type,
        )

    block_type_badge.short_description = "Type"

    def warden_display(self, obj):
        """Display warden info"""
        if obj.warden_name:
            return format_html("{}<br><small>{}</small>", obj.warden_name, obj.warden_phone)
        return "—"

    warden_display.short_description = "Warden"

    def occupancy_display(self, obj):
        """Display occupancy status"""
        total = obj.total_rooms()
        occupied = obj.occupied_rooms()
        available = obj.available_rooms()
        percentage = (occupied / total * 100) if total > 0 else 0
        return format_html(
            '<div>{}/{} rooms<br><small style="color:#666;">{}% full</small></div>',
            occupied,
            total,
            int(percentage),
        )

    occupancy_display.short_description = "Occupancy"

    def is_active_badge(self, obj):
        """Display active status"""
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">✓</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗</span>')

    is_active_badge.short_description = "Active"

    def block_statistics(self, obj):
        """Display block statistics"""
        total = obj.total_rooms()
        occupied = obj.occupied_rooms()
        available = obj.available_rooms()
        percentage = (occupied / total * 100) if total > 0 else 0
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">'
            "<p><strong>Total Rooms:</strong> {}</p>"
            "<p><strong>Occupied:</strong> {} ({:.1f}%)</p>"
            "<p><strong>Available:</strong> {}</p>"
            "</div>",
            total,
            occupied,
            percentage,
            available,
        )

    block_statistics.short_description = "Statistics"


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Admin for rooms"""

    list_display = [
        "room_number_display",
        "block",
        "floor",
        "room_type_badge",
        "capacity_display",
        "monthly_rent_display",
        "occupancy_display",
        "status_badge",
    ]
    list_filter = ["block", "status", "room_type", "has_ac", "has_wifi"]
    search_fields = ["room_number", "block__name"]
    readonly_fields = ["created_at", "room_details"]

    fieldsets = (
        (
            "Room Information",
            {
                "fields": ("block", "room_number", "floor", "room_type", "capacity"),
            },
        ),
        (
            "Facilities",
            {
                "fields": ("has_ac", "has_wifi", "has_attached_bathroom"),
                "classes": ("wide",),
            },
        ),
        (
            "Financial",
            {
                "fields": ("monthly_rent",),
            },
        ),
        (
            "Status & Details",
            {
                "fields": ("status", "description", "created_at", "room_details"),
                "classes": ("wide",),
            },
        ),
    )

    def room_number_display(self, obj):
        """Display room number"""
        return f"{obj.block.name}-{obj.room_number}"

    room_number_display.short_description = "Room"

    def room_type_badge(self, obj):
        """Display room type as badge"""
        colors = {
            "Single": "#0099ff",
            "Double": "#99ff00",
            "Triple": "#ff9900",
            "Dormitory": "#ff0099",
        }
        color = colors.get(obj.room_type, "#cccccc")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_room_type_display(),
        )

    room_type_badge.short_description = "Type"

    def capacity_display(self, obj):
        """Display capacity"""
        current = obj.current_occupants()
        available = obj.available_beds()
        return format_html(
            '{}/{}<br><small style="color:{}">{} available</small>',
            current,
            obj.capacity,
            "green" if available > 0 else "red",
            available,
        )

    capacity_display.short_description = "Capacity"

    def monthly_rent_display(self, obj):
        """Format rent as currency"""
        return f"₹{obj.monthly_rent:,.2f}"

    monthly_rent_display.short_description = "Rent"

    def occupancy_display(self, obj):
        """Show current vs capacity"""
        return f"{obj.current_occupants()}/{obj.capacity}"

    occupancy_display.short_description = "Occupancy"

    def status_badge(self, obj):
        """Display status as badge"""
        colors = {
            "Available": "#28a745",
            "Occupied": "#0099ff",
            "Maintenance": "#ff9900",
            "Reserved": "#ffc107",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def room_details(self, obj):
        """Display room amenities"""
        amenities = []
        if obj.has_ac:
            amenities.append("🧊 AC")
        if obj.has_wifi:
            amenities.append("📡 WiFi")
        if obj.has_attached_bathroom:
            amenities.append("🚿 Attached Bathroom")

        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">'
            "<p><strong>Amenities:</strong> {}</p>"
            "<p><strong>Description:</strong> {}</p>"
            "</div>",
            ", ".join(amenities) if amenities else "None",
            obj.description or "—",
        )

    room_details.short_description = "Details"


@admin.register(RoomAllocation)
class RoomAllocationAdmin(admin.ModelAdmin):
    """Admin for room allocations"""

    list_display = [
        "student_display",
        "room_display",
        "allocation_date",
        "status_badge",
        "tenure_display",
    ]
    list_filter = ["status", "allocation_date", "room__block"]
    search_fields = ["student__name", "student__enrollment_no", "room__room_number"]
    readonly_fields = ["created_at", "allocation_details"]
    date_hierarchy = "allocation_date"

    fieldsets = (
        (
            "Allocation Information",
            {
                "fields": ("student", "room", "allocation_date"),
            },
        ),
        (
            "Vacating Information",
            {
                "fields": ("vacating_date", "status"),
            },
        ),
        (
            "Additional Details",
            {
                "fields": ("remarks", "created_at", "allocation_details"),
                "classes": ("wide",),
            },
        ),
    )

    def student_display(self, obj):
        """Display student with link"""
        url = reverse("admin:students_student_change", args=[obj.student.id])
        return format_html(
            '<a href="{}">{} ({})</a>', url, obj.student.name, obj.student.enrollment_no
        )

    student_display.short_description = "Student"

    def room_display(self, obj):
        """Display room with link"""
        url = reverse("admin:hostel_room_change", args=[obj.room.id])
        return format_html('<a href="{}">{}-{}</a>', url, obj.room.block.name, obj.room.room_number)

    room_display.short_description = "Room"

    def status_badge(self, obj):
        """Display status as badge"""
        colors = {"Active": "#28a745", "Vacated": "#6c757d", "Transferred": "#0099ff"}
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def tenure_display(self, obj):
        """Display length of stay"""
        from datetime import date

        if obj.vacating_date:
            days = (obj.vacating_date - obj.allocation_date).days
            return f"{days} days"
        else:
            days = (date.today() - obj.allocation_date).days
            return f"{days} days (ongoing)"

    tenure_display.short_description = "Tenure"

    def allocation_details(self, obj):
        """Display allocation summary"""
        from datetime import date

        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">'
            "<p><strong>Student:</strong> {}</p>"
            "<p><strong>Room:</strong> {}-{}</p>"
            "<p><strong>Allocated:</strong> {}</p>"
            "<p><strong>Vacated:</strong> {}</p>"
            "<p><strong>Status:</strong> {}</p>"
            "</div>",
            obj.student.name,
            obj.room.block.name,
            obj.room.room_number,
            obj.allocation_date,
            obj.vacating_date if obj.vacating_date else "—",
            obj.get_status_display(),
        )

    allocation_details.short_description = "Allocation Details"


@admin.register(RoomBill)
class RoomBillAdmin(admin.ModelAdmin):
    """Admin for room bills"""

    list_display = [
        "student_link",
        "month_year_display",
        "room_rent_display",
        "status_badge",
        "due_date",
        "paid_date_display",
    ]
    list_filter = ["status", "year", "month", "created_at"]
    search_fields = ["student__name", "student__enrollment_no"]
    readonly_fields = ["created_at", "bill_summary"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Bill Information",
            {
                "fields": ("student", "room", "month", "year"),
            },
        ),
        (
            "Payment Details",
            {
                "fields": ("room_rent", "status", "due_date", "paid_date"),
                "classes": ("wide",),
            },
        ),
        (
            "Additional Information",
            {
                "fields": ("remarks", "created_at", "bill_summary"),
                "classes": ("wide",),
            },
        ),
    )

    def student_link(self, obj):
        """Student with link"""
        url = reverse("admin:students_student_change", args=[obj.student.id])
        return format_html('<a href="{}">{}</a>', url, obj.student.name)

    student_link.short_description = "Student"

    def month_year_display(self, obj):
        """Format month and year"""
        return f"{obj.get_month_display()} {obj.year}"

    month_year_display.short_description = "Period"

    def room_rent_display(self, obj):
        """Format as currency"""
        return f"₹{obj.room_rent:,.2f}"

    room_rent_display.short_description = "Rent"

    def status_badge(self, obj):
        """Status as badge"""
        colors = {"Pending": "#ffc107", "Paid": "#28a745", "Overdue": "#dc3545"}
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def paid_date_display(self, obj):
        """Display paid date or dash"""
        return obj.paid_date if obj.paid_date else "—"

    paid_date_display.short_description = "Paid On"

    def bill_summary(self, obj):
        """Bill summary view"""
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">'
            "<p><strong>Amount:</strong> ₹{:,.2f}</p>"
            "<p><strong>Period:</strong> {} {}</p>"
            "<p><strong>Status:</strong> {}</p>"
            "<p><strong>Due:</strong> {}</p>"
            "</div>",
            obj.room_rent,
            obj.get_month_display(),
            obj.year,
            obj.get_status_display(),
            obj.due_date,
        )

    bill_summary.short_description = "Bill Summary"

    actions = ["mark_paid", "mark_pending"]

    def mark_paid(self, request, queryset):
        """Mark as paid bulk action"""
        updated = queryset.update(status="Paid")
        self.message_user(request, f"{updated} bills marked as paid.")

    mark_paid.short_description = "Mark selected as paid"

    def mark_pending(self, request, queryset):
        """Mark as pending bulk action"""
        updated = queryset.update(status="Pending")
        self.message_user(request, f"{updated} bills marked as pending.")

    mark_pending.short_description = "Mark selected as pending"
