from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import logging
import pickle
import geojson
import pandas as pd
import numpy as np
import requests
import json
import math

from .models import BusStop, BusRoute, DublinBikeStation
from .serializers import BusRouteSerializer, DublinBikesStationSerializer
from .utils import get_openroute_geojson, get_weather_forecast


class BusRouteView(APIView):
    '''
    Class for all the operations related to the Bus Routes.
    '''
    # permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs) -> None:
        # Defining logger here to get the name for the class
        self.logger = logging.getLogger(__name__)

    def get(self, request, *args, **kwargs):
        """
        GET request handler to retrieve bus route data from a GeoJSON file if a 
        'bus_name' query parameter is provided, return details for that specific bus route.
        Otherwise, lists all bus routes available.
        """
        try:
            bus_name = request.query_params.get('bus_name', None)
            if bus_name:
                bus = BusRoute.objects.get(bus_name=bus_name)
                result = bus.geojson
            else:
                bus_routes = BusRoute.objects.all()
                result = BusRouteSerializer(bus_routes, many=True).data
            return Response({"message": "Successfully fetched the required data", "data": result},
                            status=status.HTTP_200_OK)
        except BusRoute.DoesNotExist:
            return Response({"message": "The given bus not found. Please check and try again.", "data": None},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            return Response({"message": "Some unexpected exception occured. Please try again", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        """
        POST request handler for the BusRoute to get the route based on the coordinates passed

        :returns: Response object with a JSON payload. The JSON payload contains
        the data of the geojson_route, which is a route based on the coordinates passed.
        """
        try:
            bus_name = request.data['bus_name']
            coords = request.data['coordinates']
            coordinates = [list(item for item in coord if not isinstance(
                item, str)) for coord in coords]
            geojson_route_custom = get_openroute_geojson(
                coordinates=coordinates, optimize=True)

            bus = BusRoute.objects.get(bus_name=bus_name)
            geojson_route = bus.geojson

            # Adding the red colour property for the new route
            for feature in geojson_route_custom["features"]:
                if feature['geometry']['type'] == 'LineString':
                    feature['properties']['style'] = {
                        "color": "red"
                    }

            # Modify the geojson to include the coordinate points/markers
            point_features = [{
                "type": "Feature",
                "properties": {
                    "Stop Name": coord[2],
                    "Location": f"{coord[0]}, {coord[1]}"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [coord[0], coord[1]]
                }
            } for coord in coords]
            geojson_route_custom["features"].extend(point_features)

            # Extending the original geojson from DB to include the new route
            geojson_route["features"].extend(geojson_route_custom["features"])

            return Response({"message": "Successfully fetched the required data", "data": geojson_route},
                            status=status.HTTP_200_OK)
        except KeyError as e:
            return Response({"message": f"Please pass required parameter: {e}", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)
        except BusRoute.DoesNotExist:
            return Response({"message": f"The given bus '{bus_name}' not found. Please check and try again.", "data": None},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            return Response({"message": "Some unexpected exception occured. Please try again", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)


class DublinBikesView(APIView):
    '''
    Class for all the operations related to the Dublin Bikes.
    '''
    # permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs) -> None:
        # Defining logger here to get the name for the class
        self.logger = logging.getLogger(__name__)

        # self.df_stations = pd.read_csv('cityservices/data/STATION ID - BIKE STANDS.csv')
        self.model = pickle.load(open("cityservices/data/RFmodel_lr.pkl", 'rb'))

    def prepare_query_for_model(self, weather_forecast=None):
        if (weather_forecast == None):
            weather_forecast = get_weather_forecast()

        res = pd.DataFrame.from_dict(pd.json_normalize(
            weather_forecast['hourly']['data']), orient='columns')
        res['date'] = pd.to_datetime(res['date'])
        res = res[['date', 'precipitation.total', 'temperature']]
        res.rename(columns={'precipitation.total': 'rain',
                            'temperature': 'temp', 'date': 'TIME'}, inplace=True)

        res['hour'] = res['TIME'].dt.hour
        res['minute'] = res['TIME'].dt.minute
        res['day'] = res['TIME'].dt.day
        res['dayofweek'] = res['TIME'].dt.dayofweek
        
        queryset = DublinBikeStation.objects.all().values('station_id',
                                                          'bike_stands')
        # Convert the QuerySet to a DataFrame
        df_stations = pd.DataFrame.from_records(queryset)
        df_stations.rename(columns={'station_id': 'STATION ID',
                            'bike_stands': 'BIKE STANDS'}, inplace=True)
        
        df_stations['dummy'] = 1
        res['dummy'] = 1
        res = pd.merge(df_stations, res, on='dummy')
        res = res.drop(columns='dummy')

        res = res.reset_index(drop=True)
        df_return = pd.DataFrame()
        df_return = res.copy()
        df_return.drop(['hour', 'minute', 'day', 'dayofweek'],
                       axis=1, inplace=True)
        res.drop('TIME', axis=1, inplace=True)
        return res, df_return

    def get(self, request, *args, **kwargs):
        try:
            dublinbikestations = DublinBikeStation.objects.all()
            result = DublinBikesStationSerializer(
                dublinbikestations, many=True).data
            df_query, df_return = self.prepare_query_for_model()
            prediction = self.model.predict(df_query)
            prediction = np.rint(prediction)
            df_return['available_bikes'] = prediction
            return Response({"message": "Successfully fetched the required data", "data": {
                'prediction': json.loads(df_return.to_json(orient='records')),
                'positions': result}
            }, status=status.HTTP_200_OK)
        except Exception as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            return Response({"message": "Some unexpected exception occured. Please try again", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)
