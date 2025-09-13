# api/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()

class Employe(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employe')
    nom = models.CharField(max_length=100)
    poste = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        permissions = [
            ("can_manage_employee", "Peut gérer les employés"),
            ("can_view_all_employees", "Peut voir tous les employés"),
        ]

    def __str__(self):
        return f"{self.nom} - {self.poste}"

