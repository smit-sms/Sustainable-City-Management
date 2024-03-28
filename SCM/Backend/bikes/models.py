from django.db import models

class Station(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()

class Snapshot(models.Model):
    station_id = models.IntegerField()
    bike_stands = models.IntegerField()
    available_bikes = models.IntegerField()
    usage_percent = models.FloatField()
    last_update = models.DateTimeField()
    status = models.CharField(max_length=20)