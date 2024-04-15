from rest_framework.test import APITestCase
from django.urls import reverse
from ..models import SA_energy_consumption
from authentication.models import User, Whitelist
from rest_framework import status

class SA_energy(APITestCase):
    # Set up your test data and environment
    def setUp(self):
        Whitelist.objects.create(email='testuser@tcd.ie')
        self.user = User.objects.create_user(email='testuser@tcd.ie', password='testpassword')
        # Create test data for SA_energy_consumption
        SA_energy_consumption.objects.create(SA_code=268139005, Energy_use=3146948, Energy_cost=255726, Total_Floor_Area=12661, Small_Area_Name="CLONTARF")
        SA_energy_consumption.objects.create(SA_code=268109016, Energy_use=1052962, Energy_cost=118833, Total_Floor_Area=5608, Small_Area_Name="NORTH INNER CITY")

    def test_energy_no_login(self):
        '''
        Test for checking if login works properly on SA Energy API.
        '''
        response = self.client.get(reverse('SA_energy'), {'small_area_code': 0})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Test with a valid small area code        
    def test_get_valid_small_area_code(self):
        '''
        Tests for getting valid small area code.
        '''
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('SA_energy'), {'small_area_code': '268139005'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(True, 'Success. Data fetched from the DB for the small_area ' in data['message'])

    # Test with an invalid small area code
    def test_get_invalid_small_area_code(self):
        '''
        Tests for getting invalid small area code.
        '''
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('SA_energy'), {'small_area_code': 0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'message': 'Failure. Invalid small_area 0.', 'data': []}
        )
