# core/views.py (suite)
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from api.models import Rapport
from api.serializers import RapportSerializer
from core.mixins import PermissionMixin
from rest_framework.permissions import IsAuthenticated
from users.authentication import JWTAuthentication

# -------------------------
# Rapport Views — MISES À JOUR
# -------------------------
class RapportListCreateAPIView(PermissionMixin, generics.ListCreateAPIView):
    """
    List et création de rapports.
    Permissions :
    - Staff → voit/crée seulement ses propres rapports.
    - Manager/RH/Admin → voit/crée tous les rapports.
    """
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().select_related('employe__user')  # ← Optimisation N+1

        # Si l'utilisateur a la permission de voir tous les rapports → accès complet
        if user.has_perm("api.can_view_all_reports"):
            return qs

        # Sinon, seulement ses propres rapports
        return qs.filter(employe__user=user)

    def perform_create(self, serializer):
        user = self.request.user

        # Vérifie la permission de génération de rapports
        if not user.has_perm("api.can_generate_reports"):
            raise PermissionDenied("Vous n'avez pas la permission de générer des rapports.")

        # Si admin/manager/RH → création libre
        if user.is_admin or user.is_manager or user.is_rh:
            serializer.save()
            return

        # Staff : forcer l'employé lié
        employe = getattr(user, "employe", None)
        if not employe:
            raise ValidationError("Votre compte n'est pas associé à un employé. Contactez l'administrateur.")

        serializer.save(employe=employe)


class RapportRetrieveUpdateDestroyAPIView(PermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve / Update / Destroy d'un rapport.
    Permissions :
    - Staff → accès seulement à ses propres rapports.
    - Manager/RH/Admin → accès à tous les rapports.
    """
    serializer_class = RapportSerializer
    queryset = Rapport.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().select_related('employe__user')  # ← Optimisation N+1

        if user.has_perm("api.can_view_all_reports"):
            return qs
        return qs.filter(employe__user=user)

    def perform_update(self, serializer):
        user = self.request.user

        # Vérifie la permission
        if not user.has_perm("api.can_generate_reports"):
            raise PermissionDenied("Vous n'avez pas la permission de modifier ce rapport.")

        # Si admin/manager/RH → modification libre
        if user.is_admin or user.is_manager or user.is_rh:
            serializer.save()
            return

        # Staff : ne peut modifier que ses propres rapports
        rapport = self.get_object()
        if rapport.employe.user != user:
            raise PermissionDenied("Vous ne pouvez modifier que vos propres rapports.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        # Vérifie la permission
        if not user.has_perm("api.can_generate_reports"):
            raise PermissionDenied("Vous n'avez pas la permission de supprimer ce rapport.")

        # Seul un admin peut supprimer (ou RH si tu veux)
        if not user.is_admin:
            raise PermissionDenied("Seul l'administrateur peut supprimer un rapport.")

        instance.delete()