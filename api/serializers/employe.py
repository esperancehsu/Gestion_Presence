# api/serializers.py
from rest_framework import serializers
from api.models import Employe
from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model


User = get_user_model()


class EmployeSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=False
    )
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Employe
        fields = [
            'id', 'user', 'user_id', 'user_username', 'user_email',
            'nom', 'poste', 'telephone', 'email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user_username', 'user_email']

    def validate(self, data):
        request = self.context.get('request')
        if request and not (request.user.is_admin or request.user.is_rh):
            if 'user' in data and data['user'] != request.user:
                raise serializers.ValidationError("Vous ne pouvez créer un profil que pour vous-même.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and not (request.user.is_admin or request.user.is_rh):
            validated_data['user'] = request.user
        return super().create(validated_data)



