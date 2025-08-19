from django.db import models
from django.utils import timezone  


class Rapport(models.Model):
    
    TYPE_CHOICES = [
        (1, 'Journalier'),
        (2, 'Hebdomadaire'),
        (3, 'Mensuel'),
        (4, 'Personnalisé'),
    ]
  
    type = models.IntegerField(choices=TYPE_CHOICES)

    date_debut = models.DateField()
  
    date_fin = models.DateField()
    
    contenu = models.TextField(blank=True)

    
    def __str__(self):
        # get_type_display() perme 
        return f"Rapport {self.get_type_display()} - {self.date_debut} à {self.date_fin}"
