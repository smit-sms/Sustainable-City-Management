from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
import logging
import pickle
import geojson
import pandas as pd
import numpy as np
import requests
import json
import math
import datetime
from django.utils import timezone

from .models import BusStop, BusRoute, DublinBikeStation, SA_energy_consumption
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


class SA_energy(APIView):
    '''
    Class for all the operations related to the Energy Consumption for small areas.
    '''
    def __init__(self, *args, **kwargs) -> None:
        # Defining logger here to get the name for the class
        self.logger = logging.getLogger(__name__)
        self.response_message = ''
        self.response_status = status.HTTP_200_OK
        self.response_data = []

    def get(self, request, *args, **kwargs):
        """
        GET request handler to retrieve energy consumption data from the database
        """

        try:
            small_area_code = request.query_params.get('small_area_code', None)
            SA_db_obj = SA_energy_consumption.objects.filter(
                SA_code=small_area_code).first()
            if (SA_db_obj != None):
                self.response_data = list(SA_energy_consumption.objects.filter(
                    id=SA_db_obj.id).values())  # return data of requested Small_area only
                self.response_message = f'Success. Data fetched from the DB for the small_area {small_area_code}.'
                self.response_status = status.HTTP_200_OK
            else:
                self.response_data = []
                self.response_status = status.HTTP_400_BAD_REQUEST
                self.response_message = f'Failure. Invalid small_area {small_area_code}.'
        except Exception as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            self.response_message= f'Failure. Could not fetch data from the DB for the small_area {small_area_code}.'
            self.response_status = status.HTTP_400_BAD_REQUEST

        # Return response.
        return JsonResponse({'message': self.response_message, 'data': self.response_data}, status=self.response_status, safe=True)


class DublinBikesView(APIView):
    '''
    Class for all the operations related to the Dublin Bikes.
    '''
    # permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs) -> None:
        # Defining logger here to get the name for the class
        self.logger = logging.getLogger(__name__)

    def get(self, request, *args, **kwargs):
        try:
            dublinbikestations = DublinBikeStation.objects.all()
            result = DublinBikesStationSerializer(dublinbikestations, many=True).data
            return Response({"message": "Successfully fetched the required data", "data": result}, 
                            status=status.HTTP_200_OK)
        except Exception as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            return Response({"message": "Some unexpected exception occured. Please try again", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, *args, **kwargs):
        try:
            dublin_bike_data = request.data['dublin_bikes']
            result = []
            for station_data in dublin_bike_data:              
                naive_datetime = datetime.datetime.strptime(station_data.get('last_update'), '%Y-%m-%dT%H:%M:%S')
                timezone_aware_datetime = naive_datetime.astimezone(timezone.get_default_timezone())
                station, created = DublinBikeStation.objects.update_or_create(
                    station_id = station_data.get('station_id'),
                    defaults = {
                        'bike_stands': station_data.get('bike_stands'),
                        'available_bikes': station_data.get('available_bikes'),
                        'usage_percent': station_data.get('usage_percent'),
                        'last_update': timezone_aware_datetime,
                        'status': station_data.get('status'),
                    }
                )
                result.append({
                    'station_id': station.station_id,
                    'created': created
                })
            return Response({"message": "Successfully saved the required data", "data": result},
                            status=status.HTTP_200_OK)
        except KeyError as e:
            return Response({"message": f"Please pass required parameter: {e}", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            return Response({"message": "Some unexpected exception occured. Please try again", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)


class DublinBikesPredictionView(APIView):
    '''
    Class for all the operations related to the Dublin Bikes Prediction.
    '''
    # permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs) -> None:
        # Defining logger here to get the name for the class
        self.logger = logging.getLogger(__name__)

        # self.df_stations = pd.read_csv('cityservices/data/STATION ID - BIKE STANDS.csv')
        self.model = pickle.load(
            open("cityservices/data/RFmodel_lr.pkl", 'rb'))

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


class BinLocationsView(APIView):
    '''
    Class for all the operations related to the Bin Locations.
    '''
    # permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs) -> None:
        # Defining logger here to get the name for the class
        self.logger = logging.getLogger(__name__)

    def get(self, request, *args, **kwargs):
        try:
            with open('cityservices/data/dcc_public_bins_locations.json', 'r') as j:
                return Response({"message": "Successfully fetched the required data", "data": json.load(j)
                                 }, status=status.HTTP_200_OK)
        except Exception as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            return Response({"message": "Some unexpected exception occured. Please try again", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)
