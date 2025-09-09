from rest_framework import serializers
from api.models import Employe



# On crée un serializer pour la classe Employe.
class EmployeSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Employe
        fields = ["id", "user", "user_username", "nom", "poste", "telephone", "email", "created_at", "updated_at"]
        read_only_fields = ["user","created_at", "updated_at", "user_username"]

  