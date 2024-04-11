import csv
from cityservices.models import DublinBikeStation

def run():
    try:
        stations = open('cityservices/data/dublin-bike-stations.csv', encoding='utf8')
        stations = csv.reader(stations)

        # skip the 1st row
        next(stations)
        # Flush the DB tables
        DublinBikeStation.objects.all().delete()

        for row in stations:
            DublinBikeObj = DublinBikeStation(
                station_id = row[0],
                name = row[1],
                bike_stands = row[4],
                latitude = row[2],
                longitude = row[3]
            )
            DublinBikeObj.save()

        print('Successfully loaded the data for Dublin Bike Stations.')

    except Exception as e:
        print(e)
        print(f'Some unexpected exception occured: {e}. Dropping all data in Dublin Bike Station table.')
        DublinBikeStation.objects.all().delete()
