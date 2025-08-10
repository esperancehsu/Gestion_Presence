from django.db import models
from django.utils import timezone

# On crée la classe Employe qui représente un employé dans l'entreprise.
class Employe(models.Model):
    # On définit une liste de rôles possibles pour un employé.
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
