from django.db import models
from django.utils import timezone
from .employe import Employe
from django.core.exceptions import ValidationError


class Presence(models.Model):
    STATUT_CHOICES = [
        ('absent', 'Absent'),
        ('arrive', 'Arrivé'),
        ('parti', 'Parti'),
    ]

    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='presences')
    date = models.DateField(default=timezone.localdate)
    heure_arrivee = models.TimeField(null=True, blank=True)
    heure_sortie = models.TimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='absent')
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Présence"
        verbose_name_plural = "Présences"
        unique_together = ['employe', 'date']
        ordering = ['-date', '-created_at']
        permissions = [
            ("can_manage_presence", "Peut gérer les présences"),
            ("can_view_all_reports", "Peut voir tous les rapports"),
        ]

    def clean(self):
        if self.heure_arrivee and self.heure_sortie:
            if self.heure_sortie <= self.heure_arrivee:
                raise ValidationError("L'heure de sortie doit être après l'heure d'arrivée.")

    def enregistrer_arrivee(self):
        """Enregistre l'heure d'arrivée avec l'heure exacte actuelle."""
        if self.heure_arrivee:
            raise ValueError("L'arrivée a déjà été enregistrée pour aujourd'hui.")
        
        now = timezone.localtime()
        self.heure_arrivee = now.time()
        self.statut = 'arrive'
        self.save(update_fields=['heure_arrivee', 'statut', 'updated_at'])
        return f"Arrivée enregistrée à {self.heure_arrivee.strftime('%H:%M:%S')}"

    def enregistrer_sortie(self):
        """Enregistre l'heure de sortie avec l'heure exacte actuelle."""
        if not self.heure_arrivee:
            raise ValueError("Vous devez d'abord enregistrer votre arrivée.")
        
        if self.heure_sortie:
            raise ValueError("La sortie a déjà été enregistrée pour aujourd'hui.")
        
        now = timezone.localtime()
        self.heure_sortie = now.time()
        self.statut = 'parti'
        self.save(update_fields=['heure_sortie', 'statut', 'updated_at'])
        return f"Sortie enregistrée à {self.heure_sortie.strftime('%H:%M:%S')}"

    def get_duree_travail(self):
        """Calcule la durée de travail en heures et minutes."""
        if self.heure_arrivee and self.heure_sortie:
            from datetime import datetime, timedelta
            arrivee = datetime.combine(self.date, self.heure_arrivee)
            sortie = datetime.combine(self.date, self.heure_sortie)
            duree = sortie - arrivee
            heures = duree.seconds // 3600
            minutes = (duree.seconds % 3600) // 60
            return f"{heures}h {minutes}min"
        return "En cours" if self.heure_arrivee else "Non calculable"

    def __str__(self):
        return f"Présence de {self.employe.nom} le {self.date}"