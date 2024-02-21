from rest_framework import serializers
from .models import User

class Userserializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=("email","password","username")