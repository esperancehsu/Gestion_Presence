import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
SECRET_KEY = settings.SECRET_KEY

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise AuthenticationFailed("Token manquant")
        token = token.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expiré")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Token invalide")

        if payload.get("type") != "access":
            raise AuthenticationFailed("Ce n'est pas un access token")

        user = User.objects.filter(id=payload["id"]).first()
        if not user:
            raise AuthenticationFailed("Utilisateur introuvable")
        return (user, token)
