from rest_framework.test import APITestCase
from rest_framework import status
import json
from django.urls import reverse
from unittest.mock import patch
from authentication.models import User, Whitelist

class BinLocationsViewTestCase(APITestCase):
    def setUp(self):
        Whitelist.objects.create(email='testuser@tcd.ie')
        self.user = User.objects.create_user(email='testuser@tcd.ie', password='testpassword')

    def test_get_bin_locations_success(self):
        '''
        Tests for getting bin locations.
        '''
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('dublin-bin-locations'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Successfully fetched the required data', response.data['message'])
        self.assertTrue('data' in response.data)

    def test_get_bin_locations_no_login(self):
        '''
        Test for checking if login works properly on Dublin Bins API.
        '''
        response = self.client.get(reverse('dublin-bin-locations'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_bin_locations_exception(self):
        '''
        Tests for checking exception handling in bins API.
        '''
        self.client.force_authenticate(user=self.user)
        # Mocking the open method to raise an exception
        with patch('builtins.open', side_effect=Exception('Test Exception')):
            response = self.client.get(reverse('dublin-bin-locations'))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('Some unexpected exception occurred', response.data['message'])
            self.assertIsNone(response.data['data'])
