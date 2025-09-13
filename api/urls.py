from django.urls import path

from .views.employe import EmployeListCreateAPIView, EmployeRetrieveUpdateDestroyAPIView
from .views.rapport import RapportListCreateAPIView, RapportRetrieveUpdateDestroyAPIView
from .views.presence import (
    PresenceListCreateAPIView, 
    PresenceDetailAPIView, 
    PresenceArriveeAPIView, 
    PresenceSortieAPIView,
    MaPresenceAPIView  # Nouvelle vue à créer
)

urlpatterns = [
    # Employe
    path("employes/", EmployeListCreateAPIView.as_view(), name="employe-list-create"),
    path("employes/<int:pk>/", EmployeRetrieveUpdateDestroyAPIView.as_view(), name="employe-detail"),

    # Rapport
    path("rapports/", RapportListCreateAPIView.as_view(), name="rapport-list-create"),
    path("rapports/<int:pk>/", RapportRetrieveUpdateDestroyAPIView.as_view(), name="rapport-detail"),

    # Presence - URLs existantes
    path("presences/", PresenceListCreateAPIView.as_view(), name="presence-list-create"),
    path("presences/<int:pk>/", PresenceDetailAPIView.as_view(), name="presence-detail"),
    path("presences/<int:pk>/arrivee/", PresenceArriveeAPIView.as_view(), name="presence-arrivee"),
    path("presences/<int:pk>/sortie/", PresenceSortieAPIView.as_view(), name="presence-sortie"),
    
    # Presence - Nouvelles URLs pour les employés (sans ID)
    path("ma-presence/", MaPresenceAPIView.as_view(), name="ma-presence"),
    path("ma-presence/arrivee/", PresenceArriveeAPIView.as_view(), name="mon-arrivee"),
    path("ma-presence/sortie/", PresenceSortieAPIView.as_view(), name="ma-sortie"),
]