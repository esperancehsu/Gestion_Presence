# core/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Employe(models.Model):
    # Lier l'employé au User pour centraliser le rôle et l'authentification
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employe")
    nom = models.CharField(max_length=150)
    poste = models.CharField(max_length=150, blank=True)
    telephone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.nom or self.user.username


