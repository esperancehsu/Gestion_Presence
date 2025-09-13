# api/models.py
from django.db import models
from django.utils import timezone
from .employe import Employe
from django.core.exceptions import ValidationError


class Rapport(models.Model):
    TYPE_CHOICES = [
        ('mensuel', 'Mensuel'),
        ('hebdomadaire', 'Hebdomadaire'),
        ('annuel', 'Annuel'),
        ('personnalise', 'Personnalisé'),
    ]

    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='rapports')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_debut = models.DateField()
    date_fin = models.DateField()
    contenu = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rapport"
        verbose_name_plural = "Rapports"
        ordering = ['-created_at']
        permissions = [
            ("can_generate_reports", "Peut générer des rapports"),
        ]

    def clean(self):
        if self.date_fin < self.date_debut:
            raise ValidationError("La date de fin doit être après la date de début.")

    def __str__(self):
        return f"Rapport {self.type} de {self.employe.nom}"
