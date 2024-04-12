from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from authentication.models import User

class AuthenticateTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        test_user = User(email='testuser@tcd.ie', password='testpassword')
        test_user.save()

    def test_successful_login(self):
        url = reverse('authentication_login')
        data = {'email': 'testuser@tcd.ie', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_credentials(self):
        url = reverse('authentication_login')
        data = {'email': 'invalid@example.com', 'password': 'invalidpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
