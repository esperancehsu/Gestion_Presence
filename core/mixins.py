# core/mixins.py
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from users.authentication import JWTAuthentication

class PermissionMixin:
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Si superuser ou admin → accès complet
        if user.is_superuser or user.is_admin:
            return super().get_queryset()

        qs = super().get_queryset()

        # Pour les modèles liés à un User (ex: Employe)
        if hasattr(qs.model, "user"):
            return qs.filter(user=user)

        # Pour les modèles liés à un Employe (ex: Presence, Rapport)
        if hasattr(qs.model, "employe"):
            return qs.filter(employe__user=user)

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        model_name = serializer.Meta.model.__name__.lower()

        
        permission_map = {
            "employe": "api.can_manage_employee",
            "presence": "api.can_manage_presence",
            "rapport": "api.can_generate_reports",
        }

        required_permission = permission_map.get(model_name)
        if not required_permission:
            raise PermissionDenied(f"Permission non définie pour le modèle {model_name}.")

        # Vérifie la permission
        if not user.has_perm(required_permission):
            raise PermissionDenied(f"Vous n'avez pas la permission de créer un {model_name}.")

        # Presence → assigne l'employé automatiquement
        if model_name == "presence":
            employe = getattr(user, "employe", None)
            if not employe:
                raise PermissionDenied("Votre compte n'est pas associé à un employé.")
            serializer.save(employe=employe)
        else:
            serializer.save()



from rest_framework.permissions import AllowAny

class IsAuthenticatedOrSwagger(AllowAny):
    """
    Autorise Swagger/Redoc sans auth, impose auth ailleurs.
    """
    def has_permission(self, request, view):
        path = request.path
        if (
            path.startswith("/swagger") or 
            path.startswith("/redoc") or 
            path.endswith("/swagger.json") or 
            path.endswith("/swagger.yaml")
        ):
            return True
        return request.user and request.user.is_authenticated
