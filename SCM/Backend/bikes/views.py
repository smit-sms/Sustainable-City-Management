import time
import pytz
import json
import requests
from .models import Snapshot
from datetime import datetime
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class ViewSnapshot(View):
    response_message = ''
    response_status = 200
    response_data = []

    def post(self, request):
        """ 
        Saves given data to DB in the bikes_snapshot table. 
        @param request: Requests of the form {
            'snapshot':[{station 1 data}, {station 2 data}, ...]
        }
        """
        request_json = json.loads(request.body.decode('utf-8'))
        snapshot = request_json['snapshot']

        try:
            for station_data in snapshot:
                # Format date time data.
                station_data['last_update'] = datetime.strptime(
                    station_data['last_update'], 
                    "%Y-%m-%dT%H:%M:%S"
                )
                station_data['last_update'] = station_data['last_update'].replace(
                    tzinfo=pytz.timezone('GMT')
                )
                snapshot_db, created = Snapshot.objects.update_or_create(
                    station_id=station_data['station_id'], 
                    usage_percent=station_data['usage_percent'], 
                    bike_stands=station_data['bike_stands'],
                    available_bikes=station_data['available_bikes'],
                    last_update=station_data['last_update'],
                    status=station_data['status']
                )
            self.response_message = f"Success. Saved snapshot of bike data for every station."
            self.response_status = 200
        except Exception as e:
            self.response_message = f"Failure. Could not save snapshot of bike data due to '{e}'."
            self.response_status = 400
        
        # Return response.
        return JsonResponse({
            'message': self.response_message,
        } , status=self.response_status, safe=True)