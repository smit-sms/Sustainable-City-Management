from django.test import TestCase
# from django.contrib.auth.models import User
from authentication.models import Whitelist, User
from rest_framework.test import APIClient
from django.urls import reverse

class SignupTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        test_user = User(email='existing.user@tcd.ie',
                         password='testpassword', username='testusername')
        Whitelist(email='existing.user@tcd.ie').save()
        Whitelist(email='whitelisted@tcd.ie').save()
        test_user.save()

    def test_signup_existing_user(self):
        response = self.client.post(reverse('authentication_signup'), {
                                    'email': 'existing.user@tcd.ie', 'password': 'testpassword', 'username': 'testusername'})
        self.assertEqual(response.status_code, 400)

    def test_signup_with_incomplete_parameters(self):
        response = self.client.post(reverse('authentication_signup'), {
                                    'email': 'new@tcd.ie', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse('authentication_signup'), {
                                    'email': 'new@tcd.ie', 'username': 'testusername'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse('authentication_signup'), {
                                    'password': 'testpassword', 'username': 'testusername'})
        self.assertEqual(response.status_code, 400)

    def test_signup_new_user_without_whitelist(self):
        response = self.client.post(reverse('authentication_signup'), {
                                    'email': 'new@tcd.ie', 'password': 'testpassword', 'username': 'testoozer'})
        self.assertEqual(response.status_code, 401)

    def test_signup_new_user(self):
        response = self.client.post(reverse('authentication_signup'), {
                                    'email': 'whitelisted@tcd.ie', 'password': 'testpassword', 'username': 'testoozer'})
        self.assertEqual(response.status_code, 201)
