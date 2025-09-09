from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import Group

# ==============================
# 1. RBAC (Role-Based Access Control)
# ==============================

# Mapping centralisé : quel rôle possède quelles permissions ?
ROLE_PERMISSIONS = {
    "admin": {
        "can_view_all_employees",
        "can_create_employee",
        "can_manage_employee",
        "can_view_reports",
        "can_manage_reports",
        "can_manage_presence",
    },
    "staff": {
        "can_view_self",
        "can_create_presence",
    },
    "manager": {
        "can_view_all_employees",
        "can_view_reports",
        "can_manage_presence",
    },
}

class RBACPermission(BasePermission):
    """
    Permission basée sur les rôles (RBAC).
    Usage dans une vue :
        required_permission = "can_manage_employee"
    """

    required_permission = None
    required_permissions = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Permissions déclarées dans la vue
        perms = []
        if self.required_permission:
            perms.append(self.required_permission)
        perms += getattr(view, "required_permissions", [])

        if not perms:
            return True  # accès libre si rien n’est défini

        # Vérifie via le rôle (attribut custom User.role)
        user_role = getattr(request.user, "role", None)
        if user_role and user_role in ROLE_PERMISSIONS:
            for perm in perms:
                if perm in ROLE_PERMISSIONS[user_role]:
                    return True

        # Vérifie via les permissions Django
        for perm in perms:
            if request.user.has_perm(perm):
                return True

        # Vérifie via les groupes liés
        for group in request.user.groups.all():
            if any(perm.codename in [p.split('.')[-1] for p in perms]
                   for perm in group.permissions.all()):
                return True

        return False


# ==============================
# 2. GBAC (Group-Based Access Control)
# ==============================
class GBACPermission(BasePermission):
    """
    Permission basée uniquement sur les groupes.
    Usage dans une vue :
        allowed_groups = ["Managers", "RH"]
    """

    allowed_groups = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        allowed_groups = getattr(view, "allowed_groups", self.allowed_groups)
        if not allowed_groups:
            return True

        return request.user.groups.filter(name__in=allowed_groups).exists()


# ==============================
# 3. ABAC (Attribute-Based Access Control)
# ==============================
class ABACPermission(BasePermission):
    """
    Permission basée sur les attributs de l’utilisateur ou de l’objet.
    Exemple :
      - Admin → accès total
      - Employé → accès à ses propres données
    """

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "role", None) == "admin":
            return True

        # Cas Employe → accès seulement à ses propres données
        if hasattr(obj, "user"):  # modèle Employe
            return obj.user == request.user

        if hasattr(obj, "employe"):  # modèle Presence ou Rapport
            return obj.employe.user == request.user

        return False


# ==============================
# 4. Helpers globaux
# ==============================
def user_has_permission(user, perm_codename: str) -> bool:
    """
    Vérifion si un utilisateur possède une permission donnée
    (directe, par rôle, ou par groupe).
    """
    if not user or not user.is_authenticated:
        return False

    # Vérifie permissions Django
    if user.has_perm(perm_codename):
        return True

    # Vérifie via rôle (RBAC)
    user_role = getattr(user, "role", None)
    if user_role and user_role in ROLE_PERMISSIONS:
        if perm_codename in ROLE_PERMISSIONS[user_role]:
            return True

    # Vérifie via groupes
    for group in user.groups.all():
        if any(perm.codename == perm_codename.split('.')[-1] for perm in group.permissions.all()):
            return True

    return False


def require_permission(user, perm_codename: str):
    """Lève une exception si l’utilisateur n’a pas la permission."""
    if not user_has_permission(user, perm_codename):
        raise PermissionDenied(f"Permission '{perm_codename}' requise.")
