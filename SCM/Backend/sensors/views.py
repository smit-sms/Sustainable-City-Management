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
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime, timedelta
from .models import Sensor, Air, Noise
from .utils import *

class AirView(APIView):
    '''
    Class for all the operations related to the Bus Routes.
    '''
    # permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs) -> None:
        # Defining logger here to get the name for the class
        self.logger = logging.getLogger(__name__)
        self.sonitos_base_url = os.getenv('SONITOS_API_URL')

    def get(self, request, *args, **kwargs):
        """
        GET request handler to retrieve Air Pollution data
        """
        try:
            current_time = datetime.now()
            minute = (current_time.minute // 15) * 15
            closest_past_quarter_hour = current_time.replace(minute=minute, second=0, microsecond=0)

            # Define the start and end times for the query
            datetime_end = closest_past_quarter_hour
            datetime_start = datetime_end - timedelta(minutes=15)

            sensors = Sensor.objects.filter(sensor_type='air')
            result = []

            for sensor in sensors:
                try:
                    air_obj = Air.objects.get(sensor=sensor)
                    result.append({
                        'serial_number': sensor.serial_number,
                        'latitude': sensor.latitude,
                        'longitude': sensor.longitude,
                        'sensor_type': sensor.sensor_type,
                        'pm2_5': air_obj.pm2_5,
                        'datetime': datetime_end,
                    })
                except Air.DoesNotExist:
                    continue
                    # No data found then fetch from external API
                    response = requests.post(f"{self.sonitos_base_url}/api/data", json={
                        'username': os.getenv('SONITOS_USERNAME'),
                        'password': os.getenv('SONITOS_PASSWORD'),
                        'monitor': sensor.serial_number,
                        'start': datetime_to_unix_timestamp(datetime_start),
                        'end': datetime_to_unix_timestamp(datetime_end)
                    })

                    if response.status_code == 200 and response.text != '' and response.text != 'error':
                        api_data = response.json()

                        for entry in api_data:
                            if entry != 'error':
                                # Create and save a new Air instance for each entry
                                datetime_str = entry.get('datetime')
                                datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                                datetime_obj_gmt = pytz.timezone('GMT').localize(datetime_obj)
                                sensor_value = entry.get('pm2_5') if entry.get('pm2_5') else entry.get('no2')
                                air_instance, created = Air.objects.update_or_create(
                                    sensor=sensor,
                                    defaults={'pm2_5': sensor_value, 'datetime': datetime_obj_gmt}
                                )

                                # Add the newly fetched data to the response
                                result.append({
                                    'serial_number': sensor.serial_number,
                                    'latitude': sensor.latitude,
                                    'longitude': sensor.longitude,
                                    'sensor_type': sensor.sensor_type,
                                    'pm2_5': air_instance.pm2_5,
                                    'datetime': air_instance.datetime,
                                })
                
            return Response({"message": "Successfully fetched the required data", "len":len(result), "data": result},
                        status=status.HTTP_200_OK)
        except KeyError as e:
            return Response({"message": f"Please pass required parameter: {e}", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)
        except Sensor.DoesNotExist:
            return Response({"message": "The given sensor not found. Please check and try again.", "data": None},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            self.logger.exception(f'Some unexpected exception occured: {e}')
            return Response({"message": f"Some unexpected exception occured: {e}. Please try again", "data": None},
                            status=status.HTTP_400_BAD_REQUEST)

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class AirViewOld(View):
    response_message = ''
    response_status = 200
    response_data = []

    def get(self, request):
        sensor_serial_number = request.GET.get('sensor_serial_number')
        time_start = datetime.strptime(request.GET.get('time_start'), "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone('GMT'))
        time_end = datetime.strptime(request.GET.get('time_end'), "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone('GMT'))
        sensor_db_obj = Sensor.objects.filter(serial_number=sensor_serial_number).first() # get requested sensor for the sensors table in the DB
        if (sensor_db_obj != None): # if requested sensor does exist, then ...
            try: # try to fetch data from the database.
                self.response_data = list(Air.objects.filter(
                    sensor_id=sensor_db_obj.id,
                    datetime__gte=time_start, # Inclusive
                    datetime__lt=time_end # Exclusive
                ).values()) # return data of requested sensor only
                self.response_message = f'Success. Data fetched from the DB for the air sensor {sensor_serial_number}.'
                self.response_status = 200
            except Exception as e: # if there was some error with fetching data then ...
                self.response_message= f'Failure. Could not fetch data from the DB for the air sensor {sensor_serial_number}.'
                self.response_status = 400
        else: # if requested sensor does not exist, then ...
            self.response_data = []
            self.response_status = 400
            self.response_message = f'Failure. Invalid sensor {sensor_serial_number}.'
    
        # Return response.
        response = JsonResponse({'message': self.response_message, 'data': self.response_data}, status=self.response_status, safe=True)
        return response
        
    def post(self, request):
        url_root = "https://data.smartdublin.ie/sonitus-api"
        
        # Get requested sensor's serial number.
        request_json = json.loads(request.body.decode('utf-8'))
        sensor_serial_number = request_json['sensor_serial_number']
        
        # Fetching data from now to 24 hrs ago.
        datetime_now = datetime.now()
        datetime_yesterday = datetime_now - timedelta(days=1)
        datetime_end = time.mktime(datetime_now.timetuple()) # Now.
        datetime_start = time.mktime(datetime_yesterday.timetuple()) # 24 hrs ago.

        sensor_db_obj = Sensor.objects.filter(serial_number=sensor_serial_number).first() # Get requested sensor from the database.
        if (sensor_db_obj != None): # If requested sensor exists then ...
            try: # Try to request data @ https://data.smartdublin.ie/sonitus-api.
                res = requests.post(f"{url_root}/api/data", json={ 
                    'username': os.getenv('SONITOS_USERNAME'),
                    'password': os.getenv('SONITOS_PASSWORD'),
                    'monitor': sensor_serial_number,
                    'start': datetime_start,
                    'end': datetime_end
                })
                if len(res.text) > 0: # if response data is not empty then ...
                    res_data = [{'datetime':d['datetime'], 'pm2_5':d['pm2_5']} for d in res.json()]
                else: # if response data is empty then ...
                    res_data = []
                for d in res_data: # Process data received from the API.
                    dt = datetime.strptime(d['datetime'], "%Y-%m-%d %H:%M:%S") # Extract datetime in the correct format.
                    dt = dt.replace(tzinfo=pytz.timezone('GMT')) # Add timezone information.
                    try: # Try to save air data into the database.
                        air_db = Air(pm2_5=d['pm2_5'], datetime=dt, sensor_id=sensor_db_obj.id)
                        air_db.save()
                        self.response_message = f'Success. Data saved to DB.'
                        self.response_status = 200
                    except Exception as e: # If something goes wrong with the save operation ...
                        self.response_message = f'Failure. Data could not be saved to the DB due to "{e}".'
            except Exception as e:
                self.response_message = f"Failure. Could not fetch data from sonitus api due to '{e}'."
                self.response_status = 400
        else: # If requested sensor does not exist then ...
            self.response_message = f'Failure. Invalid sensor {sensor_serial_number}.'
            self.response_status = 400 
        
        # Return response.
        return JsonResponse({'message': self.response_message} , status=self.response_status, safe=True)

@method_decorator(csrf_exempt, name='dispatch')
class NoiseView(View):
    response_message = ''
    response_status = 200
    response_data = []

    def get(self, request):
        sensor_serial_number = request.GET.get('sensor_serial_number')
        time_start = datetime.strptime(request.GET.get('time_start'), "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone('GMT'))
        time_end = datetime.strptime(request.GET.get('time_end'), "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone('GMT'))
        sensor_db_obj = Sensor.objects.filter(serial_number=sensor_serial_number).first() # get requested sensor for the sensors table in the DB
        if (sensor_db_obj != None): # if requested sensor does exist, then ...
            try: # try to fetch data from the database.
                self.response_data = list(Noise.objects.filter(
                    sensor_id=sensor_db_obj.id,
                    datetime__gte=time_start, # Inclusive
                    datetime__lt=time_end # Exclusive
                ).values()) # return data of requested sensor only
                self.response_message = f'Success. Data fetched from the DB for the air sensor {sensor_serial_number}.'
                self.response_status = 200
            except Exception as e: # if there was some error with fetching data then ...
                self.response_message= f'Failure. Could not fetch data from the DB for the air sensor {sensor_serial_number}.'
                self.response_status = 400
        else: # if requested sensor does not exist, then ...
            self.response_data = []
            self.response_status = 400
            self.response_message = f'Failure. Invalid sensor {sensor_serial_number}.'
    
        # Return response.
        return JsonResponse({'message': self.response_message, 'data': self.response_data}, status=self.response_status, safe=True)
        
    def post(self, request):
        url_root = "https://data.smartdublin.ie/sonitus-api"
        
        # Get requested sensor's serial number.
        request_json = json.loads(request.body.decode('utf-8'))
        sensor_serial_number = request_json['sensor_serial_number']
        
        # Fetching data from now to 24 hrs ago.
        datetime_now = datetime.now()
        datetime_yesterday = datetime_now - timedelta(days=1)
        datetime_end = time.mktime(datetime_now.timetuple()) # Now.
        datetime_start = time.mktime(datetime_yesterday.timetuple()) # 24 hrs ago.

        sensor_db_obj = Sensor.objects.filter(serial_number=sensor_serial_number).first() # Get requested sensor from the database.
        if (sensor_db_obj != None): # If requested sensor exists then ...
            try: # Try to request data @ https://data.smartdublin.ie/sonitus-api.
                res = requests.post(f"{url_root}/api/data", json={ 
                    'username': os.getenv('SONITOS_USERNAME'),
                    'password': os.getenv('SONITOS_PASSWORD'),
                    'monitor': sensor_serial_number,
                    'start': datetime_start,
                    'end': datetime_end
                })
                if len(res.text) > 0: # if response data is not empty then ...
                    res_data = [{'datetime':d['datetime'], 'laeq':d['laeq']} for d in res.json()]
                else: # if response data is empty then ...
                    res_data = []
                for d in res_data: # Process data received from the API.
                    dt = datetime.strptime(d['datetime'], "%Y-%m-%d %H:%M:%S") # Extract datetime in the correct format.
                    dt = dt.replace(tzinfo=pytz.timezone('GMT')) # Add timezone information.
                    try: # Try to save air data into the database.
                        noise_db = Noise(laeq=d['laeq'], datetime=dt, sensor_id=sensor_db_obj.id)
                        noise_db.save()
                        self.response_message = f'Success. Data saved to DB.'
                        self.response_status = 200
                    except Exception as e: # If something goes wrong with the save operation ...
                        self.response_message = f'Failure. Data could not be saved to the DB due to "{e}".'
            except Exception as e:
                self.response_message = f"Failure. Could not fetch data from sonitus api due to '{e}'."
                self.response_status = 400
        else: # If requested sensor does not exist then ...
            self.response_message = f'Failure. Invalid sensor {sensor_serial_number}.'
            self.response_status = 400 
        
        # Return response.
        return JsonResponse({'message': self.response_message} , status=self.response_status, safe=True)

class AirPredictions(APIView):
    pass
