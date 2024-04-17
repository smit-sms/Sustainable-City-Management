import csv, datetime
from cityservices.models import DublinBikeStation
from django.utils import timezone

def run():
    try:
        stations = open('cityservices/data/dublin-bike-stations.csv', encoding='utf8')
        stations = csv.reader(stations)

        # skip the 1st row
        next(stations)
        # Flush the DB tables
        DublinBikeStation.objects.all().delete()
        
        naive_datetime = datetime.datetime.strptime(str(datetime.datetime.now()).split('.')[0], '%Y-%m-%d %H:%M:%S')
        timezone_aware_datetime = naive_datetime.astimezone(timezone.get_default_timezone())

        for row in stations:
            DublinBikeObj = DublinBikeStation(
                station_id = row[0],
                name = row[1],
                bike_stands = row[4],
                latitude = row[2],
                longitude = row[3],
                available_bikes=0,
                usage_percent=0,
                last_update=timezone_aware_datetime,
                status='open'
            )
            DublinBikeObj.save()

        print('Successfully loaded the data for Dublin Bike Stations.')

    except Exception as e:
        print(e)
        print(f'Some unexpected exception occured: {e}. Dropping all data in Dublin Bike Station table.')
        DublinBikeStation.objects.all().delete()
