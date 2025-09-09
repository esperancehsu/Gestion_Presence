from django.db import models
from django.utils import timezone  
from .employe import Employe

class Presence(models.Model):
    STATUS_CHOICES = [
        ("absent", "Absent"),
        ("arrive", "Arrivé"),
        ("sorti", "Sorti"),
    ]

    employe = models.ForeignKey(Employe, related_name="presences", on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate)
    heure_arrivee = models.DateTimeField(null=True, blank=True)
    heure_sortie = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=10, choices=STATUS_CHOICES, default="absent")
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("employe", "date")  # une présence par employé / jour

    def enregistrer_arrivee(self):
        if self.heure_arrivee:
            raise ValueError("Arrivée déjà enregistrée.")
        self.heure_arrivee = timezone.now()
        self.statut = "arrive"
        self.save(update_fields=["heure_arrivee", "statut", "updated_at"])

    def enregistrer_sortie(self):
        if not self.heure_arrivee:
            raise ValueError("Impossible d'enregistrer la sortie : arrivée non enregistrée.")
        if self.heure_sortie:
            raise ValueError("Sortie déjà enregistrée.")
        self.heure_sortie = timezone.now()
        self.statut = "sorti"
        self.save(update_fields=["heure_sortie", "statut", "updated_at"])

    def __str__(self):
        return f"{self.employe.nom} - {self.date} - {self.get_statut_display()}"


