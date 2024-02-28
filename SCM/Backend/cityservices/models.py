from django.db import models

# Create your models here.

class BusRoute(models.Model):
    route_id = models.CharField(max_length=50)
    name = models.CharField(max_length=150)
    bus_name = models.CharField(max_length=50)
    geojson = models.JSONField(default=dict)

class BusStop(models.Model):
    stop_id = models.CharField(max_length=50)
    route_id = models.CharField(max_length=50)
    name = models.CharField(max_length=150)
    latitude = models.FloatField()
    longitude = models.FloatField()
    direction = models.IntegerField()

class DublinBikeStation(models.Model):
    station_id = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    bike_stands = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
