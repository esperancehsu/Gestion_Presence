from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import Group

#admin,staff, manager
RolePerimissions = {
    "admin" :{
        "peut_voir_tous_les_employes",
        "peut_creer_employe",
        "peut_gerer_employe",
        "peut_voir_rapports",
        "peut_gerer_rapports",
        "peut_gerer_presence",
    },
    "staff" :{
        "peut_voir_son_profil",
        "peut_creer_presence",
    },
    "manager" :{
        "peut_voir_tous_les_employes",
        "peut_voir_rapports",
        "peut_gerer_presence",
    },
}

class RBACPermission(BasePermission):
    def has_permission(self, request, view):
         user = request.user
         if not user or not user.authenticated:
            return False
         
         perms = []