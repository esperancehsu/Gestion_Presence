from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from .authentication import JWTAuthentication
from .permissions import IsAdmin
import datetime, jwt

User = get_user_model()
SECRET_KEY = settings.SECRET_KEY

# ---------------- Register ----------------
class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------- Login ----------------
class UserLoginView(APIView):
    def post(self, request):
        identifier = request.data.get("identifier")
        password = request.data.get("password")

        if not identifier or not password:
            raise AuthenticationFailed("Identifiant et mot de passe requis")

        # Vérifier username ou email
        if "@" in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
        else:
            user = User.objects.filter(username__iexact=identifier).first()

        if not user or not user.check_password(password):
            raise AuthenticationFailed("Identifiant ou mot de passe invalide")

        # Générer Access + Refresh tokens
        now = datetime.datetime.utcnow()
        access_payload = {
            "id": user.id,
            "exp": now + datetime.timedelta(minutes=15),
            "iat": now,
            "type": "access"
        }
        refresh_payload = {
            "id": user.id,
            "exp": now + datetime.timedelta(days=7),
            "iat": now,
            "type": "refresh"
        }

        access_token = jwt.encode(access_payload, SECRET_KEY, algorithm="HS256")
        refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm="HS256")

        response = Response({
            "access": access_token,
            "refresh": refresh_token,
            "user": UserSerializer(user).data
        })
        response.set_cookie(key="jwt", value=access_token, httponly=True)
        return response


# ---------------- Refresh Token ----------------
class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            raise AuthenticationFailed("Refresh token manquant")

        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Refresh token expiré")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Token invalide")

        if payload.get("type") != "refresh":
            raise AuthenticationFailed("Mauvais type de token")

        user = User.objects.filter(id=payload["id"]).first()
        if not user:
            raise AuthenticationFailed("Utilisateur introuvable")

        now = datetime.datetime.utcnow()
        new_access_payload = {
            "id": user.id,
            "exp": now + datetime.timedelta(minutes=15),
            "iat": now,
            "type": "access"
        }
        new_access_token = jwt.encode(new_access_payload, SECRET_KEY, algorithm="HS256")
        return Response({"access": new_access_token})


# ---------------- Protected View ----------------
class ProtectedView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        return Response({
            "message": "Accès autorisé",
            "user": UserSerializer(user).data
        })


# ---------------- User Liste (admin only) ----------------
class UserListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)


class UserDetailView(APIView):

    
    def get(self, request):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise AuthenticationFailed("Token manquant")

        token = token.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Access token expiré")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Token invalide")

        if payload.get("type") != "access":
            raise AuthenticationFailed("Ce n'est pas un access token")

        user = User.objects.filter(id=payload["id"]).first()
        if not user:
            raise AuthenticationFailed("Utilisateur not fund")

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "status": user.status
        })

class UserLogoutView(APIView):

 
    def post(self, request):
        response = Response()
        response.delete_cookie("jwt")
        response.data = {
            "message": "Déconnexion réussie"
        }
        return response