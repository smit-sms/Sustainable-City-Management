import logging
import os
import openrouteservice
import requests
import pandas as pd


def get_openroute_geojson(coordinates: list[list], optimize: bool = False):
    '''
    Function to return a route between the given co-ordinates for a selected profile and
    its settings as GeoJSON
    coords = [[-6.262200464, 53.39114056], [-6.259719573, 53.39187739], [-6.256536433, 53.39139952]]
    '''
    # Initializing OpenRouteService Client
    ORS_KEY = os.getenv('OPENROUTESERVICE_API_KEY')
    client = openrouteservice.Client(key=ORS_KEY)

    # Convert into tuples of tuples for openrouteservice
    coords = tuple(tuple(coordinate) for coordinate in coordinates)
    route = client.directions(coords, profile='driving-car', format='geojson', optimize_waypoints=optimize)

    return route


def get_weather_forecast():
    '''
    Function to return the weather forecast for 24hrs
    '''
    try:
        APIKEY_METEOSOURCE = os.getenv('APIKEY_METEOSOURCE')
        parameters = {'key': APIKEY_METEOSOURCE,
                    'place_id': 'dublin'}
        url = "https://www.meteosource.com/api/v1/free/point"
        data = requests.get(url, parameters).json()
        return data
    except Exception as e:
        logging.getLogger(__name__).exception(f'Some unexpected exception occured: {e}')
        raise f"Error in Weather API {e}"
