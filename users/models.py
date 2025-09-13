from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("staff", "Staff"),     
        ("manager", "Manager"), 
        ("rh", "RH"),            
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="staff")

    def __str__(self):
        return f"{self.username} - ({self.role})"

    @property
    def is_admin(self):
        return self.role == "admin" or self.is_superuser

    @property
    def is_staff_member(self):
        return self.role == "staff"

    @property
    def is_manager(self):
        return self.role == "manager"

    @property
    def is_rh(self):
        return self.role == "rh"