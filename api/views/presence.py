from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from django.db import transaction

from api.models import Presence, Employe
from api.serializers import PresenceSerializer
from users.authentication import JWTAuthentication


class PresenceListCreateAPIView(generics.ListCreateAPIView):
    """Liste et création de présences."""
    queryset = Presence.objects.all()
    serializer_class = PresenceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().select_related('employe__user').prefetch_related('employe')
        
        if user.is_admin or user.is_manager or user.is_rh:
            return qs
        
        # Staff voit seulement ses présences
        return qs.filter(employe__user=user)

    def perform_create(self, serializer):
        user = self.request.user
        
        # Vérifier la permission
        if not user.has_perm("api.can_manage_presence"):
            raise PermissionDenied("Vous n'avez pas la permission de gérer les présences.")
        
        # Pour staff, vérifier qu'il n'a pas déjà une présence aujourd'hui
        if not (user.is_admin or user.is_manager or user.is_rh):
            try:
                employe = user.employe
                today = timezone.localdate()
                if Presence.objects.filter(employe=employe, date=today).exists():
                    raise ValidationError("Vous avez déjà une présence pour aujourd'hui.")
            except Employe.DoesNotExist:
                raise ValidationError("Votre compte n'est pas associé à un employé.")
        
        serializer.save()


class PresenceDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification et suppression d'une présence."""
    serializer_class = PresenceSerializer
    queryset = Presence.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().select_related('employe__user')
        
        if user.is_admin or user.is_manager or user.is_rh:
            return qs
        
        return qs.filter(employe__user=user)

    def perform_update(self, serializer):
        user = self.request.user
        presence = self.get_object()
        
        if not user.has_perm("api.can_manage_presence"):
            raise PermissionDenied("Vous n'avez pas la permission de gérer les présences.")
        
        # Staff ne peut modifier que sa présence du jour
        if not (user.is_admin or user.is_manager or user.is_rh):
            if presence.employe.user != user or presence.date != timezone.localdate():
                raise PermissionDenied("Vous ne pouvez modifier que votre présence du jour.")
        
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        
        if not user.has_perm("api.can_manage_presence"):
            raise PermissionDenied("Vous n'avez pas la permission de gérer les présences.")
        
        if not user.is_admin:
            raise PermissionDenied("Seul l'administrateur peut supprimer une présence.")
        
        instance.delete()


class PresenceArriveeAPIView(APIView):
    """Marquer l'arrivée."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        user = request.user
        
        if not user.has_perm("api.can_manage_presence"):
            raise PermissionDenied("Vous n'avez pas la permission de gérer les présences.")
        
        # Si pk fourni, récupérer la présence spécifique
        if pk:
            try:
                presence = Presence.objects.select_related('employe__user').get(pk=pk)
            except Presence.DoesNotExist:
                raise NotFound("Présence introuvable.")
            
            # Vérifier les permissions pour cette présence
            if not (user.is_admin or user.is_manager or user.is_rh):
                if presence.employe.user != user or presence.date != timezone.localdate():
                    raise PermissionDenied("Vous ne pouvez marquer l'arrivée que pour votre présence du jour.")
        else:
            # Créer ou récupérer la présence du jour pour l'utilisateur
            if user.is_admin or user.is_manager or user.is_rh:
                raise ValidationError("Les administrateurs doivent spécifier un ID de présence.")
            
            try:
                employe = user.employe
                today = timezone.localdate()
                presence, created = Presence.objects.get_or_create(
                    employe=employe,
                    date=today,
                    defaults={'statut': 'absent'}
                )
            except Employe.DoesNotExist:
                raise ValidationError("Votre compte n'est pas associé à un employé.")

        # Enregistrer l'arrivée
        try:
            with transaction.atomic():
                presence.enregistrer_arrivee()
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PresenceSerializer(presence, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PresenceSortieAPIView(APIView):
    """Marquer la sortie."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        user = request.user
        
        if not user.has_perm("api.can_manage_presence"):
            raise PermissionDenied("Vous n'avez pas la permission de gérer les présences.")
        
        # Si pk fourni, récupérer la présence spécifique
        if pk:
            try:
                presence = Presence.objects.select_related('employe__user').get(pk=pk)
            except Presence.DoesNotExist:
                raise NotFound("Présence introuvable.")
            
            # Vérifier les permissions pour cette présence
            if not (user.is_admin or user.is_manager or user.is_rh):
                if presence.employe.user != user or presence.date != timezone.localdate():
                    raise PermissionDenied("Vous ne pouvez marquer la sortie que pour votre présence du jour.")
        else:
            # Récupérer la présence du jour pour l'utilisateur
            if user.is_admin or user.is_manager or user.is_rh:
                raise ValidationError("Les administrateurs doivent spécifier un ID de présence.")
            
            try:
                employe = user.employe
                today = timezone.localdate()
                presence = Presence.objects.get(employe=employe, date=today)
            except (Employe.DoesNotExist, Presence.DoesNotExist):
                raise NotFound("Aucune présence trouvée pour aujourd'hui.")

        # Enregistrer la sortie
        try:
            with transaction.atomic():
                presence.enregistrer_sortie()
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PresenceSerializer(presence, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class MaPresenceAPIView(APIView):
    """Endpoints pour la présence de l'utilisateur connecté."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Récupérer ma présence du jour."""
        user = request.user
        
        try:
            employe = user.employe
            today = timezone.localdate()
            presence = Presence.objects.get(employe=employe, date=today)
            serializer = PresenceSerializer(presence, context={"request": request})
            return Response(serializer.data)
        except Employe.DoesNotExist:
            return Response({"detail": "Votre compte n'est pas associé à un employé."}, 
                          status=status.HTTP_400_BAD_REQUEST)
        except Presence.DoesNotExist:
            return Response({"detail": "Aucune présence pour aujourd'hui."}, 
                          status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Créer ma présence du jour."""
        user = request.user
        
        if not user.has_perm("api.can_manage_presence"):
            raise PermissionDenied("Vous n'avez pas la permission de gérer les présences.")
        
        try:
            employe = user.employe
            today = timezone.localdate()
            
            if Presence.objects.filter(employe=employe, date=today).exists():
                return Response({"detail": "Présence déjà créée pour aujourd'hui."}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            presence = Presence.objects.create(employe=employe, date=today)
            serializer = PresenceSerializer(presence, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Employe.DoesNotExist:
            return Response({"detail": "Votre compte n'est pas associé à un employé."}, 
                          status=status.HTTP_400_BAD_REQUEST)

