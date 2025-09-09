
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError

from api.models import Presence
from api.serializers import PresenceSerializer
from core.mixins import PermissionMixin



# -------------------------
# ----------------------------------------------- on code avec sourir :)
# -------------------------
class PresenceListCreateAPIView(PermissionMixin, generics.ListCreateAPIView):
    serializer_class = PresenceSerializer
    queryset = Presence.objects.all()
    required_permission = "can_manage_presence"  # RBAC
    allowed_groups = ["Managers", "RH"]         # GBAC
    abac_check = True

    def get_queryset(self):
        user = self.request.user
        #qs = super().get_queryset().order_by("-date", "-created_at")
        qs = super().get_queryset().select_related('employe__user').order_by("-date", "-created_at")
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        is_admin = getattr(user, "role", None) == "admin" or user.is_superuser

        if is_admin:
            # Admin / Manager → création libre
            serializer.save()
            return

        # Staff : on crée uniquement sa présence du jour
        employe = getattr(user, "employe", None)
        if not employe:
            raise ValidationError("Votre compte n'est pas associé à un employé.")

        today = timezone.localdate()
        if Presence.objects.filter(employe=employe, date=today).exists():
            raise ValidationError("Présence du jour déjà créée.")

        serializer.save(employe=employe, date=today)


# -------------------------
# Presence Retrieve / Update / Destroy
# -------------------------
class PresenceDetailAPIView(PermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PresenceSerializer
    queryset = Presence.objects.all()
    required_permission = "can_manage_presence"
    allowed_groups = ["Managers", "RH"]
    abac_check = True

    def perform_update(self, serializer):
        user = self.request.user
        is_admin = getattr(user, "role", None) == "admin" or user.is_superuser
        presence = self.get_object()

        if is_admin:
            serializer.save()
            return

        # Staff : uniquement sa présence du jour
        if presence.employe.user != user or presence.date != timezone.localdate():
            raise PermissionDenied("Vous ne pouvez modifier que votre présence du jour.")

        serializer.save()


    def perform_destroy(self, instance):
        user = self.request.user
        is_admin = getattr(user, "role", None) == "admin" or user.is_superuser
        if not is_admin:
            raise PermissionDenied("Seul l'administrateur peut supprimer une présence.")
        instance.delete()

    def get_queryset(self):
       return super().get_queryset().select_related('employe__user').order_by("-date", "-created_at")


# -------------------------
# Présence Arrivée / Sortie (spécifique)
# -------------------------
class PresenceArriveeAPIView(PermissionMixin, APIView):
    required_permission = "can_manage_presence"
    allowed_groups = ["Managers", "RH"]

    def post(self, request, pk):
        presence = Presence.objects.select_related('employe__user').filter(pk=pk).first()
        if not presence:
            raise NotFound("Présence introuvable.")

        user = request.user
        is_admin = getattr(user, "role", None) == "admin" or user.is_superuser

        if not is_admin and (not hasattr(user, "employe") or presence.employe.user != user or presence.date != timezone.localdate()):
            raise PermissionDenied("Vous ne pouvez marquer l'arrivée que pour votre propre présence du jour.")

        try:
            presence.enregistrer_arrivee()
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PresenceSerializer(presence, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PresenceSortieAPIView(PermissionMixin, APIView):
    required_permission = "can_manage_presence"
    allowed_groups = ["Managers", "RH"]

    def post(self, request, pk):
        presence = Presence.objects.select_related('employe__user').filter(pk=pk).first()
        if not presence:
            raise NotFound("Présence introuvable.")

        user = request.user
        is_admin = getattr(user, "role", None) == "admin" or user.is_superuser

        if not is_admin and (not hasattr(user, "employe") or presence.employe.user != user or presence.date != timezone.localdate()):
            raise PermissionDenied("Vous ne pouvez marquer la sortie que pour votre propre présence du jour.")

        try:
            presence.enregistrer_sortie()
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PresenceSerializer(presence, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
