from django.urls import reverse
from django.test import TestCase, Client
from ..models import Sensor, Air, DateTime
from unittest.mock import patch
import json
from datetime import datetime
import pytz

class AirQualityTests(TestCase):
    
    #Prepares the environment before each test method runs. It sets up a test client and creates test data in the database.
    def setUp(self):
        self.client = Client()
        self.air_pm2_5_url = reverse('air_pm2_5')  
        # Setup initial data in the database
        self.sensor = Sensor.objects.create(serial_number='DCC-AQ2',latitude=53.349805, longitude=-6.260310)
        self.datetime_obj = DateTime.objects.create(datetime=datetime.now().replace(tzinfo=pytz.timezone('GMT')))
        Air.objects.create(pm2_5=10, datetime=self.datetime_obj, sensor=self.sensor)

    #Tests the GET request for a valid sensor serial number.
    def test_get_air_pm2_5_valid_sensor(self):
        response = self.client.get(self.air_pm2_5_url, {'sensor_serial_number': 'DCC-AQ2'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('data', data)

    #Tests the GET request for an invalid sensor serial number.
    def test_get_air_pm2_5_invalid_sensor(self):
        response = self.client.get(self.air_pm2_5_url, {'sensor_serial_number': 'INVALID-SENSOR'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['data']['pm2_5'], [])

    # Tests the POST request for a valid sensor serial number, mocking the requests.post call to return a predetermined JSON response.
    def test_post_air_pm2_5_valid_sensor(self):
        with patch('requests.post') as mocked_post:
            mocked_post.return_value.json.return_value = [
                {'datetime': '2024-01-26 12:00:00', 'pm2_5': 20}
            ]
            mocked_post.return_value.text = json.dumps([
                {'datetime': '2024-01-26 12:00:00', 'pm2_5': 20}
            ])

            response = self.client.post(
                self.air_pm2_5_url,
                json.dumps({'sensor_serial_number': 'DCC-AQ2'}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('data', data)
            self.assertEqual(len(data['data']), 1)

    #Tests the POST request for an invalid sensor serial number.
    def test_post_air_pm2_5_invalid_sensor(self):
        response = self.client.post(
            self.air_pm2_5_url,
            json.dumps({'sensor_serial_number': 'INVALID-SENSOR'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('message', data)

    #Tests the POST request when an exception is raised during the requests.post call.
    def test_post_air_pm2_5_with_exception(self):
        with patch('requests.post') as mocked_post:
            mocked_post.side_effect = Exception('Failed to fetch data')
            response = self.client.post(
                self.air_pm2_5_url,
                json.dumps({'sensor_serial_number': 'DCC-AQ2'}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 404)
            data = response.json()
            self.assertIn('error', data)
