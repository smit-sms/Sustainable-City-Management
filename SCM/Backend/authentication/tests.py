from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, Whitelist

class TestWhitelist(APITestCase):
    def setUp(self):
        self.url = reverse('whitelist')
        self.email = 'testuser@tcd.ie'

    def test_new_whitelist(self):
        data = {'email': self.email}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, "New email added to Whitelist")
    
    def test_duplicate_whitelist(self):
        Whitelist.objects.create(email=self.email)
        data = {'email': self.email}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_208_ALREADY_REPORTED)
        self.assertEqual(response.data, "Already existing email")

class TestAuth(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.email = 'testuser@tcd.ie'
        self.password = 'testpassword'
        self.user = User.objects.create_user(email=self.email, password=self.password)
        Whitelist.objects.create(email='whitelist-test@tcd.ie')

    def test_register(self):
        data = {'email': 'whitelist-test@tcd.ie', 'password': 'newuserpassword', 'name': 'New User'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_login(self):
        data = {'email': self.email, 'password': self.password}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_logout(self):
        data = {'email': self.email, 'password': self.password}
        response = self.client.post(reverse('token_obtain_pair'), data)
        token = response.json()['refresh']
        data = {'refresh_token': str(token)}
        response = self.client.post(self.logout_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Successfully Logged out!"})

class TestTokenEndpoints(APITestCase):
    def setUp(self):
        Whitelist(email='testuser@tcd.ie').save()
        User.objects.create_user(email='testuser@tcd.ie', password='testpassword')

    def test_token_obtain_pair(self):
        url = reverse('token_obtain_pair')
        data = {'email': 'testuser@tcd.ie', 'password': 'testpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_refresh(self):
        data = {'email': 'testuser@tcd.ie', 'password': 'testpassword'}
        response = self.client.post(reverse('token_obtain_pair'), data)
        refresh_token = response.json()['refresh']

        url = reverse('token_refresh')
        data = {'refresh': refresh_token}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
