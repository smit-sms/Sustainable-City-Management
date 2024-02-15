import time
import json
import requests
from datetime import datetime, timedelta
from django.urls import reverse
from django.test import TestCase, Client

def fetch_noise_data(sensor_serial_number):
    """
    Fetch noise data from https://data.smartdublin.ie/sonitus-api
    to act as dummy data.
    @param sensor_serial_number: Identifier of the sensor whose data
                                 is to be fetched.
    """
    datetime_now = datetime.now()
    datetime_yesterday = datetime_now - timedelta(days=1)
    datetime_end = time.mktime(datetime_now.timetuple()) # Now.
    datetime_start = time.mktime(datetime_yesterday.timetuple()) # 24 hrs ago.
    res = requests.post("https://data.smartdublin.ie/sonitus-api/api/data", json={ 
        'username': "dublincityapi",
        'password': "Xpa5vAQ9ki",
        'monitor': sensor_serial_number,
        'start': datetime_start,
        'end': datetime_end
    })
    data = {"time": [], "data": []}
    if len(res.text) > 0: # if response data is not empty then ...
        for d in res.json():
            data["time"].append(str(datetime.strptime(d['datetime'], "%Y-%m-%d %H:%M:%S")))
            data["data"].append(float(d["laeq"]))
    return data

# Create your tests here.
class TimeSeriesAnalysis(TestCase):
    def setUp(self):
        self.client = Client()
        self.urls = {
            "tsa_decomposition": reverse('tsa_decomposition')  
        }
        self.dummyData = fetch_noise_data('10.1.1.1')

    # Test success.
    def test_decomposition_success(self):
        response = self.client.post(
            path=self.urls["tsa_decomposition"], 
            data=json.dumps({
                "data": self.dummyData,
                "freq": "30min",
                "period": 8, 
                "model_type":"additive"
            }),
            content_type='application/json'
        )
        # print('RESPONSE =', response.json())
        res = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Success. Extracted trend, seasonal and residual components.', res["message"])
        self.assertEqual(len(res["data"]["trend"]) > 0, True)
        self.assertEqual(len(res["data"]["seasonal"]) > 0, True)
        self.assertEqual(len(res["data"]["residual"]) > 0, True)