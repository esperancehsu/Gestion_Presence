from django.db import models
from django.utils import timezone   

class Employe(models.Model):    
    
    ROLES = [
        ('admin', 'Administrateur'),
        ('staff', 'Employé'),
    ]
  
    nom = models.CharField(max_length=100)
  
    email = models.EmailField(unique=True)

    # ici , on a le rôle de l'employé, 'admin' ou 'staff'
    role = models.CharField(max_length=20, choices=ROLES, default='staff')

    
    def voir_historique(self):
        

        # On utilise related_name 'presences'  de le modèle Presence pour récupérer les présences.
        return self.presences.all()

    def __str__(self):
        return self.nom

    