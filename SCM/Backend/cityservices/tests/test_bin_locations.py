from django.test import TestCase, Client
from rest_framework import status
import json
from django.urls import reverse
from unittest.mock import patch

class BinLocationsViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_bin_locations_success(self):
        response = self.client.get(reverse('dublin-bin-locations'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Successfully fetched the required data', response.data['message'])
        self.assertTrue('data' in response.data)

    def test_get_bin_locations_exception(self):
        # Mocking the open method to raise an exception
        with patch('builtins.open', side_effect=Exception('Test Exception')):
            response = self.client.get(reverse('dublin-bin-locations'))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('Some unexpected exception occurred', response.data['message'])
            self.assertIsNone(response.data['data'])
