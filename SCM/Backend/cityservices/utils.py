import os
import openrouteservice


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
