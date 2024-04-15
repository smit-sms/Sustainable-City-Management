from django.test import TestCase, Client
from django.urls import reverse
from ..models import SA_energy_consumption

class SA_energy(TestCase):
    # Set up your test data and environment
    def setUp(self):
        self.client = Client()
        # Create test data for SA_energy_consumption
        SA_energy_consumption.objects.create(SA_code=268139005, Energy_use=3146948, Energy_cost=255726, Total_Floor_Area=12661, Small_Area_Name="CLONTARF")
        SA_energy_consumption.objects.create(SA_code=268109016, Energy_use=1052962, Energy_cost=118833, Total_Floor_Area=5608, Small_Area_Name="NORTH INNER CITY")
			
    # Test with a valid small area code        
    def test_get_valid_small_area_code(self):
        response = self.client.get(reverse('SA_energy'), {'small_area_code': '268139005'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(True, 'Success. Data fetched from the DB for the small_area ' in data['message'])
       

    # Test with an invalid small area code
    def test_get_invalid_small_area_code(self):
        response = self.client.get(reverse('SA_energy'), {'small_area_code': 0})
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'message': 'Failure. Invalid small_area 0.', 'data': []}
        )