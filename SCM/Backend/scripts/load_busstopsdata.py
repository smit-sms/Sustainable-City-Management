import pandas as pd
from typing import Tuple
from django.shortcuts import get_list_or_404
from django.http import Http404
import openrouteservice
import geojson
from cityservices.models import BusRoute, BusStop


def get_openroute_geojson(client: openrouteservice.Client, coords: Tuple[Tuple]):
    '''
    Function to return a route between the given co-ordinates for a selected profile and 
    its settings as GeoJSON
    coords = ((-6.262200464, 53.39114056), (-6.259719573, 53.39187739), (-6.256536433, 53.39139952))
    '''
    route = client.directions(coords, profile='driving-car', format='geojson')
    return route


def initial_load_bus_data():
    """
    Function to load the initial bus data from the txt files
    """
    try:
        shapes_df = pd.read_csv('cityservices/data/shapes.txt')
        stop_times_df = pd.read_csv('cityservices/data/stop_times.txt')
        stops_df = pd.read_csv('cityservices/data/stops.txt')
        trips_df = pd.read_csv('cityservices/data/trips.txt')

        buses = BusRoute.objects.all()
        for bus in buses:
            route_id = bus.route_id
            direction_of_interest = 0
            route_trips = trips_df[(trips_df['route_id'] == route_id) & (trips_df['direction_id'] == direction_of_interest)]

            try:
                shape_id = route_trips['shape_id'].iloc[0]
            except Exception as e:
                direction_of_interest = 1
                route_trips = trips_df[(trips_df['route_id'] == route_id) & (trips_df['direction_id'] == direction_of_interest)]
                shape_id = route_trips['shape_id'].iloc[0]

            route_shape = shapes_df[shapes_df['shape_id'] == shape_id]
            route_stop_times = stop_times_df[stop_times_df['trip_id'].isin(route_trips['trip_id'])]
            route_stops = stops_df.merge(route_stop_times[['stop_id']], on='stop_id').drop_duplicates(subset=['stop_id'])

            geojson_route = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "route_id": route_id,
                            "direction_id": direction_of_interest,
                            "type": "route"
                        },
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[row['shape_pt_lon'], row['shape_pt_lat']] for idx, row in route_shape.iterrows()]
                        }
                    }
                ] +
                [
                    {
                        "type": "Feature",
                        "properties": {
                            "Stop Name": row['stop_name'],
                            "Location": f"{row['stop_lon']}, {row['stop_lat']}"
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [row['stop_lon'], row['stop_lat']]
                        }
                    } for idx, row in route_stops.iterrows()
                ]
            }

            bus.geojson = geojson_route
            bus.save()
        print('Successfully loaded the DB with the geojsons for all Buses.')

    except Exception as e:
        print(f'Some unexpected exception occured: {e}.')


def update_geojsons():
    """
    Function to update the geojson data in the DB
    """
    try:
        with open('cityservices/data/DublinBusMain.geojson', 'r', encoding="utf8") as f:
            geojson_val = geojson.load(f)

        buses = BusRoute.objects.all()
        for bus in buses:
            for updated_geojson in geojson_val['features']:
                if bus.bus_name == updated_geojson['properties']['route_short_name']:
                    for feature in bus.geojson['features']:
                        if feature['geometry']['type'] == 'LineString':
                            feature['geometry'] = updated_geojson['geometry']
            bus.save()

        print('Successfully updated the geojson in DB.')
    except Exception as e:
        print(f'Some unexpected exception occured: {e}.')


def run():
    print("Loading the initial data.")
    initial_load_bus_data()
    print("\nUpdating the geojson fieds in the db.....")
    update_geojsons()
