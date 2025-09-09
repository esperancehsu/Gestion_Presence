
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Utilisateur personnalisé avec un champ `role`.
    Rôles utilisés dans RBAC : admin, staff, manager...
    """
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("staff", "Staff"),
        ("manager", "Manager"),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="staff")

    def __str__(self):
        return f"{self.username} - ({self.role})"
