from rest_framework import serializers
from api.models import Rapport


# Serializer pour la classe Rapport.
class RapportSerializer(serializers.ModelSerializer):
    employe_nom = serializers.CharField(source="employe.nom", read_only=True)

    class Meta:
        model = Rapport
        fields = ["id", "employe", "employe_nom", "type", "date_debut", "date_fin", "contenu", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at", "employe_nom"]

    def validate(self, attrs):
        if attrs["date_fin"] < attrs["date_debut"]:
            raise serializers.ValidationError({"date_fin": "La date de fin doit être après la date de début."})
        return attrs