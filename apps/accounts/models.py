from django.contrib.auth.models import User
from django.db import models


class WardenProfile(models.Model):
    """Links a User account to one or more Blocks as a Warden."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="warden_profile")
    blocks = models.ManyToManyField("hostel.Block", blank=True, related_name="wardens")
    phone = models.CharField(max_length=15, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Warden: {self.user.get_full_name() or self.user.username}"

    def get_blocks(self):
        return self.blocks.filter(is_active=True)
