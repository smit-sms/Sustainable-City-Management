from django.shortcuts import render
from rest_framework.views import APIView

class Authenticate(APIView):
    def get(self,request,format=None):
        

