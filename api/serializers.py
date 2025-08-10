from rest_framework import serializers
from .models import Employe, Presence, Rapport

# On crée un serializer pour la classe Presence,
# qui va permettre de transformer un objet Presence en JSON et vice versa.
class PresenceSerializer(serializers.ModelSerializer):
    class Meta:
        # On indique le modèle lié à ce serializer.
        model = Presence
        # On inclut tous les champs du modèle.
        fields = '__all__'
        
        read_only_fields = ('heure_arrivee', 'heure_sortie', 'date') 

# On crée un serializer pour la classe Employe.
class EmployeSerializer(serializers.ModelSerializer):
 
    presences = PresenceSerializer(many=True, read_only=True)

    class Meta:
        model = Employe
    
        fields = ['id', 'nom', 'email', 'role', 'presences']

# Serializer pour la classe Rapport.
class RapportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rapport
        # On inclut tous les champs.
        fields = '__all__'
