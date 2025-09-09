from django.urls import path
from .views import (
    UserRegisterView,
    UserLoginView,
    RefreshTokenView,
    UserListView,
    ProtectedView,
    UserLogoutView
)

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('refresh/', RefreshTokenView.as_view(), name='token-refresh'),
    path('list/', UserListView.as_view(), name='user-list'),         # Admin seulement
    path('protected/', ProtectedView.as_view(), name='protected'),  # Exemple endpoint protégé
    path('logout/', UserLogoutView.as_view(), name='user-logout'),  # Déconnexion

]
