from django.urls import reverse
from unittest.mock import patch
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import Sensor, Air, Noise
from authentication.models import User, Whitelist
from scripts import load_sensors, load_sensor_data
import random

class AirNoiseViewTestCase(APITestCase):
    '''
    Tests for Air Noise View.
    '''
    def setUp(self):
        Whitelist.objects.create(email='testuser@tcd.ie')
        self.user = User.objects.create_user(email='testuser@tcd.ie', password='testpassword')

    def test_get_air_noise_data(self):
        '''
        Test for checking Air Noise API.
        '''
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('air_noise'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        
    def test_get_air_noise_data_no_login(self):
        '''
        Test for checking if login works properly on Air Noise API.
        '''
        response = self.client.get(reverse('air_noise'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AirPredictionsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@tcd.ie', password='testpassword')
        load_sensors.run()
        Sensor.objects.exclude(sensor_type="air").delete()
        sensors = list(Sensor.objects.filter(sensor_type="air"))
        while len(sensors)>3:
            sensor = random.choice(sensors)
            # print(sensor.id)
            if(sensor.id!=None):
                sensor.delete()
            else:
                print(sensor.id)
            sensors.remove(sensor)
        load_sensor_data.run()

    def test_get_air_predictions(self):
        '''
        Test for checking Air Predictions API.
        '''
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('air_predictions'))
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_get_air_predictions_no_login(self):
        '''
        Test for checking if login works properly on Air Predictions API.
        '''
        response = self.client.get(reverse('air_predictions'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class NoisePredictionsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@tcd.ie', password='testpassword')
        load_sensors.run()
        Sensor.objects.exclude(sensor_type="noise").delete()
        sensors = list(Sensor.objects.filter(sensor_type="noise"))
        while len(sensors)>2:
            sensor = random.choice(sensors)
            # print(sensor.id)
            if(sensor.id!=None):
                sensor.delete()
            else:
                print(sensor.id)
            sensors.remove(sensor)
        load_sensor_data.run()

    def test_get_noise_predictions(self):
        '''
        Test for checking Noise Predictions API.
        '''
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('noise_predictions'))
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_get_noise_predictions_no_login(self):
        '''
        Test for checking if login works properly on Noise Predictions API.
        '''
        response = self.client.get(reverse('noise_predictions'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
