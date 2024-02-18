from django.urls import reverse
from unittest import mock
from django.test import TestCase, Client
from ..models import BusRoute
from rest_framework import status


class BusRouteTests(TestCase):
    '''
    Tests for Bus Routes APIView
    '''
    def setUp(self):
        self.client = Client()
        self.bus_routes_url = reverse('bus-routes')
        # Setup initial data in the database
        bus_route = {
            "route_id": '1',
            "name": 'test_route',
            "bus_name": 'TestBus1',
            "geojson": {
                "features":[{
                        "type": "Feature",
                        "properties": {
                            "Stop Name": "Test Stop",
                            "Location": "-104.99404, 39.75621"
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-104.99404, 39.75621]
                        }
                }]
            }
        }
        self.bus_routes = BusRoute.objects.create(**bus_route)
        
        self.post_data = {
            "bus_name": "TestBus1",
            "coordinates": [
                [-6.262200464, 53.39114056, "Stop 1"],
                [-6.259719573, 53.39187739, "Stop 2"],
                [-6.256536433, 53.39139952, "Stop 3"],
                [-6.251344506, 53.39114381, "Stop 4"],
            ]
        }

    def test_get_all_bus_routes(self):
        '''
        Test for fetching all bus routes.
        '''
        response = self.client.get(self.bus_routes_url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertIsNotNone(result['data'])

    def test_get_bus_route(self):
        '''
        Test for fetching a bus route.
        '''
        response = self.client.get(self.bus_routes_url, {'bus_name':'TestBus1'})
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertIsNotNone(result['data'])

    def test_get_invalid_bus_route(self):
        '''
        Test for fetching an invalid bus route.
        '''
        response = self.client.get(self.bus_routes_url, {'bus_name':'NOT_FOUND'})
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        result = response.json()
        self.assertIsNone(result['data'])

    def test_custom_bus_route_post(self):
        '''
        Test for getting bus route based on co-ordinates passed
        '''
        with mock.patch('cityservices.views.get_openroute_geojson'):
            response = self.client.post(self.bus_routes_url, self.post_data, format='json',
                                        content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('Successfully fetched the required data', response.data['message'])

    def test_custom_bus_route_post_key_error(self):
        '''
        Test for getting bus route when no co-ordinates passed
        '''
        payload = {}

        response = self.client.post(self.bus_routes_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Please pass required parameter', response.data['message'])

    def test_post_unexpected_exception(self):
        '''
        Test for checking the unexpected exception
        '''
        with mock.patch('cityservices.views.get_openroute_geojson', side_effect=Exception("Test exception")):
            response = self.client.post(self.bus_routes_url, self.post_data, format='json',
                                        content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('Some unexpected exception occured', response.data['message'])
