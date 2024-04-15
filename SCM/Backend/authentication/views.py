from django.shortcuts import render
from rest_framework.views import APIView
from .models import User, Whitelist
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError
from .serializers import UserSerializer
import logging

class New_whitelist(APIView):
    def post(self,request,format=None):
        try:
            email=request.data["email"]
            existing=Whitelist.objects.filter(email=email)
            if existing:
                return Response("Already existing email", status=status.HTTP_208_ALREADY_REPORTED)
            new=Whitelist.objects.create(email=email)
            return Response("New email added to Whitelist", status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(f"Some unexpected error occured, error: {e}", status=status.HTTP_204_NO_CONTENT)

class RegisterView(APIView):
    def post(self, request):
        result = Whitelist.objects.filter(email=request.data["email"])
        if result:
            serializer = UserSerializer(data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            user = User.objects.get(email = request.data["email"])
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            return Response({
                "access_token" : str(access_token),
                "refresh_token" : str(refresh_token)
            }, status=status.HTTP_201_CREATED)
        else:
            return Response("User Not Authorized",status=status.HTTP_401_UNAUTHORIZED)

class Loginview(APIView):

    def __init__(self, *args, **kwargs) -> None:
        # Defining logger here to get the name for the class
        self.logger = logging.getLogger(__name__)

    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]
        
        try:
            user = User.objects.get(email = email)
        except User.DoesNotExist:
            raise AuthenticationFailed("Account does not exist")
        if user is None:
            raise AuthenticationFailed("User does not exist")
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect Password")
        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        return Response({
            "access_token" : str(access_token),
            "refresh_token" : str(refresh_token)
        })
    
class LogoutView(APIView):
    
    def __init__(self, *args, **kwargs) -> None:
        # Defining logger here to get the name for the class
        self.logger = logging.getLogger(__name__)
    
    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"message": "Successfully Logged out!"}, status=status.HTTP_200_OK)
        except TokenError as e:
            self.logger.exception(f'Token error occured: {e}')
            raise AuthenticationFailed("Invalid Token")
