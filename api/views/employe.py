# core/views.py
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from api.models import Employe
from api.serializers import EmployeSerializer
from core.mixins import PermissionMixin
from rest_framework.permissions import IsAuthenticated
from users.authentication import JWTAuthentication


class EmployeListCreateAPIView(PermissionMixin, generics.ListCreateAPIView):
    """
    List et création d'employés.
    Permissions :
    - Staff → voit/crée seulement son propre profil.
    - RH/Manager/Admin → voit/crée tous les profils.
    """
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().select_related('user')  

        # Si l'utilisateur a la permission de voir tous les employés → accès complet
        if user.has_perm("api.can_view_all_employees"):
            return qs

        # Sinon, seulement son propre employé
        return qs.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user

        # Vérifie si un employé existe déjà pour cet utilisateur
        if Employe.objects.filter(user=user).exists():
            raise ValidationError({
                "user": ["Un employé existe déjà pour cet utilisateur."]
            })

        # Vérifie la permission de gestion des employés
        if not user.has_perm("api.can_manage_employee"):
            raise PermissionDenied("Vous n'avez pas la permission de créer un employé.")

        serializer.save()


class EmployeRetrieveUpdateDestroyAPIView(PermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve / Update / Destroy d'un employé.
    Permissions :
    - Staff → accès seulement à son propre profil.
    - RH/Manager/Admin → accès à tous les profils.
    """
    serializer_class = EmployeSerializer
    queryset = Employe.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().select_related('user')  # ← Optimisation N+1

        if user.has_perm("api.can_view_all_employees"):
            return qs
        return qs.filter(user=user)

    def perform_update(self, serializer):
        user = self.request.user
        employe = self.get_object()

        # Vérifie la permission
        if not user.has_perm("api.can_manage_employee"):
            raise PermissionDenied("Vous n'avez pas la permission de modifier cet employé.")

        # Si ce n'est pas un admin/RH, l'utilisateur ne peut modifier que son propre profil
        if not (user.is_admin or user.is_rh) and employe.user != user:
            raise PermissionDenied("Vous ne pouvez modifier que votre propre profil.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        # Vérifie la permission
        if not user.has_perm("api.can_manage_employee"):
            raise PermissionDenied("Vous n'avez pas la permission de supprimer cet employé.")

        # Si ce n'est pas un admin/RH, l'utilisateur ne peut supprimer que son propre profil
        if not (user.is_admin or user.is_rh) and instance.user != user:
            raise PermissionDenied("Vous ne pouvez supprimer que votre propre profil.")

        instance.delete()