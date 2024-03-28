import time
import pytz
import json
import requests
from datetime import datetime
from django.views import View
from django.http import JsonResponse
from .models import Snapshot, Station
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class ViewSnapshot(View):
    response_message = ''
    response_status = 200
    response_data = []

    def get(self, request):
        """
        Gets data from the bikes_snapshot table in the DB.
        @param request: Requests of the form {
            'station_id': <int>,
            'time_start': <datetime>,
            'time_end': <datetime>
        }
        @return response: 
        """
        # Get station ID, start and end time from the request.
        station_id = request.GET.get('station_id')
        time_start = datetime.strptime(
            request.GET.get('time_start'), "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=pytz.timezone('GMT'))
        time_end = datetime.strptime(
            request.GET.get('time_end'), "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=pytz.timezone('GMT'))
        # Try to get the requested station.
        station = Station.objects.filter(id=station_id).first()
        if (station != None): # If requested station does exist, then ...
            try: # Try to fetch data from the database related to this station.
                self.response_data = list(Snapshot.objects.filter(
                    station_id=station.id,
                    last_update__gte=time_start, # Inclusive.
                    last_update__lt=time_end # Exclusive.
                ).values()) # Return data of requested sensor only.
                self.response_message = (
                    "Success. Data fetched from DB "
                    + f"for bike station {station_id}."
                )
                self.response_status = 200
            except Exception as e: # In case of fetching error ...
                self.response_message= (
                    "Failure. Could not fetch data from DB for "
                    + f"bike station {station_id} due to '{e}'."
                )
                self.response_status = 400
                self.self.response_data = []
        else: # If requested sensor does not exist, then ...
            self.response_data = []
            self.response_status = 400
            self.response_message = f"Failure. Invalid bike station '{station_id}'."

        return JsonResponse({
            'message': self.response_message,
            'data': self.response_data
        } , status=self.response_status, safe=True)

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