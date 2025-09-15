# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from django.core.exceptions import ValidationError
import re

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer pour afficher les infos de l'utilisateur (lecture seule).
    """
    class Meta:
        model = User
        fields = ("id", "username", "email", "role")
        read_only_fields = ("id", "username", "email", "role")

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'inscription.
    - Les utilisateurs normaux ne peuvent s'inscrire qu'en tant que 'staff'.
    - Seuls les admin peuvent créer des utilisateurs avec d'autres rôles.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            #'role': {'required': False}  # Optionnel, par défaut 'staff'
        }

    def validate_password(self, value):
        """
        Valide la complexité du mot de passe :
        - Minimum 8 caractères
        - Au moins 1 majuscule
        - Au moins 1 chiffre
        - Au moins 1 caractère spécial
        """
        if len(value) < 8:
            raise ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        if not re.search(r'[A-Z]', value):
            raise ValidationError("Le mot de passe doit contenir au moins une majuscule.")
        if not re.search(r'\d', value):
            raise ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError("Le mot de passe doit contenir au moins un caractère spécial.")
        return value

    def validate_role(self, value):
        """
        Empêche un utilisateur non-admin de s'auto-promouvoir.
        """
        request = self.context.get('request')
        if request and not (getattr(request.user, 'is_admin', False) or request.user.is_superuser):
            if value != 'staff':
                raise serializers.ValidationError("Vous ne pouvez pas vous attribuer ce rôle.")
        return value

    def create(self, validated_data):
        """
        Crée un nouvel utilisateur.
        - Force le rôle à 'staff' si l'utilisateur n'est pas admin.
        """
        request = self.context.get('request')
        if request and not (getattr(request.user, 'is_admin', False) or request.user.is_superuser):
            validated_data['role'] = 'staff'

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'staff'),  # Par défaut 'staff'
        )
        return user

class LoginSerializer(serializers.Serializer):
    """
    Serializer pour le login.
    Accepte username ou email.
    """
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        # Cherche par email ou username
        if "@" in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
        else:
            user = User.objects.filter(username__iexact=identifier).first()

        # Vérifie l'authentification
        if not user or not user.check_password(password):
            raise serializers.ValidationError("Identifiant ou mot de passe invalide")

        # Vérifie que le compte est actif
        if not user.is_active:
            raise serializers.ValidationError("Compte désactivé")

        data['user'] = user
        return data