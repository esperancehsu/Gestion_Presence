from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from .authentication import JWTAuthentication
from rest_framework.permissions import AllowAny

import datetime, jwt

from core.mixins import PermissionMixin
from rest_framework.exceptions import PermissionDenied




User = get_user_model()
SECRET_KEY = settings.SECRET_KEY


# ---------------- Register ----------------
class UserRegisterView(APIView):
    authentication_classes = []  # Pas besoin de token pour s'inscrire
    permission_classes = [AllowAny]  # Permet à n'importe qui de s'inscrire

    
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response({"user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------- Login ----------------
class UserLoginView(APIView):
    
    authentication_classes = [JWTAuthentication]  # Pas besoin de token pour se connecter
    permission_classes = [AllowAny]

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
class ProtectedView(PermissionMixin, APIView):
    authentication_classes = [JWTAuthentication]
    required_permission = "can_view_protected"
    abac_check = True

    def get(self, request):
        user = request.user
        return Response({
            "message": "Accès autorisé",
            "user": UserSerializer(user).data
        })


# ---------------- User Liste (admin only) ----------------
class UserListView(PermissionMixin, APIView):
    authentication_classes = [JWTAuthentication]
    allowed_groups = ["admin"]
    abac_check = False

    def get(self, request):
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)


# ---------------- User Detail ----------------
class UserDetailView(PermissionMixin,APIView):
    
    authentication_classes = [JWTAuthentication]
    required_permission = "can_view_user_detail"
    abac_check = True

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            # "status": user.status  # ⚠️ Supprimé car inexistant dans User par défaut
        })


# ---------------- Logout ----------------
class UserLogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie("jwt")
        response.data = {"message": "Déconnexion réussie"}
        return response
