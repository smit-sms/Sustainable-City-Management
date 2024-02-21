import csv
from cityservices.models import BusRoute, BusStop

def run():
    try:
        bus_routes = open('cityservices/data/bus_routes.csv', encoding='utf8')
        bus_stops = open('cityservices/data/bus_stops.csv', encoding='utf8')
        
        bus_route_reader = csv.reader(bus_routes)
        bus_stops_reader = csv.reader(bus_stops)
        # skip the 1st row
        next(bus_route_reader)
        next(bus_stops_reader)

        # Flush the DB tables
        BusStop.objects.all().delete()
        BusRoute.objects.all().delete()

        for row in bus_route_reader:
            BusRouteObj = BusRoute(route_id=row[0], name=row[2], bus_name=row[1])
            BusRouteObj.save()
        
        for row in bus_stops_reader:
            BusStopObj = BusStop(stop_id=row[1],route_id=row[0],name=row[2],latitude=row[3],longitude=row[4],direction=row[5])
            BusStopObj.save()

        print('Successfully loaded the data for Bus Routes and Bus Stops.')

    except Exception as e:
        print(f'Some unexpected exception occured: {e}. Dropping all data in bus routes and bus stops tables.')
        BusStop.objects.all().delete()
        BusRoute.objects.all().delete()
