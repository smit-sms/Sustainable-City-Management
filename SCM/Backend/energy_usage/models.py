from django.db import models

# Create your models here.
class SA_energy_consumption(models.Model):
    SA_code = models.IntegerField()
    Energy_use=models.IntegerField()
    Energy_cost=models.IntegerField()
    Total_Floor_Area=models.IntegerField()
    Small_Area_Name=models.CharField(max_length=50)    