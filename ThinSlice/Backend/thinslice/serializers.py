from rest_framework import serializers, viewsets
from .models import ThinSlice

class ThinSliceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThinSlice
        fields = '__all__'


