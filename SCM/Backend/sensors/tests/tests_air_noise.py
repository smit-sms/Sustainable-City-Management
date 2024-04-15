from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from authentication.models import User, Whitelist

class AirNoiseTests(APITestCase):
    '''
    Tests for Air Noise Routes APIView
    '''
    def setUp(self):
        self.air_noise_url = reverse('air_noise')
        Whitelist.objects.create(email='test-email@tcd.ie')
        self.user = User.objects.create_user(email='testuser@tcd.ie', password='testpassword')

    def test_get_data(self):
        '''
        Test for fetching the data.
        '''
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.air_noise_url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertIsNotNone(result['data'])
        self.assertIn('Successfully fetched the required data', response.data['message'])
