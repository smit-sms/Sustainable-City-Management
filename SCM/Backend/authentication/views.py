from django.shortcuts import render
from rest_framework.views import APIView
from .models import User,Whitelist
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from .serializers import Userserializer
import logging


class Authenticate(APIView):

    def __init__(self, *args, **kwargs) -> None:
        # Defining logger here to get the name for the class
        self.logger = logging.getLogger(__name__)

    serializer_class = Userserializer

    def post(self, request, format=None):
        try:
            email = request.data["email"]
            password = request.data["password"]
            queryset = User.objects.filter(email=email, password=password)
            if queryset:
                if not self.request.session.exists(self.request.session.session_key):
                    self.request.session.create()
                self.request.session["email"] = email
                return Response({"message": "Successful login"}, status = status.HTTP_200_OK)
            return Response({"message": "Invalid credentials, please check and try again"}, status = status.HTTP_401_UNAUTHORIZED)
        except KeyError as e:
            return Response({"message": f"Please pass required parameter: {e}", "data": None}, 
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            return Response({"message": "Some unexpected exception occured. Please try again", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)

class IsAuthenticated(APIView):

    def __init__(self, *args, **kwargs) -> None:
        # Defining logger here to get the name for the class
        self.logger = logging.getLogger(__name__)

    def get(self,request,format=None):
        try:
            if not self.request.session.exists(self.request.session.session_key):
                self.request.session.create()
            data = {
                "email":self.request.session.get("email")
            }
            return JsonResponse(data, status=status.HTTP_200_OK)
        except Exception as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            return Response({"message": "Some unexpected exception occured. Please try again", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)

class Signup(APIView):

    def __init__(self, *args, **kwargs) -> None:
        # Defining logger here to get the name for the class
        self.logger = logging.getLogger(__name__)

    serializer_class=Userserializer
    def post(self,request,format=None):
        try:
            email=request.data["email"]
            password=request.data["password"]
            username=request.data["username"]   
            result=Whitelist.objects.filter(email=email)
            if result:
                if User.objects.filter(email=email):
                    return Response("Already existing user",status=status.HTTP_400_BAD_REQUEST)
                user=User(email=email,password=password,username=username)
                user.save()
                return Response("User Created",status=status.HTTP_201_CREATED)
            else:
                return Response("User Not Authorized",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            return Response({"message": "Some unexpected exception occured. Please try again", "data": None},
                        status=status.HTTP_400_BAD_REQUEST)


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
            return Response(f"Some unexpected error occured, error: {e}",status=status.HTTP_204_NO_CONTENT)

class get_user(APIView):

    def __init__(self, *args, **kwargs) -> None:
        # Defining logger here to get the name for the class
        self.logger = logging.getLogger(__name__)

    serializer_class = Userserializer

    def post(self,request,format=None):
        try:
            email = request.data["email"]
            password = request.data["password"]
            user_list = User.objects.filter(email=email, password=password)
            if user_list:
                user = user_list[0]
                return Response(self.serializer_class(user).data, status=status.HTTP_200_OK)
            return Response("No User",status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            return Response({"message": "Some unexpected exception occured. Please try again", "data": None},
                        status=status.HTTP_400_BAD_REQUEST)
