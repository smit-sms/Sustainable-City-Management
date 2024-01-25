from django.db import models


class User(models.Model):
    email=models.CharField(null=False,max_length=50,default='')
    password=models.CharField(null=False,max_length=20,default="")
    username=models.CharField(null=False,max_length=20,default="")

class Whitelist(User):
    

