from django.db import models

from apps.students.models import Student


class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ("Room", "Room Issue"),
        ("Mess", "Mess Issue"),
        ("Water", "Water Supply"),
        ("Electricity", "Electricity"),
        ("WiFi", "WiFi Issue"),
        ("Cleanliness", "Cleanliness"),
        ("Security", "Security"),
        ("Other", "Other"),
    ]
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
        ("Rejected", "Rejected"),
    ]
    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
        ("Critical", "Critical"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="Medium")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    admin_remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.name} - {self.subject[:50]}"

    class Meta:
        ordering = ["-created_at"]
