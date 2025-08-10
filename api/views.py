from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Employe, Presence, Rapport
from .serializers import EmployeSerializer, PresenceSerializer, RapportSerializer


# ModelViewSet fourni automatiquement méthodes list, create, retrieve, update, destroy. 

# par la suite on fera avec APIView et le decorator api_view aussi

class EmployeViewSet(viewsets.ModelViewSet):
    # On définit la requête de base : tous les employés en base.
    queryset = Employe.objects.all()
    # On indique quel serializer utiliser pour convertir les données.
    serializer_class = EmployeSerializer

    
    @action(detail=True, methods=['post'], url_path='enregistrer_arrivee')
    def enregistrer_arrivee(self, request, pk=None):
        """
        On crée ou récupère une présence pour la date du jour de cet employé.
        On met à jour l'heure d'arrivée avec l'heure actuelle.
        """
       
        employe = self.get_object()
       
        today = timezone.localdate()
       
        presence, created = Presence.objects.get_or_create(employe=employe, date=today)
       
        presence.heure_arrivee = timezone.now()
        presence.save()
       
        serializer = PresenceSerializer(presence)
       
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['post'], url_path='enregistrer_sortie')
    def enregistrer_sortie(self, request, pk=None):
        """
        On cherche la dernière présence du jour pour l'employé qui n'a pas d'heure de sortie.
        On met à jour l'heure de sortie avec l'heure actuelle.
        """
        employe = self.get_object()
        today = timezone.localdate()
        try:
            # On récupère la dernière présence du jour (triée par id décroissant).
            presence = Presence.objects.filter(employe=employe, date=today).order_by('-id').first()
            # Si aucune présence trouvée, on renvoie une erreur 404.
            if not presence:
                return Response({"detail": "Aucune présence trouvée pour aujourd'hui."}, status=status.HTTP_404_NOT_FOUND)
            # On met à jour l'heure de sortie.
            presence.heure_sortie = timezone.now()
            presence.save()
            serializer = PresenceSerializer(presence)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Presence.DoesNotExist:
            # En cas d'exception, on renvoie un message d'erreur.
            return Response({"detail": "Aucune présence trouvée."}, status=status.HTTP_404_NOT_FOUND)


# ViewSet pour gérer les présences.
class PresenceViewSet(viewsets.ModelViewSet):
    queryset = Presence.objects.all()
    serializer_class = PresenceSerializer

    # Action personnalisée pour marquer la sortie d'une présence précise.
    @action(detail=True, methods=['post'], url_path='marquer_sortie')
    def marquer_sortie(self, request, pk=None):
        
        presence = self.get_object()
      
        presence.heure_sortie = timezone.now()
        presence.save()
        
        return Response(PresenceSerializer(presence).data)


# ViewSet pour gérer les rapports.
class RapportViewSet(viewsets.ModelViewSet):
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer
