# users/urls.py
from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView, AdminOnlyView, ModeratorOnlyView, UserOnlyView

urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginView.as_view(), name="login"),
    path('user/', UserView.as_view(), name="user"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('admin-only/', AdminOnlyView.as_view(), name="admin-only"),
    path('moderator-only/', ModeratorOnlyView.as_view(), name="moderator-only"),
    path('user-only/', UserOnlyView.as_view(), name="user-only"),
]
