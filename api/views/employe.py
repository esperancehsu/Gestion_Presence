# core/views.py
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from api.models import Employe
from api.serializers import EmployeSerializer
from core.mixins import PermissionMixin

# -------------------------
# Employe Views avec PermissionMixin
# -------------------------
class EmployeListCreateAPIView(PermissionMixin, generics.ListCreateAPIView):
    """
    List et création d'employés.
    RBAC : admin/manager → accès complet
    Staff → accès limité à son propre profil
    """

    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer
    queryset = Employe.objects.all()
    required_permission = "can_view_all_employees"  # RBAC
    allowed_groups = ["Managers", "RH"]  # GBAC facultatif

    def get_queryset(self):
        """
        DRY : PermissionMixin filtre automatiquement via RBAC + ABAC + GBAC
        """
        return super().get_queryset()

    

    def perform_create(self, serializer):
        # Vérifie si un employé existe déjà pour cet utilisateur
        if Employe.objects.filter(user=self.request.user).exists():
            raise ValidationError({
                "user": ["Un employé existe déjà pour cet utilisateur."]
            })

        # Vérifie si l'utilisateur est Staff
        if self.request.user.groups.filter(name="Staff").exists():
            raise PermissionDenied("Un staff ne peut pas créer d'autres employés.")

        # Sauvegarde l'employé avec l'utilisateur courant
        serializer.save(user=self.request.user)


class EmployeRetrieveUpdateDestroyAPIView(PermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve / Update / Destroy d'un employé.
    RBAC : admin/manager → accès complet
    Staff → accès seulement à ses propres données (ABAC)
    """
    serializer_class = EmployeSerializer
    required_permission = "can_manage_employee"  # RBAC
    allowed_groups = ["Managers"]  # GBAC facultatif
    abac_check = True  # appliquer ABAC sur l'objet

    queryset = Employe.objects.all()
