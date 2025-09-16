# api/serializers.py
from rest_framework import serializers
from api.models import Employe
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer
import traceback
User = get_user_model()

class EmployeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=False
    )

    class Meta:
        model = Employe
        fields = [
            'id', 'user', 'user_id', 'nom', 'poste',
            'telephone', 'email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    


        def create(self, request, *args, **kwargs):
            try:
                return super().create(request, *args, **kwargs)
            except Exception as e:
                print(f"Erreur lors de la création: {e}")
                print(traceback.format_exc())
                raise


    def validate(self, data):
        request = self.context.get('request')
        if not request:
            return data

        # Si un user_id est fourni, vérifier que l'utilisateur a la permission
        if 'user' in data:
            if not (getattr(request.user, 'is_admin', False) or getattr(request.user, 'is_rh', False)):
                raise serializers.ValidationError("Vous ne pouvez pas spécifier un autre utilisateur.")
            
            # Vérifions que l'utilisateur n'a pas déjà un employé
            if Employe.objects.filter(user=data['user']).exists():
                raise serializers.ValidationError("Cet utilisateur a déjà un profil employé.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            return super().create(validated_data)

        # Si admin/RH a fourni un user_id → l'utiliser
        if 'user' in validated_data:
            return super().create(validated_data)

        # Sinon, assigner l'utilisateur courant (pour un staff)
        validated_data['user'] = request.user
        return super().create(validated_data)