from django.db import models
from django.utils import timezone  
from .employe import Employe

# On crée la classe Presence qui représente la présence d'un employé un jour donné.
class Presence(models.Model):
    # La date de la présence, par défaut la date du jour au moment de la création.
    date = models.DateField(default=timezone.localdate)
    # L'heure d'arrivée (optionnelle au départ, peut être nulle).
    heure_arrivee = models.DateTimeField(null=True, blank=True)
    # L'heure de sortie (optionnelle aussi).
    heure_sortie = models.DateTimeField(null=True, blank=True)


    # Relation avec l'employé : une présence appartient à un employé.
    # related_name='presences' permet d'accéder aux présences depuis un Employe.
    employe = models.ForeignKey(Employe, related_name='presences', on_delete=models.CASCADE)

    # Méthode pour enregistrer l'heure d'arrivée à l'instant présent.
    def enregistrer_arrivee(self):
        self.heure_arrivee = timezone.now()
        self.save()

    # Méthode pour enregistrer l'heure de sortie à l'instant présent.
    def enregistrer_sortie(self):
        self.heure_sortie = timezone.now()
        self.save()

    # Affichage textuel d'une présence (exemple : "Jean Dupont - 2025-08-09").
    def __str__(self):
        return f"{self.employe.nom} - {self.date}"