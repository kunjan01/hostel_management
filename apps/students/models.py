from django.contrib.auth.models import User
from django.db import models


class Student(models.Model):
    GENDER_CHOICES = [("M", "Male"), ("F", "Female"), ("O", "Other")]
    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("O+", "O+"),
        ("O-", "O-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
    ]
    COURSE_CHOICES = [
        ("BTech", "B.Tech"),
        ("MTech", "M.Tech"),
        ("MBA", "MBA"),
        ("MCA", "MCA"),
        ("BCA", "BCA"),
        ("BSc", "B.Sc"),
        ("MSc", "M.Sc"),
        ("BA", "B.A"),
        ("MA", "M.A"),
        ("BPharm", "B.Pharm"),
        ("Other", "Other"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    enrollment_no = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    course = models.CharField(max_length=20, choices=COURSE_CHOICES)
    year = models.IntegerField()
    branch = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)
    emergency_contact = models.CharField(max_length=15, blank=True)
    photo = models.ImageField(upload_to="students/photos/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    joining_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.enrollment_no})"

    class Meta:
        ordering = ["name"]
