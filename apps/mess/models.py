from django.db import models

from apps.students.models import Student


class MessBillQuerySet(models.QuerySet):
    """Custom QuerySet for MessBill model"""

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
        return self.select_related("student", "student__user")


class MessBillManager(models.Manager):
    """Custom Manager for MessBill model"""

    def get_queryset(self):
        return MessBillQuerySet(self.model, using=self._db)

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


class MessMenu(models.Model):
    DAY_CHOICES = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ]
    MEAL_CHOICES = [
        ("Breakfast", "Breakfast"),
        ("Lunch", "Lunch"),
        ("Snacks", "Snacks"),
        ("Dinner", "Dinner"),
    ]

    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    meal = models.CharField(max_length=15, choices=MEAL_CHOICES)
    items = models.TextField()
    timing = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.day} - {self.meal}"

    class Meta:
        unique_together = ["day", "meal"]
        ordering = ["day", "meal"]


class MessRegistration(models.Model):
    PLAN_CHOICES = [
        ("Full", "Full Day (B+L+S+D)"),
        ("Lunch_Dinner", "Lunch + Dinner"),
        ("Breakfast_Lunch", "Breakfast + Lunch"),
    ]

    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="Full")
    monthly_charge = models.DecimalField(max_digits=8, decimal_places=2, default=3500.00)
    registration_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.student.name} - {self.plan}"


class MessBill(models.Model):
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
    month = models.IntegerField(choices=MONTH_CHOICES)
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Apply custom manager
    objects = MessBillManager()

    def __str__(self):
        return f"{self.student.name} - {self.get_month_display()} {self.year}"

    class Meta:
        unique_together = ["student", "month", "year"]
        ordering = ["-year", "-month"]
        indexes = [
            models.Index(fields=["student", "month", "year"]),
            models.Index(fields=["status", "year"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["status"]),
        ]
