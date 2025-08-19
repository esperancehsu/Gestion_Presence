from rest_framework import serializers
from api.models import Employe



# On crée un serializer pour la classe Employe.
class EmployeSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = Employe
    
        fields = ['id', 'nom', 'email', 'role', 'presences']