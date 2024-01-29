import time
import pytz
import json
import requests
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import Sensor, Air, Noise, DateTime
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token

sensors_air = [
    'DCC-AQ2', 'DCC-AQ3', 'DCC-AQ4', 
    'DCC-AQ5', 'DCC-AQ6', 'DCC-AQ10', 
    'TNO2161', 'TNO2162', 'DCC-AQ13', 
    'DCC-AQ17', 'DCC-AQ22', 'DCC-AQ52', 
    'DCC-AQ69', 'TNO4435', 'TNO4438', 
    'TNO4390', 'TNO4324', 'TNO4323', 
    'TNO4437', '0110-000157-000000', 
    'DM30-00530', 'DM30-00531', 'DCC-AQ91'
]

sensors_noise = [
    '10.1.1.1', '01749', '01508',
    '10118', '01548', '10115', 
    '10.1.1.7', '01870', '01575', 
    '01737', '10.1.1.11', '10.1.1.12', 
    '01550', '01534', '01535', 
    '01509', '01529', '01528'
]

# def post(self, request):
#         url_root = "https://data.smartdublin.ie/sonitus-api"
#         data = {}
#         data["message"] = "Response to POST request."
        
#         # Get sensor ID and do sanity check.
#         request_json = json.loads(request.body.decode('utf-8'))
#         sensor_serial_number = request_json['sensor_serial_number']
#         if sensor_serial_number not in sensors_noise:
#             return JsonResponse({'message': 'Not a laeq sensor.'}, status=400, safe=True)
        
#         # Fetching data from now to 24 hrs ago.
#         datetime_now = datetime.now()
#         datetime_yesterday = datetime_now - timedelta(days=1)
#         datetime_end = time.mktime(datetime_now.timetuple())
#         datetime_start = time.mktime(datetime_yesterday.timetuple())
#         print(datetime_start, datetime_end)
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
#             return JsonResponse({'error': f'Failed to fetch data due to {e}'}, status=404, safe=True)

#         data["data"] = data_list

#         # Add to the database.
#         db_obj_sensor = Sensor.objects.filter(serial_number=sensor_serial_number).first()
#         if (db_obj_sensor != None):
#             for d in data_list:
#                 dt = datetime.strptime(d['datetime'], "%Y-%m-%d %H:%M:%S")
#                 dt = dt.replace(tzinfo=pytz.timezone('GMT'))
#                 db_datetime, db_datetime_created = DateTime.objects.get_or_create(datetime=dt)
#                 try:
#                     db_laeq = Noise.objects.get(laeq=d['laeq'], datetime_id=db_datetime.id, sensor_id=db_obj_sensor.id)
#                 except Noise.DoesNotExist:
#                     db_laeq = Noise(laeq=d['laeq'], datetime_id=db_datetime.id, sensor_id=db_obj_sensor.id)
#                     db_laeq.save()
#         else:
#             data['message'] = {'message':'no such sensor'}
#         data["message"] = "Response to POST request."
#         return JsonResponse(data, status=200, safe=True)

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class AirView(View):

    def get(self, request):
        data = {}
        data["message"] = "Response to GET request."

        # Get sensor ID and do sanity check.
        sensor_serial_number = request.GET.get('sensor_serial_number')
        if sensor_serial_number not in sensors_air:
            return JsonResponse({'message': 'Not a pm2.5 sensor.'}, status=400, safe=True)
        
        db_obj_sensor = Sensor.objects.filter(serial_number=sensor_serial_number).first()
        if (db_obj_sensor != None):
            db_obj_pm2_5 = list(Air.objects.filter(sensor_id=db_obj_sensor.id).values())
            pm2_5 = [o['pm2_5'] for o in db_obj_pm2_5]
            datetime_ids = [o['datetime_id'] for o in db_obj_pm2_5]
            dts = [o['datetime'].strftime("%Y-%m-%d %H:%M:%S") for o in DateTime.objects.filter(id__in=datetime_ids).values()]
            data['data'] = {'datetime':dts, 'pm2_5':pm2_5}
            return JsonResponse(data, status=200, safe=True)
        else:
            data['data'] = {'datetime':[], 'pm2_5':[]}
            return JsonResponse(data, status=200, safe=True)
        
    def post(self, request):
        url_root = "https://data.smartdublin.ie/sonitus-api"
        data = {}
        data["message"] = "Response to POST request."
        
        # Get sensor ID and do sanity check.
        request_json = json.loads(request.body.decode('utf-8'))
        sensor_serial_number = request_json['sensor_serial_number']
        if sensor_serial_number not in sensors_air:
            return JsonResponse({'message': 'Not a pm2_5 sensor.'}, status=400, safe=True)
        
        # Fetching data from now to 24 hrs ago.
        datetime_now = datetime.now()
        datetime_yesterday = datetime_now - timedelta(days=1)
        datetime_end = time.mktime(datetime_now.timetuple())
        datetime_start = time.mktime(datetime_yesterday.timetuple())
        print(datetime_start, datetime_end)
        try:
            res = requests.post(f"{url_root}/api/data", json={
                'username': "dublincityapi",
                'password': "Xpa5vAQ9ki",
                'monitor': sensor_serial_number,
                'start': datetime_start,
                'end': datetime_end
            })
            if len(res.text) > 0: 
                data_list = [{'datetime':d['datetime'], 'pm2_5':d['pm2_5']} for d in res.json()]
            else: data_list = []
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch data due to {e}'}, status=404, safe=True)

        data["data"] = data_list

        # Add to the database.
        db_obj_sensor = Sensor.objects.filter(serial_number=sensor_serial_number).first()
        if (db_obj_sensor != None):
            for d in data_list:
                dt = datetime.strptime(d['datetime'], "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(tzinfo=pytz.timezone('GMT'))
                db_datetime, db_datetime_created = DateTime.objects.get_or_create(datetime=dt)
                try:
                    db_pm2_5 = Air.objects.get(pm2_5=d['pm2_5'], datetime_id=db_datetime.id, sensor_id=db_obj_sensor.id)
                except Air.DoesNotExist:
                    db_pm2_5 = Air(pm2_5=d['pm2_5'], datetime_id=db_datetime.id, sensor_id=db_obj_sensor.id)
                    db_pm2_5.save()
        else:
            data['message'] = {'message':'no such sensor'}
        data["message"] = "Response to POST request."
        
        return JsonResponse(data, status=200, safe=True)

@method_decorator(csrf_exempt, name='dispatch')
class NoiseView(View):
    def get(self, request):
        data = {}
        data["message"] = "Response to GET request."

        # Get sensor ID and do sanity check.
        sensor_serial_number = request.GET.get('sensor_serial_number')
        if sensor_serial_number not in sensors_noise:
            return JsonResponse({'message': 'Not a laeq sensor.'}, status=400, safe=True)
        
        db_obj_sensor = Sensor.objects.filter(serial_number=sensor_serial_number).first()
        if (db_obj_sensor != None):
            db_obj_laeq = list(Noise.objects.filter(sensor_id=db_obj_sensor.id).values())
            laeq = [o['laeq'] for o in db_obj_laeq]
            datetime_ids = [o['datetime_id'] for o in db_obj_laeq]
            dts = [o['datetime'].strftime("%Y-%m-%d %H:%M:%S") for o in DateTime.objects.filter(id__in=datetime_ids).values()]
            data['data'] = {'datetime':dts, 'laeq':laeq}
            return JsonResponse(data, status=200, safe=True)
        else:
            data['data'] = {'datetime':[], 'laeq':[]}
            return JsonResponse(data, status=200, safe=True)

    def post(self, request):
        url_root = "https://data.smartdublin.ie/sonitus-api"
        data = {}
        data["message"] = "Response to POST request."
        
        # Get sensor ID and do sanity check.
        request_json = json.loads(request.body.decode('utf-8'))
        sensor_serial_number = request_json['sensor_serial_number']
        if sensor_serial_number not in sensors_noise:
            return JsonResponse({'message': 'Not a laeq sensor.'}, status=400, safe=True)
        
        # Fetching data from now to 24 hrs ago.
        datetime_now = datetime.now()
        datetime_yesterday = datetime_now - timedelta(days=1)
        datetime_end = time.mktime(datetime_now.timetuple())
        datetime_start = time.mktime(datetime_yesterday.timetuple())
        print(datetime_start, datetime_end)
        try:
            res = requests.post(f"{url_root}/api/data", json={
                'username': "dublincityapi",
                'password': "Xpa5vAQ9ki",
                'monitor': sensor_serial_number,
                'start': datetime_start,
                'end': datetime_end
            })
            if len(res.text) > 0: 
                data_list = [{'datetime':d['datetime'], 'laeq':d['laeq']} for d in res.json()]
            else: data_list = []
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch data due to {e}'}, status=404, safe=True)

        data["data"] = data_list

        # Add to the database.
        db_obj_sensor = Sensor.objects.filter(serial_number=sensor_serial_number).first()
        if (db_obj_sensor != None):
            for d in data_list:
                dt = datetime.strptime(d['datetime'], "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(tzinfo=pytz.timezone('GMT'))
                db_datetime, db_datetime_created = DateTime.objects.get_or_create(datetime=dt)
                try:
                    db_laeq = Noise.objects.get(laeq=d['laeq'], datetime_id=db_datetime.id, sensor_id=db_obj_sensor.id)
                except Noise.DoesNotExist:
                    db_laeq = Noise(laeq=d['laeq'], datetime_id=db_datetime.id, sensor_id=db_obj_sensor.id)
                    db_laeq.save()
        else:
            data['message'] = {'message':'no such sensor'}
        data["message"] = "Response to POST request."
        return JsonResponse(data, status=200, safe=True)