import os
import time
import pytz
import json
import requests
import logging
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from requests.exceptions import HTTPError

from datetime import datetime, timedelta
from .models import Sensor, Air, Noise
from .utils import *
import numpy as np
import pandas as pd
import pickle


class AirNoiseView(APIView):
    '''
    Class for all the operations related to the Air and Noise.
    '''
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs) -> None:
        self.logger = logging.getLogger(__name__)
        self.airnoise_api = os.getenv('AIRNOISE_URL')
        
    def get(self, request, *args, **kwargs):
        """
        GET request handler to retrieve the Air and Noise Pollution Data from API
        """
        try:
            result = []
            res = requests.get(f"{self.airnoise_api}")
            for record in res.json():
                datetime_str = record['latest_reading']['recorded_at']
                datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                datetime_obj_gmt = pytz.timezone('GMT').localize(datetime_obj)
                try:
                    sensor = Sensor.objects.get(serial_number=record['serial_number'])
                except Sensor.DoesNotExist:
                    continue
                if record['monitor_type']['category'] == 'noise':
                    sensor_value = record['latest_reading']['laeq']
                    unit = 'laeq'
                    noise_instance, created = Noise.objects.update_or_create(
                        sensor=sensor,
                        defaults={'laeq': sensor_value, 'datetime': datetime_obj_gmt}
                    )
                else:
                    sensor_value = record['latest_reading']['pm2_5'] if record['latest_reading']['pm2_5'] else 1.0
                    unit = 'pm2.5'
                    air_instance, created = Air.objects.update_or_create(
                        sensor=sensor,
                        defaults={'pm2_5': sensor_value, 'datetime': datetime_obj_gmt}
                    )
                    
                result.append({
                    'serial_number': record['code'],
                    'latitude': record['latitude'],
                    'longitude': record['longitude'],
                    'sensor_type': record['monitor_type']['category'],
                    'unit': unit,
                    'value': sensor_value,
                    'status': record['latest_reading']['status'],
                    'datetime': datetime_str,
                })
            return Response({"message": "Successfully fetched the required data", "data": result},
                        status=status.HTTP_200_OK)
        except HTTPError as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            return Response({"message": f"unexpected exception occured with the API, please try again", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)
        except Sensor.DoesNotExist:
            return Response({"message": "The sensor not found. Please check and try again.", "data": None},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            return Response({"message": f"Some unexpected exception occured: {e}. Please try again", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)

class AirPredictions(APIView):
    '''
    Class for all the operations related to the Air Predictions.
    '''
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs) -> None:
        self.logger = logging.getLogger(__name__)
        self.model = pickle.load(open("sensors/data/air_model.pkl", 'rb'))
        
    def get(self, request, *args, **kwargs):
        """
        GET request handler to retrieve the Air predictions
        """
        try:
            serial_number_mapping = {'DCC-AQ4': 9,'DCC-AQ5': 10,'DCC-AQ6': 12,'DCC-AQ10': 3,'DCC-AQ91': 14,'DM30-00531': 16,
                                     'DM30-00530': 15,'0110-000141-000000': 0,'0110-000157-000000': 1,
                                     'TNO4437': 23,'TNO4438': 24,'TNO4435': 22,'DCC-AQ69': 13,'DCC-AQ52': 11,'DCC-AQ22': 7,
                                     'DCC-AQ17': 5,'DCC-AQ13': 4,'TNO2162': 18,'TNO2161': 17,'TNO4390': 21,'TNO4324': 20,
                                     'TNO4323': 19,'DCC-AQ1': 2,'DCC-AQ2': 6,'DCC-AQ3': 8}

            pred_df = pd.DataFrame(columns=['datetime', 'serial_number', 'pm2_5_lag1', 'latitude', 'longitude'])
            curr_time = pd.to_datetime(datetime.now()) + pd.Timedelta(hours=1)
            air_sensors = Air.objects.all().prefetch_related('sensor')
            for air_sensor in air_sensors:
                if air_sensor.sensor.serial_number in serial_number_mapping:
                    new_row = {
                        'datetime': curr_time,
                        'serial_number': air_sensor.sensor.serial_number,
                        'pm2_5_lag1': air_sensor.pm2_5,
                        'latitude': air_sensor.sensor.latitude,
                        'longitude': air_sensor.sensor.longitude
                    }
                    pred_df = pred_df._append(new_row, ignore_index=True)

            pred_df['hour'] = pred_df['datetime'].dt.hour
            pred_df['day'] = pred_df['datetime'].dt.day
            pred_df['dayofweek'] = pred_df['datetime'].dt.dayofweek
            pred_df['month'] = pred_df['datetime'].dt.month
            pred_df['serial_number_encoded'] = pred_df['serial_number'].map(serial_number_mapping)
            pred_features = ['pm2_5_lag1','serial_number_encoded', 'hour', 'day', 'dayofweek', 'month']
            pred_df['predicted_pm2_5'] = self.model.predict(pred_df[pred_features])

            result = []
            for _, row in pred_df.iterrows():
                latitude = row['latitude']
                longitude = row['longitude']
                sensor_type = "air"
                unit = "pm2.5"
                sensor_value = row['predicted_pm2_5']
                if 0 <= sensor_value <= 35:
                    color = 'green'
                elif 36 <= sensor_value <= 53:
                    color = 'orange'
                elif 54 <= sensor_value <= 70:
                    color = 'red'
                else:
                    color = 'purple'
                datetime_str = row['datetime'].strftime('%Y-%m-%d %H:%M:%S')  # Format datetime as string

                result.append({
                    'serial_number': row['serial_number'],
                    'latitude': latitude,
                    'longitude': longitude,
                    'sensor_type': sensor_type,
                    'unit': unit,
                    'value': sensor_value,
                    'status': color,
                    'datetime': datetime_str,
                })

            return Response({"message": "Successfully fetched the required data", "data": result},
                        status=status.HTTP_200_OK)
        except Exception as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            return Response({"message": f"Some unexpected exception occured: {e}. Please try again", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)


class NoisePredictions(APIView):
    '''
    Class for all the operations related to the Noise Predictions.
    '''
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs) -> None:
        self.logger = logging.getLogger(__name__)
        self.model = pickle.load(open("sensors/data/noise_model.pkl", 'rb'))
        
    def get(self, request, *args, **kwargs):
        """
        GET request handler to retrieve the Noise predictions
        """
        try:
            serial_number_mapping = {'01508': 0,'01509': 1,'01528': 2,'01529': 3,'01534': 4,'01535': 5,'01548': 6,'01550': 7,'01575': 8,'01737': 9,'01749': 10,'01870': 11,'10.1.1.1': 12,'10.1.1.11': 13,'10.1.1.12': 14,'10.1.1.7': 15,'10115': 16,'10118': 17}

            pred_df = pd.DataFrame(columns=['datetime', 'serial_number', 'laeq_lag1', 'latitude', 'longitude'])
            curr_time = pd.to_datetime(datetime.now())  + pd.Timedelta(hours=1)
            noise_sensors = Noise.objects.all().prefetch_related('sensor')
            for noise_sensor in noise_sensors:
                if noise_sensor.sensor.serial_number in serial_number_mapping:
                    new_row = {
                        'datetime': curr_time,
                        'serial_number': noise_sensor.sensor.serial_number,
                        'laeq_lag1': noise_sensor.laeq,
                        'latitude': noise_sensor.sensor.latitude,
                        'longitude': noise_sensor.sensor.longitude
                    }
                    pred_df = pred_df._append(new_row, ignore_index=True)

            pred_df['hour'] = pred_df['datetime'].dt.hour
            pred_df['day'] = pred_df['datetime'].dt.day
            pred_df['dayofweek'] = pred_df['datetime'].dt.dayofweek
            pred_df['month'] = pred_df['datetime'].dt.month
            pred_df['sensor_encoded'] = pred_df['serial_number'].map(serial_number_mapping)
            pred_features = ['laeq_lag1', 'sensor_encoded', 'hour', 'day', 'dayofweek', 'month']
            pred_df['predicted_laeq'] = self.model.predict(pred_df[pred_features])

            result = []
            for _, row in pred_df.iterrows():
                latitude = row['latitude']
                longitude = row['longitude']
                sensor_type = "noise"
                unit = "laeq"
                sensor_value = row['predicted_laeq']
                if 0 <= sensor_value <= 54:
                    color = 'green'
                elif 55 <= sensor_value <= 64:
                    color = 'orange'
                elif 65 <= sensor_value <= 75:
                    color = 'red'
                else:
                    color = 'purple'
                datetime_str = row['datetime'].strftime('%Y-%m-%d %H:%M:%S')  # Format datetime as string

                result.append({
                    'serial_number': row['serial_number'],
                    'latitude': latitude,
                    'longitude': longitude,
                    'sensor_type': sensor_type,
                    'unit': unit,
                    'value': sensor_value,
                    'status': color,
                    'datetime': datetime_str,
                })

            return Response({"message": "Successfully fetched the required data", "data": result},
                        status=status.HTTP_200_OK)
        except Exception as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            return Response({"message": f"Some unexpected exception occured: {e}. Please try again", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)
