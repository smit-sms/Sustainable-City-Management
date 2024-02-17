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
            "tsa_decomposition": reverse('tsa_decomposition'),
            "tsa_stationarity": reverse("tsa_stationarity"),
            "tsa_first_difference": reverse("tsa_first_difference"),
            "tsa_correlation": reverse("tsa_correlation")
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
        res = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Success. Extracted trend, seasonal and residual components.', res["message"])
        self.assertEqual(len(res["data"]["trend"]) > 0, True)
        self.assertEqual(len(res["data"]["seasonal"]) > 0, True)
        self.assertEqual(len(res["data"]["residual"]) > 0, True)

    def test_stationarity_success(self):
        response = self.client.post(
            path=self.urls["tsa_stationarity"], 
            data=json.dumps({"data": self.dummyData['data']}),
            content_type='application/json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Success. Augmented Dickey Fuller test complete.', res["message"])
        self.assertIn(res["data"]["is_stationary"], [1, 0])
        self.assertEqual(type(res["data"]["adf"]) == float, True)
        self.assertEqual(type(res["data"]["p"]) == float, True)
        self.assertEqual(type(res["data"]["num_lags"]) == int, True)
        self.assertEqual(type(res["data"]["num_obs"]) == int, True)

    def test_first_difference_success(self):
        response = self.client.post(
            path=self.urls["tsa_first_difference"], 
            data=json.dumps({
                "data": self.dummyData,
                "freq": "30min",
            }),
            content_type='application/json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Success. First order difference computed.', res["message"])
        self.assertEqual(len(res["data"]["data"]) > 0, True)
        self.assertEqual(len(res["data"]["data"]), len(res["data"]["time"]))

    def test_correlation_success(self):
        response = self.client.post(
            path=self.urls["tsa_correlation"], 
            data=json.dumps({
                "data": self.dummyData,
                "freq": "30min",
                "lags": 10
            }),
            content_type='application/json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Success. First order difference computed.', res["message"])
        self.assertEqual(
            len(res["data"]["lag"]) 
            == len(res["data"]["partial_autocorrelation"])
            == len(res["data"]["autocorrelation"])
            == len(res["data"]["confidence_interval"])
            > 0
        , True)
        self.assertEqual(type(res["data"]["lag"][0]) == int, True)
        self.assertEqual(type(res["data"]["partial_autocorrelation"][0]) == float, True)
        self.assertEqual(type(res["data"]["autocorrelation"][0]) == float, True)
        self.assertEqual(type(res["data"]["confidence_interval"][0]) == float, True)

    # Test failure.
    def test_decomposition_failure(self):
        response = self.client.post(
            path=self.urls["tsa_decomposition"], 
            data=json.dumps({
                "data": self.dummyData,
                "freq": "30min",
                "period": "20", # Wrong data format. Should be integer.
                "model_type":"additive"
            }),
            content_type='application/json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 500)
        self.assertIn('Failure.', res["message"])

    def test_stationarity_failure(self):
        response = self.client.post(
            path=self.urls["tsa_stationarity"], 
            data=json.dumps({}), # Missing parameter data.
            content_type='application/json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 500)
        self.assertIn('Failure.', res["message"])

    def test_first_difference_failure(self):
        response = self.client.post(
            path=self.urls["tsa_first_difference"], 
            data=json.dumps({
                "data": self.dummyData,
                "freq": "0min", # Invalid frequency offset
            }),
            content_type='application/json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 500)
        self.assertIn('Failure.', res["message"])

    def test_correlation_failure(self):
        response = self.client.post(
            path=self.urls["tsa_correlation"], 
            data=json.dumps({
                "data": self.dummyData,
                "freq": "30min",
                "lags": len(self.dummyData['data'])+1 # Value for lags out of accepted range.
            }),
            content_type='application/json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 500)
        self.assertIn('Failure.', res["message"])