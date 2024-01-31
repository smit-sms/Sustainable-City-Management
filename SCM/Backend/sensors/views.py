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

sensors_noise = [
    '10.1.1.1', '01749', '01508',
    '10118', '01548', '10115', 
    '10.1.1.7', '01870', '01575', 
    '01737', '10.1.1.11', '10.1.1.12', 
    '01550', '01534', '01535', 
    '01509', '01529', '01528'
]

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class AirView(View):

    def get(self, request):
        data = {}
        sensor_serial_number = request.GET.get('sensor_serial_number')
        db_obj_sensor = Sensor.objects.filter(serial_number=sensor_serial_number).first()
        if (db_obj_sensor != None):
            db_obj_pm2_5 = list(Air.objects.filter(sensor_id=db_obj_sensor.id).values())
            pm2_5 = [o['pm2_5'] for o in db_obj_pm2_5]
            datetime_ids = [o['datetime_id'] for o in db_obj_pm2_5]
            dts = [o['datetime'].strftime("%Y-%m-%d %H:%M:%S") for o in DateTime.objects.filter(id__in=datetime_ids).values()]
            data['data'] = {'datetime':dts, 'pm2_5':pm2_5}
            data["message"] = "Success."
            return JsonResponse(data, status=200, safe=True)
        else:
            data['data'] = {'datetime':[], 'pm2_5':[]}
            data['message'] = f'Failure. Invalid sensor {sensor_serial_number}.'
            return JsonResponse(data, status=400, safe=True)
        
    def post(self, request):
        url_root = "https://data.smartdublin.ie/sonitus-api"
        data = {}
        
        # Get sensor ID and do sanity check.
        request_json = json.loads(request.body.decode('utf-8'))
        sensor_serial_number = request_json['sensor_serial_number']
        
        # Fetching data from now to 24 hrs ago.
        datetime_now = datetime.now()
        datetime_yesterday = datetime_now - timedelta(days=1)
        datetime_end = time.mktime(datetime_now.timetuple())
        datetime_start = time.mktime(datetime_yesterday.timetuple())
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
            data['message'] = f"Failure. Could not fetch data from sonitus api due to '{e}'."
            return JsonResponse(data, status=400, safe=True)

        # Add to the database.
        db_obj_sensor = Sensor.objects.filter(serial_number=sensor_serial_number).first()
        if (db_obj_sensor != None):
            for d in data_list:
                dt = datetime.strptime(d['datetime'], "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(tzinfo=pytz.timezone('GMT'))
                db_datetime, db_datetime_created = DateTime.objects.get_or_create(datetime=dt)
                try: # try to fetch data
                    db_pm2_5 = Air.objects.get(pm2_5=d['pm2_5'], datetime_id=db_datetime.id, sensor_id=db_obj_sensor.id)
                    data['message'] = f'Success. Data already exists.'
                except Air.DoesNotExist: # when it does not already exist, add
                    db_pm2_5 = Air(pm2_5=d['pm2_5'], datetime_id=db_datetime.id, sensor_id=db_obj_sensor.id)
                    data['message'] = f'Success. Data saved to DB.'
                    db_pm2_5.save()
        else:
            data['message'] = {f'Failure. Invalid sensor {sensor_serial_number}.'}
            return JsonResponse(data, status=400, safe=True)
        
        return JsonResponse(data, status=200, safe=True)

@method_decorator(csrf_exempt, name='dispatch')
class NoiseView(View):
    def get(self, request):
        data = {}
        sensor_serial_number = request.GET.get('sensor_serial_number')
        db_obj_sensor = Sensor.objects.filter(serial_number=sensor_serial_number).first()
        if (db_obj_sensor != None):
            db_obj_laeq = list(Noise.objects.filter(sensor_id=db_obj_sensor.id).values())
            laeq = [o['laeq'] for o in db_obj_laeq]
            datetime_ids = [o['datetime_id'] for o in db_obj_laeq]
            dts = [o['datetime'].strftime("%Y-%m-%d %H:%M:%S") for o in DateTime.objects.filter(id__in=datetime_ids).values()]
            data['data'] = {'datetime':dts, 'laeq':laeq}
            data["message"] = "Success."
            return JsonResponse(data, status=200, safe=True)
        else:
            data['data'] = {'datetime':[], 'laeq':[]}
            data['message'] = f'Failure. Invalid sensor {sensor_serial_number}.'
            return JsonResponse(data, status=400, safe=True)

    def post(self, request):
        url_root = "https://data.smartdublin.ie/sonitus-api"
        data = {}
        
        # Get sensor ID and do sanity check.
        request_json = json.loads(request.body.decode('utf-8'))
        sensor_serial_number = request_json['sensor_serial_number']
        
        # Fetching data from now to 24 hrs ago.
        datetime_now = datetime.now()
        datetime_yesterday = datetime_now - timedelta(days=1)
        datetime_end = time.mktime(datetime_now.timetuple())
        datetime_start = time.mktime(datetime_yesterday.timetuple())
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
            data['message'] = f"Failure. Could not fetch data from sonitus api due to {e}."
            return JsonResponse(data, status=400, safe=True)
        
        # Add to the database.
        db_obj_sensor = Sensor.objects.filter(serial_number=sensor_serial_number).first()
        if (db_obj_sensor != None):
            for d in data_list:
                dt = datetime.strptime(d['datetime'], "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(tzinfo=pytz.timezone('GMT'))
                db_datetime, db_datetime_created = DateTime.objects.get_or_create(datetime=dt)
                try:
                    db_laeq = Noise.objects.get(laeq=d['laeq'], datetime_id=db_datetime.id, sensor_id=db_obj_sensor.id)
                    data['message'] = f'Success. Data already exists.'
                except Noise.DoesNotExist:
                    db_laeq = Noise(laeq=d['laeq'], datetime_id=db_datetime.id, sensor_id=db_obj_sensor.id)
                    db_laeq.save()
                    data['message'] = f'Success. Data saved to DB.'
        else:
            data['message'] = {f'Failure. Invalid sensor {sensor_serial_number}.'}
            return JsonResponse(data, status=400, safe=True)
        
        return JsonResponse(data, status=200, safe=True)