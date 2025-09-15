# core/views.py
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from api.models import Employe
from api.serializers import EmployeSerializer
from core.mixins import PermissionMixin
from rest_framework.permissions import IsAuthenticated
from users.authentication import JWTAuthentication
from rest_framework import serializers  

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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        # Vérifie la permission de base
        if not self.request.user.has_perm("api.can_manage_employee"):
            raise PermissionDenied("Vous n'avez pas la permission de créer un employé.")

        # Le serializer gère le reste (assignation de user, validation)
        serializer.save()

    def create(self, request, *args, **kwargs):
        """Override pour un meilleur feedback d'erreur"""
        try:
            return super().create(request, *args, **kwargs)
        except serializers.ValidationError as e:
            return Response({
                'error': 'Erreur de validation',
                'details': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Erreur serveur',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# core/views.py (suite)
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
        qs = super().get_queryset().select_related('user')

        if user.has_perm("api.can_view_all_employees"):
            return qs
        return qs.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_update(self, serializer):
        user = self.request.user
        employe = self.get_object()

        # Vérifie la permission de base
        if not user.has_perm("api.can_manage_employee"):
            raise PermissionDenied("Vous n'avez pas la permission de modifier cet employé.")

        # Vérifie si l'utilisateur peut modifier ce profil spécifique
        if not (getattr(user, 'is_admin', False) or getattr(user, 'is_rh', False)):
            if employe.user != user:
                raise PermissionDenied("Vous ne pouvez modifier que votre propre profil.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if not user.has_perm("api.can_manage_employee"):
            raise PermissionDenied("Vous n'avez pas la permission de supprimer cet employé.")

        # Seul un admin/RH peut supprimer un employé d'un autre
        if not (getattr(user, 'is_admin', False) or getattr(user, 'is_rh', False)):
            if instance.user != user:
                raise PermissionDenied("Vous ne pouvez supprimer que votre propre profil.")

        instance.delete()