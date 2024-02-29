import pytz
import json
from unittest.mock import patch
from django.urls import reverse
from datetime import datetime, timedelta
from django.test import TestCase, Client
from ..models import Sensor, Air, Noise

class AirQualityTests(TestCase):
    
    # Prepares the environment before each test method runs. It sets up a test client and creates test data in the database.
    def setUp(self):
        self.client = Client()
        self.air_pm2_5_url = reverse('air_pm2_5')  
        # Setup initial data in the database
        self.sensor = Sensor.objects.create(serial_number='DCC-AQ2',latitude=53.349805, longitude=-6.260310)
        Air.objects.create(pm2_5=10, sensor_id=self.sensor.id, datetime=datetime.now().replace(tzinfo=pytz.timezone('GMT')))
        now = datetime.now()
        dayago = now - timedelta(days=1)
        self.time_end = now.strftime("%Y-%m-%d %H:%M:%S")
        self.time_start = dayago.strftime("%Y-%m-%d %H:%M:%S")

    #Tests the GET request for a valid sensor serial number.
    def test_get_air_pm2_5_valid_sensor(self):
        response = self.client.get(self.air_pm2_5_url, {
            'sensor_serial_number': 'DCC-AQ2',
            'time_start': self.time_start,
            'time_end': self.time_end
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('data', data)

    #Tests the GET request for an invalid sensor serial number.
    def test_get_air_pm2_5_invalid_sensor(self):
        response = self.client.get(self.air_pm2_5_url, {
            'sensor_serial_number': 'INVALID-SENSOR',
            'time_start': self.time_start,
            'time_end': self.time_end
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(True, 'Failure. Invalid sensor' in data['message'])

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
            self.assertIn('message', data)
            self.assertEqual(True, 'Success' in data['message'])

    #Tests the POST request for an invalid sensor serial number.
    def test_post_air_pm2_5_invalid_sensor(self):
        response = self.client.post(
            self.air_pm2_5_url,
            json.dumps({'sensor_serial_number': 'INVALID-SENSOR'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(True, 'Failure. Invalid sensor' in data['message'])

class NoisePollutionTests(TestCase):
    
    #Prepares the environment before each test method runs. It sets up a test client and creates test data in the database.
    def setUp(self):
        self.client = Client()
        self.noise_laeq_url = reverse('noise_laeq')  
        # Setup initial data in the database
        self.sensor = Sensor.objects.create(serial_number='10.1.1.1', latitude=53.369864, longitude=-6.258966)
        Noise.objects.create(laeq=41.09, datetime=datetime.now().replace(tzinfo=pytz.timezone('GMT')), sensor_id=self.sensor.id)
        now = datetime.now()
        dayago = now - timedelta(days=1)
        self.time_end = now.strftime("%Y-%m-%d %H:%M:%S")
        self.time_start = dayago.strftime("%Y-%m-%d %H:%M:%S")

    #Tests the GET request for a valid sensor serial number.
    def test_get_noise_laeq_valid_sensor(self):
        response = self.client.get(self.noise_laeq_url, {
            'sensor_serial_number': '10.1.1.1',
            'time_start': self.time_start,
            'time_end': self.time_end
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('data', data)

    #Tests the GET request for an invalid sensor serial number.
    def test_get_noise_laeq_invalid_sensor(self):
        response = self.client.get(self.noise_laeq_url, {
            'sensor_serial_number': 'INVALID-SENSOR',
            'time_start': self.time_start,
            'time_end': self.time_end
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(True, 'Failure. Invalid sensor' in data['message'])

    # Tests the POST request for a valid sensor serial number, mocking the requests.post call to return a predetermined JSON response.
    def test_post_noise_laeq_valid_sensor(self):
        with patch('requests.post') as mocked_post:
            mocked_post.return_value.json.return_value = [
                {'datetime': '2024-01-26 12:00:00', 'laeq': 42.5}
            ]
            mocked_post.return_value.text = json.dumps([
                {'datetime': '2024-01-26 12:00:00', 'laeq': 42.5}
            ])

            response = self.client.post(
                self.noise_laeq_url,
                json.dumps({'sensor_serial_number': '10.1.1.1'}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(True, 'Success' in data['message'])

    #Tests the POST request for an invalid sensor serial number.
    def test_post_noise_laeq_invalid_sensor(self):
        response = self.client.post(
            self.noise_laeq_url,
            json.dumps({'sensor_serial_number': 'INVALID-SENSOR'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(True, 'Failure. Invalid sensor' in data['message'])