

from rest_framework.exceptions import PermissionDenied, ValidationError
from .permissions import RBACPermission, ABACPermission, GBACPermission
from rest_framework.permissions import IsAuthenticated




class PermissionMixin:
    """
    Mixin DRY pour appliquer RBAC + ABAC + GBAC sur n'importe quelle vue DRF.

    Usage :
        class MaVue(PermissionMixin, generics.ListCreateAPIView):
            required_permission = "can_view_reports"
            allowed_groups = ["Managers", "RH"]  # facultatif, pour GBAC
            abac_check = True  # facultatif, par défaut True pour object-level
    """

    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = None
    required_permissions = []
    allowed_groups = []
    abac_check = True  # On appliquer ABAC sur les objets (RetrieveUpdateDestroy)

    """
    
      def get_queryset(self):
        
        #Filtre automatique selon RBAC + ABAC + GBAC
        
        user = self.request.user

        # RBAC : admin / manager → accès complet
        if RBACPermission().has_permission(self.request, self):
            qs = super().get_queryset()
        else:
            # Staff → restreint aux objets liés à l'utilisateur
            qs = super().get_queryset()
            # ABAC filtrage : objets liés à user
            if hasattr(qs.model, "user"):
                qs = qs.filter(user=user)
            elif hasattr(qs.model, "employe"):
                qs = qs.filter(employe__user=user)
        return qs
    
    """
    
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()  # ← On part du queryset de la vue (déjà optimisé)

        if RBACPermission().has_permission(self.request, self):
            return qs

        if hasattr(qs.model, "user"):
            qs = qs.filter(user=user)
        elif hasattr(qs.model, "employe"):
            qs = qs.filter(employe__user=user)

        return qs

    def perform_create(self, serializer):
        """
        RBAC + ABAC lors de la création
        """
        user = self.request.user

        if RBACPermission().has_permission(self.request, self):
            # Admin / manager → création libre
            serializer.save()
        else:
            # Staff → forcer l'employe lié
            employe = getattr(user, "employe", None)
            if not employe:
                raise ValidationError(
                    "Votre compte n'est pas associé à un employé. Contactez l'administrateur."
                )
            serializer.save(employe=employe)

    def get_object(self):
        """
        RBAC + ABAC lors de Retrieve/Update/Destroy
        """
        obj = super().get_object()

        # ABAC : l'utilisateur ne peut accéder qu'à ses objets
        if self.abac_check and not ABACPermission().has_object_permission(self.request, self, obj):
            raise PermissionDenied("Vous n'avez pas la permission d'accéder à cet objet.")

        return obj
