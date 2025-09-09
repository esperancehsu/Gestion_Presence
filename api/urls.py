from django.urls import path


from .views.employe import EmployeListCreateAPIView,EmployeRetrieveUpdateDestroyAPIView
from .views.rapport import RapportListCreateAPIView, RapportRetrieveUpdateDestroyAPIView
from .views.presence import PresenceListCreateAPIView, PresenceDetailAPIView, PresenceArriveeAPIView, PresenceSortieAPIView

urlpatterns = [
    # Employe
    path("employes/", EmployeListCreateAPIView.as_view(), name="employe-list-create"),
    path("employes/<int:pk>/", EmployeRetrieveUpdateDestroyAPIView.as_view(), name="employe-detail"),

    # Rapport
    path("rapports/", RapportListCreateAPIView.as_view(), name="rapport-list-create"),
    path("rapports/<int:pk>/", RapportRetrieveUpdateDestroyAPIView.as_view(), name="rapport-detail"),

    # Presence
    path("presences/", PresenceListCreateAPIView.as_view(), name="presence-list-create"),
    path("presences/<int:pk>/", PresenceDetailAPIView.as_view(), name="presence-detail"),
    path("presences/<int:pk>/arrivee/", PresenceArriveeAPIView.as_view(), name="presence-arrivee"),
    path("presences/<int:pk>/sortie/", PresenceSortieAPIView.as_view(), name="presence-sortie"),
]


"""
from django.urls import path
from .views import (
    EmployeListCreateView,
    EmployeRetrieveUpdateDestroyView,
    RapportListCreateView,
    RapportRetrieveUpdateDestroyView,
    PresenceCreateView,
    PresenceUpdateView,
    PresenceListView
)

urlpatterns = [
    # Employés
    path('employes/', EmployeListCreateView.as_view(), name='employe-list-create'),
    path('employes/<int:pk>/', EmployeRetrieveUpdateDestroyView.as_view(), name='employe-detail'),

    # Rapports
    path('rapports/', RapportListCreateView.as_view(), name='rapport-list-create'),
    path('rapports/<int:pk>/', RapportRetrieveUpdateDestroyView.as_view(), name='rapport-detail'),

    # Présences
    path('presences/', PresenceListView.as_view(), name='presence-list'),
    path('presences/create/', PresenceCreateView.as_view(), name='presence-create'),
    path('presences/<int:pk>/update/', PresenceUpdateView.as_view(), name='presence-update'),
]

"""