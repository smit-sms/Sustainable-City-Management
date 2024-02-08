from django.shortcuts import render
from rest_framework.views import APIView
from .models import User,Whitelist
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from .serializers import Userserializer

class Authenticate(APIView):
    serializer_class=Userserializer
    def post(self,request,format=None):
        try:
            email=request.data["email"]
            password=request.data["password"]
            username=request.data["username"]
            queryset=User.objects.filter(email=email,username=username,password=password)
            if queryset:
                if not self.request.session.exists(self.request.session.session_key):
                    self.request.session.create()
                self.request.session["email"]=email
                return Response("Successful login",status=status.HTTP_200_OK)
            return Response("Invalid credentials",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response(f"Some unexpected error occured, error: {e}",status=status.HTTP_204_NO_CONTENT)
    
class IsAuthenticated(APIView):
    def get(self,request,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        data={
        "email":self.request.session.get("email")
        }
        return JsonResponse(data,status=status.HTTP_200_OK)

class Signup(APIView):
    serializer_class=Userserializer
    def post(self,request,format=None):
            try:
                email=request.data["email"]
                password=request.data["password"]
                username=request.data["username"]
    #           username=serializer.data.get("username")     
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
                return Response(f"Some unexpected error occured, error: {e}",status=status.HTTP_204_NO_CONTENT)

class Update_account(APIView):
    serializer_class=Userserializer
    def post(self,request,format=None):
        try:
            email=request.data["email"]
            password=request.data["password"]
            username=request.data["username"]
            new_username=request.data["new_username"]
            new_password=request.data["new_password"]
            query=User.objects.filter(email=email,password=password,username=username)   
            if query:
                user=query[0]
                user.password=new_password
                user.username=new_username
                user.save(update_fields=["password","username"])
                return Response("Account updated",status=status.HTTP_200_OK)
            return Response("No account corresponding to the credentials",status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(f"Some unexpected error occured, error: {e}",status=status.HTTP_204_NO_CONTENT)
        
class New_whitelist(APIView):
    def post(self,request,format=None):
        try:
            email=request.data["email"]
            existing=Whitelist.objects.filter(email=email)
            if existing:
                return Response("Already existing email",status=status.HTTP_208_ALREADY_REPORTED)
            new=Whitelist.objects.create(email=email)
            return Response("New email added to Whitelist",status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(f"Some unexpected error occured, error: {e}",status=status.HTTP_204_NO_CONTENT)
    
class get_user(APIView):
    serializer_class=Userserializer
    def post(self,request,format=None):
        try:
            email=request.data["email"]
            password=request.data["password"]
            username=request.data["username"]
            user_list=User.objects.filter(username=username,email=email,password=password)
            if user_list:
                user=user_list[0]
                return Response(self.serializer_class(user).data,status=status.HTTP_200_OK)
            return Response("No User",status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(f"Some unexpected error occured, error: {e}",status=status.HTTP_204_NO_CONTENT)
        
