from rest_framework import serializers
from api.models import Presence



# On crée un serializer pour la classe Presence,
# qui va permettre de transformer un objet Presence en JSON et vice versa.
class PresenceSerializer(serializers.ModelSerializer):
    class Meta:
        # On indique le modèle lié à ce serializer.
        model = Presence
        # On inclut tous les champs du modèle.
        fields = '__all__'
        
        read_only_fields = ('heure_arrivee', 'heure_sortie', 'date') 




