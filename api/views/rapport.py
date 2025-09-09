

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from api.models import Rapport
from api.serializers import RapportSerializer
from core.mixins import PermissionMixin


# -------------------------
# ------------------------Toujours avec le sourire :)-----------------
# -------------------------
class RapportListCreateAPIView(PermissionMixin, generics.ListCreateAPIView):
    serializer_class = RapportSerializer
    required_permission = "can_manage_reports"  # RBAC
    allowed_groups = ["Managers", "RH"]         # GBAC
    abac_check = True

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().select_related("employe")
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        is_admin = getattr(user, "role", None) == "admin" or user.is_superuser

        if is_admin:
            # Admin / Manager → création libre
            serializer.save()
            return

        # Staff : forcer l'employe lié
        employe = getattr(user, "employe", None)
        if not employe:
            raise ValidationError("Votre compte n'est pas associé à un employé. Contactez l'administrateur.")
        serializer.save(employe=employe)


# -------------------------
# Rapport Retrieve / Update / Destroy
# -------------------------
class RapportRetrieveUpdateDestroyAPIView(PermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RapportSerializer
    queryset = Rapport.objects.all()
    required_permission = "can_manage_reports"
    allowed_groups = ["Managers", "RH"]
    abac_check = True

    def perform_update(self, serializer):
        user = self.request.user
        is_admin = getattr(user, "role", None) == "admin" or user.is_superuser
        if is_admin:
            serializer.save()
            return

        # Staff : ne peut modifier que ses propres rapports
        rapport = self.get_object()
        if rapport.employe.user != user:
            raise PermissionDenied("Vous ne pouvez modifier que vos propres rapports.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        is_admin = getattr(user, "role", None) == "admin" or user.is_superuser
        if not is_admin:
            raise PermissionDenied("Seul l'administrateur peut supprimer un rapport.")
        instance.delete()
