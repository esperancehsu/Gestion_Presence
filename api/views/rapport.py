# core/views.py (suite)
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from api.models import Rapport
from api.serializers import RapportSerializer
from core.mixins import PermissionMixin
from rest_framework.permissions import IsAuthenticated
from users.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.response import Response




class RapportListCreateAPIView(PermissionMixin, generics.ListCreateAPIView):
    """
    List et création de rapports - VERSION CORRIGÉE
    """
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().select_related('employe__user')

        user_can_view_all = (
            getattr(user, 'is_admin', False) or 
            getattr(user, 'is_rh', False) or
            getattr(user, 'is_manager', False) or
            user.has_perm("api.can_view_all_reports")
        )

        if user_can_view_all:
            return qs

        # Sinon, seulement ses propres rapports
        return qs.filter(employe__user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        user = self.request.user

        if not user.has_perm("api.can_generate_reports"):
            raise PermissionDenied("Vous n'avez pas la permission de générer des rapports.")

        # Le serializer gère la logique d'assignation de l'employé
        serializer.save()

    def create(self, request, *args, **kwargs):
        """Override pour debugging"""
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({
                'error': 'Erreur de validation',
                'details': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Erreur serveur',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RapportRetrieveUpdateDestroyAPIView(PermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve / Update / Destroy d'un rapport - VERSION CORRIGÉE
    """
    serializer_class = RapportSerializer
    queryset = Rapport.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().select_related('employe__user')

        user_can_view_all = (
            getattr(user, 'is_admin', False) or 
            getattr(user, 'is_rh', False) or
            getattr(user, 'is_manager', False) or
            user.has_perm("api.can_view_all_reports")
        )

        if user_can_view_all:
            return qs
        return qs.filter(employe__user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_update(self, serializer):
        user = self.request.user

        if not user.has_perm("api.can_generate_reports"):
            raise PermissionDenied("Vous n'avez pas la permission de modifier ce rapport.")

        user_can_manage_all = (
            getattr(user, 'is_admin', False) or 
            getattr(user, 'is_rh', False) or
            getattr(user, 'is_manager', False)
        )

        if not user_can_manage_all:
            rapport = self.get_object()
            if rapport.employe.user != user:
                raise PermissionDenied("Vous ne pouvez modifier que vos propres rapports.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if not user.has_perm("api.can_generate_reports"):
            raise PermissionDenied("Vous n'avez pas la permission de supprimer ce rapport.")

        # Seul un admin peut supprimer
        if not getattr(user, 'is_admin', False):
            raise PermissionDenied("Seul l'administrateur peut supprimer un rapport.")

        instance.delete()