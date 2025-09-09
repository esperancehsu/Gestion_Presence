from django.db import models
from django.utils import timezone
from .employe import Employe


class Rapport(models.Model):
    TYPE_CHOICES = [
        (1, "Journalier"),
        (2, "Hebdomadaire"),
        (3, "Mensuel"),
        (4, "Personnalisé"),
    ]

    employe = models.ForeignKey(Employe, related_name="rapports", on_delete=models.CASCADE)
    type = models.IntegerField(choices=TYPE_CHOICES)
    date_debut = models.DateField()
    date_fin = models.DateField()
    contenu = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rapport {self.get_type_display()} — {self.employe.nom} ({self.date_debut} → {self.date_fin})"