# views/presence.py - Version finale avec support complet pour les staff
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from django.utils import timezone
from django.db import transaction

from api.models import Presence, Employe
from api.serializers import PresenceSerializer
from users.authentication import JWTAuthentication


# VUES EXISTANTES : Liste et Détail des présences
class PresenceListCreateAPIView(generics.ListCreateAPIView):
    """Liste et création de toutes les présences."""
    queryset = Presence.objects.all()
    serializer_class = PresenceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().select_related('employe__user')

        # Seuls admin, manager, RH voient tout
        if user.is_admin or user.is_manager or user.is_rh:
            return qs
        # Sinon : uniquement sa propre présence
        try:
            return qs.filter(employe__user=user)
        except:
            return qs.none()

    def perform_create(self, serializer):
        user = self.request.user

        # Seuls les utilisateurs avec permission ou staff peuvent créer
        if not (user.has_perm("api.can_manage_presence") or user.role == 'staff'):
            raise PermissionDenied("Vous n'avez pas la permission de créer une présence.")

        try:
            employe = user.employe
            today = timezone.localdate()
            if Presence.objects.filter(employe=employe, date=today).exists():
                raise ValidationError("Vous avez déjà une présence pour aujourd'hui.")
            serializer.save(employe=employe)
        except Employe.DoesNotExist:
            raise ValidationError("Votre compte n'est pas associé à un employé.")


class PresenceDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification, suppression d'une présence."""
    serializer_class = PresenceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Presence.objects.select_related('employe__user')
        if user.is_admin or user.is_manager or user.is_rh:
            return qs
        return qs.filter(employe__user=user)

    def perform_update(self, serializer):
        user = self.request.user
        presence = self.get_object()

        if not user.has_perm("api.can_manage_presence"):
            if presence.employe.user != user or presence.date != timezone.localdate():
                raise PermissionDenied("Vous ne pouvez modifier que votre présence du jour.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not user.is_admin:
            raise PermissionDenied("Seul l'administrateur peut supprimer une présence.")
        instance.delete()


# POINTAGE POUR LES EMPLOYÉS (STAFF) - CORRIGÉ
class PresenceArriveeAPIView(APIView):
    """Marquer son arrivée – accessible aux staff sans permission globale."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        user = request.user

        if pk is None:
            # Mode auto : pointage personnel (pour staff)
            if user.role != 'staff':
                return Response({
                    "success": False,
                    "message": "Accès refusé : réservé aux employés."
                }, status=status.HTTP_403_FORBIDDEN)

            try:
                employe = user.employe
                today = timezone.localdate()
                presence, created = Presence.objects.get_or_create(
                    employe=employe,
                    date=today,
                    defaults={'statut': 'absent'}
                )
            except Employe.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "Votre compte n'est pas lié à un employé."
                }, status=status.HTTP_400_BAD_REQUEST)

        else:
            # Mode admin : gestion d'autrui
            if not user.has_perm("api.can_manage_presence"):
                raise PermissionDenied("Permission requise pour gérer les présences.")
            try:
                presence = Presence.objects.select_related('employe__user').get(pk=pk)
            except Presence.DoesNotExist:
                raise NotFound("Présence introuvable.")

        # Enregistrer l'arrivée
        try:
            with transaction.atomic():
                message = presence.enregistrer_arrivee()
        except ValueError as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PresenceSerializer(presence, context={"request": request})
        return Response({
            "success": True,
            "message": message,
            "presence": serializer.data
        }, status=status.HTTP_200_OK)


class PresenceSortieAPIView(APIView):
    """Marquer sa sortie – accessible aux staff."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        user = request.user

        if pk is None:
            # Pointage personnel
            if user.role != 'staff':
                return Response({
                    "success": False,
                    "message": "Accès refusé."
                }, status=status.HTTP_403_FORBIDDEN)

            try:
                employe = user.employe
                today = timezone.localdate()
                presence = Presence.objects.get(employe=employe, date=today)
            except Employe.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "Votre compte n'est pas lié à un employé."
                }, status=status.HTTP_400_BAD_REQUEST)
            except Presence.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "Aucune présence trouvée. Pointez d'abord votre arrivée."
                }, status=status.HTTP_404_NOT_FOUND)

        else:
            # Gestion par admin
            if not user.has_perm("api.can_manage_presence"):
                raise PermissionDenied("Permission requise.")
            try:
                presence = Presence.objects.get(pk=pk)
            except Presence.DoesNotExist:
                raise NotFound("Présence introuvable.")

        # Enregistrer la sortie
        try:
            with transaction.atomic():
                message = presence.enregistrer_sortie()
        except ValueError as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PresenceSerializer(presence, context={"request": request})
        return Response({
            "success": True,
            "message": message,
            "presence": serializer.data
        }, status=status.HTTP_200_OK)


# GESTION DE LA PRÉSENCE PERSONNELLE
class MaPresenceAPIView(APIView):
    """Créer ou récupérer sa propre présence."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            employe = user.employe
            today = timezone.localdate()
            try:
                presence = Presence.objects.get(employe=employe, date=today)
                serializer = PresenceSerializer(presence)
                return Response({
                    "success": True,
                    "presence": serializer.data,
                    "message": f"Pointage du {today.strftime('%d/%m/%Y')}"
                })
            except Presence.DoesNotExist:
                return Response({
                    "success": False,
                    "presence": None,
                    "message": "Pas de pointage aujourd'hui. Cliquez sur 'Pointer Arrivée'."
                })
        except Employe.DoesNotExist:
            return Response({
                "success": False,
                "message": "Votre compte n'est pas associé à un employé."
            }, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        user = request.user

        # Autorise staff à créer sa présence
        if not (user.has_perm("api.can_manage_presence") or user.role == 'staff'):
            raise PermissionDenied("Vous n'avez pas la permission.")

        try:
            employe = user.employe
            today = timezone.localdate()
            if Presence.objects.filter(employe=employe, date=today).exists():
                return Response({
                    "success": False,
                    "message": "Présence déjà créée."
                }, status=status.HTTP_400_BAD_REQUEST)

            presence = Presence.objects.create(employe=employe, date=today)
            serializer = PresenceSerializer(presence, context={"request": request})
            return Response({
                "success": True,
                "presence": serializer.data,
                "message": "Présence créée."
            }, status=status.HTTP_201_CREATED)

        except Employe.DoesNotExist:
            return Response({
                "success": False,
                "message": "Votre compte n'est pas lié à un employé."
            }, status=status.HTTP_400_BAD_REQUEST)


# STATS OPTIONNELLES
class PresenceStatsAPIView(APIView):
    """Statistiques de présence pour l'utilisateur connecté."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            employe = user.employe
            today = timezone.localdate()
            debut_semaine = today - timezone.timedelta(days=today.weekday())
            presences_semaine = Presence.objects.filter(
                employe=employe,
                date__gte=debut_semaine,
                date__lte=today
            )

            stats = {
                "jours_travailles_semaine": presences_semaine.exclude(heure_arrivee=None).count(),
                "total_jours_semaine": presences_semaine.count(),
                "heures_travaillees_aujourd_hui": None,
                "statut_actuel": "absent"
            }

            try:
                presence_jour = Presence.objects.get(employe=employe, date=today)
                stats["statut_actuel"] = presence_jour.statut
                if presence_jour.heure_arrivee and presence_jour.heure_sortie:
                    stats["heures_travaillees_aujourd_hui"] = presence_jour.get_duree_travail()
            except Presence.DoesNotExist:
                pass

            return Response({"success": True, "stats": stats})

        except Employe.DoesNotExist:
            return Response({
                "success": False,
                "message": "Votre compte n'est pas associé à un employé."
            }, status=status.HTTP_400_BAD_REQUEST)