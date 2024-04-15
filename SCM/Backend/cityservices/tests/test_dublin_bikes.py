import pandas as pd
from django.urls import reverse
from unittest.mock import patch, MagicMock
from rest_framework.test import APITestCase
from authentication.models import User, Whitelist
from rest_framework import status

class PredictViewTest(APITestCase):
    def setUp(self):
        Whitelist.objects.create(email='testuser@tcd.ie')
        self.user = User.objects.create_user(email='testuser@tcd.ie', password='testpassword')

    def test_predict_view_no_login(self):
        '''
        Test for checking if login works properly on Dublin Bikes API.
        '''
        response = self.client.get(reverse('dublin-bikes'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('cityservices.views.DublinBikesView')
    @patch('pickle.load')
    def test_predict(self, mock_pickle_load, mock_prepare_query_for_model):
        '''
        Tests for predictions in Dublin Bikes.
        '''
        self.client.force_authenticate(user=self.user)
        # Setup mock model with a predictable return value
        mock_model = MagicMock()
        mock_model.predict.return_value = [42]  # Example prediction
        mock_pickle_load.return_value = mock_model

        # Mock the prepare_query_for_model to return a predictable DataFrame
        mock_prepare_query_for_model.return_value = pd.DataFrame({
            # Fill in with the expected structure
        })

        # Call the predict view
        response = self.client.get(reverse('dublin-bikes'))

        # Asserts
        self.assertEqual(response.status_code, 200)
