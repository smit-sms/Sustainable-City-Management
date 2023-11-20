from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from .models import ThinSlice
from .serializers import ThinSliceSerializer


# Create your views here.
class ThinSliceViewSet(viewsets.ModelViewSet):
    queryset = ThinSlice.objects.all()
    serializer_class = ThinSliceSerializer

    def list(self, request, *args, **kwargs):
        queryset = ThinSlice.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

