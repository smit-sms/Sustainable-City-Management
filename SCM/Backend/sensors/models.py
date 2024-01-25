from django.db import models

# Create your models here.
from django.db import models

# Create your models here.

class DateTime(models.Model):
  datetime = models.DateTimeField(unique=True)

class Sensor(models.Model):
  serial_number = models.CharField(max_length=50)
  latitude = models.FloatField()
  longitude = models.FloatField()
  sensor_type = models.CharField(max_length=50)

class Air(models.Model):
  pm2_5 = models.FloatField()
  datetime = models.ForeignKey('DateTime', on_delete=models.SET_NULL, null=True)
  sensor = models.ForeignKey('Sensor', on_delete=models.SET_NULL, null=True)

class Noise(models.Model):
  laeq = models.FloatField()
  datetime = models.ForeignKey('DateTime', on_delete=models.SET_NULL, null=True)
  sensor = models.ForeignKey('Sensor', on_delete=models.SET_NULL, null=True)