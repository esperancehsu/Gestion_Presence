import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
SECRET_KEY = settings.SECRET_KEY

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Vérifier d'abord dans les headers Authorization
        auth_header = request.headers.get("Authorization")
        token = None
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            # Vérifier aussi dans les cookies si pas trouvé dans headers
            token = request.COOKIES.get("jwt")
        
        # Si aucun token n'est trouvé, retournons None 
        if not token:
            return None
        
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
        
        if not user.is_active:
            raise AuthenticationFailed("Compte désactivé")
            
        return (user, token)