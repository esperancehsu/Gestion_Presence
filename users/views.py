from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed

import jwt, datetime

from .models import User
from .serializers import UserSerializer

# Create your views here.
def home(request):
    return render(request, 'home/index.html')

class RegisterView(APIView):
    def post(self, request):
        # Logic for user registration
        data = request.data
        # Assume we have a User model and a serializer for it
        
        
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']


        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('Utilisateur not found')
        
        if not user.check_password(password):
            raise AuthenticationFailed("incorrecte password")
        

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=66),
            'iat': datetime.datetime.utcnow(),
        }

        # jwt.encode returns a string in PyJWT >=2.x, so no need to decode

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response =  Response()
        response.set_cookie(key='jwt', value=token, httponly=True)

        response.data = {

            "jwt": token

        }

        return response

class UserView(APIView):

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('ANAUTHENTICATED')
        
        try:
            payload = jwt.decode(token, algorithms=['hs256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('ANAUTHENTICATED')
        
        #user = User.objects.get(payload('id'))
        user = User.objects.filter(id=payload['id']).first()

        serializers = UserSerializer(user)

        return Response(serializers.data)

        #return Response(user)

        #return Response(token)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Success'
        }

        return response