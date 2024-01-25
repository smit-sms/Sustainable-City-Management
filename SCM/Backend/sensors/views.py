import time
import pytz
import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
from .views import Sensor, Air, Noise, DateTime

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

# Create your views here.
def air_pm2_5(request):
    url_root = "https://data.smartdublin.ie/sonitus-api"
    data = {}
    if request.method == 'POST':
        request_json = json.loads(request.body.decode('utf-8'))
        monitor = request_json['monitor']
        if monitor not in sensors_air:
            return JsonResponse({'bad request': 'Not a pm2.5 monitor.'}, status=400, safe=True)
        datetime_now = datetime.now()
        datetime_yesterday = datetime_now - timedelta(days=1)
        datetime_end = time.mktime(datetime_now.timetuple())
        datetime_start = time.mktime(datetime_yesterday.timetuple())

        res = requests.post(f"{url_root}/api/data", json={
            'username': "dublincityapi",
            'password': "Xpa5vAQ9ki",
            'monitor': monitor,
            'start': datetime_start,
            'end': datetime_end
        })
        try:
            if len(res.text) > 0: 
                data_list = [{'datetime':d['datetime'], 'pm2_5':d['pm2_5']} for d in res.json()]
            else: data_list = []
        except Exception as e:
            return JsonResponse({'error': 'Failed to fetch data.'}, status=403, safe=True)

        data["text"] = "Response to POST request."
        data["data"] = data_list

        # Add to the database.
        db_monitor, db_monitor_created = Sensor.objects.get_or_create(serial_number=monitor)
        for d in data_list:
            dt = datetime.strptime(d['datetime'], "%Y-%m-%d %H:%M:%S")
            dt = dt.replace(tzinfo=pytz.timezone('GMT'))
            db_datetime, db_datetime_created = DateTime.objects.get_or_create(datetime=dt)
            try:
                db_pm2_5 = Air.objects.get(pm2_5=d['pm2_5'], datetime_id=db_datetime.id, monitor_id=db_monitor.id)
            except Air.DoesNotExist:
                db_pm2_5 = Air(pm2_5=d['pm2_5'], datetime_id=db_datetime.id, monitor_id=db_monitor.id)
                db_pm2_5.save()
        return JsonResponse(data, status=200, safe=True)
    
    else: # GET
        data["text"] = "Response to GET request."
        monitor_sn = request.GET.get('monitor')
        db_obj_monitor = Sensor.objects.filter(serial_number=monitor_sn).first()
        if (db_obj_monitor != None):
            db_obj_pm2_5 = list(Air.objects.filter(monitor_id=db_obj_monitor.id).values())
            pm2_5 = [o['pm2_5'] for o in db_obj_pm2_5]
            datetime_ids = [o['datetime_id'] for o in db_obj_pm2_5]
            dts = [o['datetime'].strftime("%Y-%m-%d %H:%M:%S") for o in DateTime.objects.filter(id__in=datetime_ids).values()]
            data['data'] = {'datetime':dts, 'pm2_5':pm2_5}
            return JsonResponse(data, status=200, safe=True)
        else:
            data['data'] = {'datetime':[], 'pm2_5':[]}
            return JsonResponse(data, status=200, safe=True)