    
from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.status == "admin"

from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import Group


# ==============================
#  RBAC (Role-Based Access Control)
# ==============================
class RBACPermission(BasePermission):
    """
    Permission basée sur les rôles (RBAC).
    Utilisation :
      - Dans une vue, définir `required_permission = "api.view_employe"`
      - Ou plusieurs via `required_permissions = ["api.add_presence", "api.change_presence"]`
    """
    required_permission = None
    required_permissions = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Si aucune permission spécifique n'est définie → accès libre
        if not self.required_permission and not self.required_permissions:
            return True

        # Normalise les permissions
        permissions = []
        if self.required_permission:
            permissions.append(self.required_permission)
        permissions += self.required_permissions

        # Vérifie les permissions Django
        for perm in permissions:
            if request.user.has_perm(perm):
                return True

        # Vérifie via les groupes (héritage des permissions)
        for group in request.user.groups.all():
            if any(perm.codename in [p.split('.')[-1] for p in permissions]
                   for perm in group.permissions.all()):
                return True

        return False


# ==============================
#  GBAC (Group-Based Access Control)
# ==============================
class GBACPermission(BasePermission):
    """
    Permission basée uniquement sur les groupes (GBAC).
    Exemple :
        class RapportView(APIView):
            permission_classes = [GBACPermission]
            allowed_groups = ["Managers", "RH"]
    """
    allowed_groups = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not self.allowed_groups:
            return True
        return request.user.groups.filter(name__in=self.allowed_groups).exists()


# ==============================
#  ABAC (Attribute-Based Access Control)
# ==============================
class ABACPermission(BasePermission):
    """
    Permission basée sur les attributs (ABAC).
    Exemple :
        - Admin → accès à tout
        - Employé → accès seulement à ses propres données
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True

        # Cas Employe → ne peut voir que ses données
        if hasattr(obj, "user"):  # modèle Employe
            return obj.user == request.user

        if hasattr(obj, "employe"):  # modèle Presence ou Rapport
            return obj.employe.user == request.user

        # Par défaut, refuse si non explicite
        return False


# ==============================
#  Helpers globaux
# ==============================
def user_has_permission(user, perm_codename: str) -> bool:
    """
    Vérifie si l'utilisateur possède une permission donnée,
    soit directement, soit via ses groupes.
    Exemple : user_has_permission(request.user, "api.delete_presence")
    """
    if not user or not user.is_authenticated:
        return False

    # Vérifie permissions directes
    if user.has_perm(perm_codename):
        return True

    # Vérifie permissions via groupes
    for group in user.groups.all():
        if any(perm.codename == perm_codename.split('.')[-1] for perm in group.permissions.all()):
            return True

    return False


def require_permission(user, perm_codename: str):
    """
    Helper pour lever une exception si l'utilisateur n'a pas la permission.
    """
    if not user_has_permission(user, perm_codename):
        raise PermissionDenied(f"Permission '{perm_codename}' requise.")
