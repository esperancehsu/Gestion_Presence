from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from api.models import Presence
from api.serializers import PresenceSerializer


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