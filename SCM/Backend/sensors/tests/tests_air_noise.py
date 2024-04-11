from django.urls import reverse
from django.test import TestCase, Client
from rest_framework import status


class AirNoiseTests(TestCase):
    '''
    Tests for Air Noise Routes APIView
    '''
    def setUp(self):
        self.client = Client()
        self.air_noise_url = reverse('air_noise')

    def test_get_data(self):
        '''
        Test for fetching the data.
        '''
        response = self.client.get(self.air_noise_url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertIsNotNone(result['data'])
        self.assertIn('Successfully fetched the required data', response.data['message'])
