from rest_framework import serializers
from .models import BusRoute, BusStop, DublinBikeStation


class BusRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusRoute
        fields = ('route_id', 'name', 'bus_name')


class BusStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusStop
        fields = ('route_id', 'name', 'latitude', 'longitude')


class DublinBikesStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DublinBikeStation
        fields = ('station_id',
                  'name',
                  'bike_stands',
                  'latitude',
                  'longitude')
