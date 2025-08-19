from rest_framework import serializers
from api.models import Rapport


# Serializer pour la classe Rapport.
class RapportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rapport
        # On inclut tous les champs.
        fields = '__all__'