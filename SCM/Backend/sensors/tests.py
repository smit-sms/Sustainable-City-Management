from unittest.mock import patch, MagicMock
from datetime import datetime
from django.urls import reverse
from unittest.mock import patch
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import Sensor, Air, Noise
from authentication.models import User, Whitelist
import pytz

AIR_SENSORS = [
    ["DCC-AQ1", 53.3442389, -6.271525, "air"],
    ["DM30-00118", 53.390398, -6.26506, "air"],
    ["TNT1138", 53.369894, -6.259124, "air"],
    ["TNO4390", 53.357689, -6.287134, "air"],
    ["0110-000141-000000", 53.337909, -6.281161, "air"],
]
NOISE_SENSORS = [
    ["01749", 53.36866, -6.149316, "noise"],
    ["10.1.1.11", 53.346694, -6.272244, "noise"],
]
parsed_datetime = datetime.strptime("2024-04-18 12:40:00", '%Y-%m-%d %H:%M:%S')
timezone = pytz.timezone('GMT')
timezone_aware_datetime = timezone.localize(parsed_datetime)

class AirNoiseViewTestCase(APITestCase):
    '''
    Tests for Air Noise View.
    '''

    def setUp(self):
        Whitelist.objects.create(email='testuser@tcd.ie')
        self.user = User.objects.create_user(
            email='testuser@tcd.ie', password='testpassword')

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
        self.user = User.objects.create_user(
            email='testuser@tcd.ie', password='testpassword')
        for air_sensor in AIR_SENSORS:
            sensor = Sensor(serial_number=air_sensor[0], latitude=float(
                air_sensor[1]), longitude=float(air_sensor[2]), sensor_type=air_sensor[3])
            sensor.save()
            Air.objects.create(pm2_5=2.5, datetime=timezone_aware_datetime, sensor=sensor)

    # def test_get_air_predictions(self):
    #     '''
    #     Test for checking Air Predictions API.
    #     '''
    #     self.client.force_authenticate(user=self.user)
    #     response = self.client.get(reverse('air_predictions'))
    #     print(response.json())
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn('data', response.data)

    def test_get_air_predictions_no_login(self):
        '''
        Test for checking if login works properly on Air Predictions API.
        '''
        response = self.client.get(reverse('air_predictions'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('sensors.views.AirPredictions')
    @patch('pickle.load')
    def test_get_air_predictions(self, mock_pickle_load, mock_prepare_query_for_model):
        '''
        Tests for predictions in Air Predictions API.
        '''
        self.client.force_authenticate(user=self.user)
        # Setup mock model with a predictable return value
        mock_model = MagicMock()
        mock_model.predict.return_value = [2.8, 2.8, 2.8]  # Example prediction
        mock_pickle_load.return_value = mock_model

        # Call the predict view
        response = self.client.get(reverse('air_predictions'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

class NoisePredictionsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@tcd.ie', password='testpassword')
        for noise_sensor in NOISE_SENSORS:
            sensor = Sensor(serial_number=noise_sensor[0], latitude=float(
                noise_sensor[1]), longitude=float(noise_sensor[2]), sensor_type=noise_sensor[3])
            sensor.save()
            Noise.objects.create(laeq=2.5, datetime=timezone_aware_datetime, sensor=sensor)

    # def test_get_noise_predictions(self):
    #     '''
    #     Test for checking Noise Predictions API.
    #     '''
    #     self.client.force_authenticate(user=self.user)
    #     response = self.client.get(reverse('noise_predictions'))
    #     print(response.json())
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn('data', response.data)

    @patch('sensors.views.NoisePredictions')
    @patch('pickle.load')
    def test_get_Noise_predictions(self, mock_pickle_load, mock_prepare_query_for_model):
        '''
        Test for checking Noise Predictions API.
        '''
        self.client.force_authenticate(user=self.user)
        # Setup mock model with a predictable return value
        mock_model = MagicMock()
        mock_model.predict.return_value = [2.8, 2.8]  # Example prediction
        mock_pickle_load.return_value = mock_model

        # Call the predict view
        response = self.client.get(reverse('noise_predictions'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_get_noise_predictions_no_login(self):
        '''
        Test for checking if login works properly on Noise Predictions API.
        '''
        response = self.client.get(reverse('noise_predictions'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
