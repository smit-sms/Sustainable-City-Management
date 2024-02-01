import time
import pytz
import json
import requests
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import Sensor, Air, Noise
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class AirView(View):

    response_message = ''
    response_status = 200
    response_data = []

    def get(self, request):
        sensor_serial_number = request.GET.get('sensor_serial_number')
        sensor_db_obj = Sensor.objects.filter(serial_number=sensor_serial_number).first() # get requested sensor for the sensors table in the DB
        if (sensor_db_obj != None): # if requested sensor does exist, then ...
            try: # try to fetch data from the database.
                self.response_data = list(Air.objects.filter(sensor_id=sensor_db_obj.id).values()) # return data of requested sensor only
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
        try:
            # Request data @ https://data.smartdublin.ie/sonitus-api.
            res = requests.post(f"{url_root}/api/data", json={ 
                'username': "dublincityapi",
                'password': "Xpa5vAQ9ki",
                'monitor': sensor_serial_number,
                'start': datetime_start,
                'end': datetime_end
            })
            if len(res.text) > 0: # if response data is not empty then ...
                res_data = [{'datetime':d['datetime'], 'pm2_5':d['pm2_5']} for d in res.json()]
            else: # if response data is empty then ...
                res_data = []

            # Add to the database.
            sensor_db_obj = Sensor.objects.filter(serial_number=sensor_serial_number).first() # Get requested sensor from the database.
            if (sensor_db_obj != None): # If requested sensor exists then ...
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
            else: # If requested sensor does not exist then ...
                self.response_message = {f'Failure. Invalid sensor {sensor_serial_number}.'}
                self.response_status = 400 
        except Exception as e:
            self.response_message = f"Failure. Could not fetch data from sonitus api due to '{e}'."
            self.response_status = 400
        
        # Return response.
        return JsonResponse({'message': self.response_message} , status=self.response_status, safe=True)

# @method_decorator(csrf_exempt, name='dispatch')
class NoiseView(View):
    def get(self, request):
        pass
#         data = {}
#         sensor_serial_number = request.GET.get('sensor_serial_number')
#         db_obj_sensor = Sensor.objects.filter(serial_number=sensor_serial_number).first()
#         if (db_obj_sensor != None):
#             db_obj_laeq = list(Noise.objects.filter(sensor_id=db_obj_sensor.id).values())
#             datetime_ids = [o['datetime_id'] for o in db_obj_laeq]
#             data_processed = {'datetime_id': [], 'laeq': []}
#             for i in range(len(db_obj_laeq)):
#                 data_processed['laeq'].append(db_obj_laeq[i]['laeq'])
#                 data_processed['datetime_id'].append(db_obj_laeq[i]['datetime_id'])
#             dts = [o['datetime'].strftime("%Y-%m-%d %H:%M:%S") for o in DateTime.objects.filter(id__in=data_processed['datetime_id']).values()]
#             data['data'] = {'datetime':dts, 'laeq':data_processed['laeq']}
#             data["message"] = "Success."
#             return JsonResponse(data, status=200, safe=True)
#         else:
#             data['data'] = {'datetime':[], 'laeq':[]}
#             data['message'] = f'Failure. Invalid sensor {sensor_serial_number}.'
#             return JsonResponse(data, status=400, safe=True)

    def post(self, request):
        pass
#         url_root = "https://data.smartdublin.ie/sonitus-api"
#         data = {}
        
#         # Get sensor ID and do sanity check.
#         request_json = json.loads(request.body.decode('utf-8'))
#         sensor_serial_number = request_json['sensor_serial_number']
        
#         # Fetching data from now to 24 hrs ago.
#         datetime_now = datetime.now()
#         datetime_yesterday = datetime_now - timedelta(days=1)
#         datetime_end = time.mktime(datetime_now.timetuple())
#         datetime_start = time.mktime(datetime_yesterday.timetuple())
#         try:
#             res = requests.post(f"{url_root}/api/data", json={
#                 'username': "dublincityapi",
#                 'password': "Xpa5vAQ9ki",
#                 'monitor': sensor_serial_number,
#                 'start': datetime_start,
#                 'end': datetime_end
#             })
#             if len(res.text) > 0: 
#                 data_list = [{'datetime':d['datetime'], 'laeq':d['laeq']} for d in res.json()]
#             else: data_list = []
#         except Exception as e:
#             data['message'] = f"Failure. Could not fetch data from sonitus api due to {e}."
#             return JsonResponse(data, status=400, safe=True)
        
#         # Add to the database.
#         db_obj_sensor = Sensor.objects.filter(serial_number=sensor_serial_number).first()
#         if (db_obj_sensor != None):
#             for d in data_list:
#                 dt = datetime.strptime(d['datetime'], "%Y-%m-%d %H:%M:%S")
#                 dt = dt.replace(tzinfo=pytz.timezone('GMT'))
#                 db_datetime, db_datetime_created = DateTime.objects.get_or_create(datetime=dt)
#                 try:
#                     db_laeq = Noise.objects.get(laeq=d['laeq'], datetime_id=db_datetime.id, sensor_id=db_obj_sensor.id)
#                     data['message'] = f'Success. Data already exists.'
#                 except Noise.DoesNotExist:
#                     db_laeq = Noise(laeq=d['laeq'], datetime_id=db_datetime.id, sensor_id=db_obj_sensor.id)
#                     db_laeq.save()
#                     data['message'] = f'Success. Data saved to DB.'
#         else:
#             data['message'] = {f'Failure. Invalid sensor {sensor_serial_number}.'}
#             return JsonResponse(data, status=400, safe=True)
        
#         return JsonResponse(data, status=200, safe=True)