from django.db import models

from apps.students.models import Student


class RoomBillQuerySet(models.QuerySet):
    """Custom QuerySet for RoomBill model"""

    def pending(self):
        """Get all pending bills"""
        return self.filter(status="Pending")

    def paid(self):
        """Get all paid bills"""
        return self.filter(status="Paid")

    def overdue(self):
        """Get overdue bills (due_date has passed)"""
        from django.utils import timezone

        today = timezone.now().date()
        return self.filter(status="Pending", due_date__lt=today)

    def for_month(self, month: int, year: int):
        """Get bills for specific month/year"""
        return self.filter(month=month, year=year)

    def for_student(self, student):
        """Get bills for a specific student"""
        return self.filter(student=student)

    def due_soon(self, days: int = 7):
        """Get bills due within specified days"""
        from django.utils import timezone

        today = timezone.now().date()
        future_date = today + timezone.timedelta(days=days)
        return self.filter(status="Pending", due_date__gte=today, due_date__lte=future_date)

    def with_related(self):
        """Optimize queries with select_related"""
        return self.select_related("student", "student__user", "room", "room__block")


class RoomBillManager(models.Manager):
    """Custom Manager for RoomBill model"""

    def get_queryset(self):
        return RoomBillQuerySet(self.model, using=self._db)

    def pending(self):
        return self.get_queryset().pending()

    def paid(self):
        return self.get_queryset().paid()

    def overdue(self):
        return self.get_queryset().overdue()

    def for_month(self, month: int, year: int):
        return self.get_queryset().for_month(month, year)

    def for_student(self, student):
        return self.get_queryset().for_student(student)

    def due_soon(self, days: int = 7):
        return self.get_queryset().due_soon(days)

    def with_related(self):
        return self.get_queryset().with_related()


class Block(models.Model):
    BLOCK_TYPE_CHOICES = [("Boys", "Boys"), ("Girls", "Girls"), ("Mixed", "Mixed")]
    name = models.CharField(max_length=50, unique=True)
    block_type = models.CharField(max_length=10, choices=BLOCK_TYPE_CHOICES, default="Boys")
    floors = models.IntegerField(default=1)
    warden_name = models.CharField(max_length=100, blank=True)
    warden_phone = models.CharField(max_length=15, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Block {self.name}"

    def total_rooms(self):
        return self.room_set.count()

    def available_rooms(self):
        return self.room_set.filter(status="Available").count()

    def occupied_rooms(self):
        return self.room_set.filter(status="Occupied").count()


class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ("Single", "Single Occupancy"),
        ("Double", "Double Occupancy"),
        ("Triple", "Triple Occupancy"),
        ("Dormitory", "Dormitory"),
    ]
    STATUS_CHOICES = [
        ("Available", "Available"),
        ("Occupied", "Occupied"),
        ("Maintenance", "Under Maintenance"),
        ("Reserved", "Reserved"),
    ]

    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10)
    floor = models.IntegerField(default=1)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default="Double")
    capacity = models.IntegerField(default=2)
    monthly_rent = models.DecimalField(max_digits=8, decimal_places=2, default=3000.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Available")
    has_ac = models.BooleanField(default=False)
    has_wifi = models.BooleanField(default=True)
    has_attached_bathroom = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Block {self.block.name} - Room {self.room_number}"

    def current_occupants(self):
        return self.roomallocation_set.filter(status="Active").count()

    def available_beds(self):
        return self.capacity - self.current_occupants()

    class Meta:
        unique_together = ["block", "room_number"]
        ordering = ["block", "room_number"]


class RoomAllocation(models.Model):
    STATUS_CHOICES = [("Active", "Active"), ("Vacated", "Vacated"), ("Transferred", "Transferred")]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    allocation_date = models.DateField(auto_now_add=True)
    vacating_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} -> {self.room}"

    class Meta:
        ordering = ["-allocation_date"]


class RoomBill(models.Model):
    """Monthly hostel room billing for each student"""

    STATUS_CHOICES = [("Pending", "Pending"), ("Paid", "Paid"), ("Overdue", "Overdue")]
    MONTH_CHOICES = [
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    month = models.IntegerField(choices=MONTH_CHOICES)
    year = models.IntegerField()
    room_rent = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Apply custom manager
    objects = RoomBillManager()

    def __str__(self):
        return f"{self.student.name} - Room Bill {self.get_month_display()} {self.year}"

    class Meta:
        unique_together = ["student", "month", "year"]
        ordering = ["-year", "-month"]
        indexes = [
            models.Index(fields=["student", "month", "year"]),
            models.Index(fields=["status", "year"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["due_date"]),
        ]
