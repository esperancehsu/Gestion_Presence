
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer
from .authentication import JWTAuthentication
import datetime, jwt

User = get_user_model()
SECRET_KEY = settings.SECRET_KEY


class UserRegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Inscription réussie !",
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UserLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']

        now = datetime.datetime.utcnow()
        access_payload = {
            "id": user.id,
            "exp": now + datetime.timedelta(days=5),
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

        if not user.is_active:
            raise AuthenticationFailed("Compte désactivé")

        now = datetime.datetime.utcnow()
        new_access_payload = {
            "id": user.id,
            "exp": now + datetime.timedelta(minutes=15),
            "iat": now,
            "type": "access"
        }
        new_access_token = jwt.encode(new_access_payload, SECRET_KEY, algorithm="HS256")
        return Response({"access": new_access_token})


class UserDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        })


class UserLogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie("jwt")
        response.data = {"message": "Déconnexion réussie"}
        return response


class UserListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]  

    def get(self, request):
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)