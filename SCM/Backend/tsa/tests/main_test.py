import time
import threading
import unittest
import requests

# Get some data to run tests using.
response = requests.get(
    url = "http://127.0.0.1:8000/bikes/snapshot",
    params = {
        'station_id':32, 
        'time_start':"2024-03-21 00:00:00",
        'time_end':"2024-03-27 00:00:00"
    }
)
TEST_DATA = {"time":[], "data":[]}
for d in response.json()['data']:
    time = d['last_update']
    time = time.replace('T', ' ')
    time = time.replace('Z', '')
    TEST_DATA['time'].append(time)
    TEST_DATA['data'].append(d['usage_percent'])

class TestTSA(unittest.TestCase):
    """ Class that tests the ETLPipeline. """

    def test_01_server_up(self):
        """ Check if the server is running. """
        response = requests.get("http://127.0.0.1:8001/admin")
        self.assertEqual(response.status_code, 200)

    def test_02_decomposition(self):
        """ 
        This test checks status of the endpoint that
        facilitates decomposition of data into the 
        trend, seasonal and residual components.
        """

        # Success case.
        # Upon successful data decomposition, the
        # the trend, seasonality and residual components
        # must be returned along with a "success" message.
        response = requests.post(
            url="http://127.0.0.1:8001/tsa/decompose/",
            json={
                "data": TEST_DATA,
                "freq": "10min", 
                "period": 5, 
                "model_type": "additive"
            }
        )
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Success.", response_json['message'])
        self.assertIn("trend", response_json['data'].keys())
        self.assertIn("seasonal", response_json['data'].keys())
        self.assertIn("residual", response_json['data'].keys())

        # Failure case.
        # Fails because data could not be processed.
        # Here due to an invalid format. This should
        # return an error message and code 400.
        data_wrong_format = requests.get(
            url = "http://127.0.0.1:8000/bikes/snapshot",
            params = {
                'station_id':32, 
                'time_start':"2024-03-26 00:00:00",
                'time_end':"2024-03-27 00:00:00"
            }
        ).json()['data']
        response = requests.post(
            url="http://127.0.0.1:8001/tsa/decompose/",
            json={
                "data": data_wrong_format,
                "freq": "10min", 
                "period": 5, 
                "model_type": "additive"
            }
        )
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertIn("Failure.", response_json['message'])

    def test_03_make_stationary(self):
        """ 
        This test checks status of endpoints that
        facilitate checking whether data is stationary
        using the Augmented Dickey Fuller test and
        computation of first difference multiple times
        to make the data stationary.
        """

        # Success case. (This is also the a use case
        # that the front end will try to implement.)
        # Upon successful ADF, some indicator as to
        # whether the data was stationary must be 
        # returned (0/1). Also, the ADF value and related
        # p value that says how significant the test was
        # should be returned along with no. of lags that
        # were considered. If the data is not stationary,
        # first difference = (data - lag1(data)) is to be
        # computed. The check for stationarity is then
        # repeated and this cycle thus continues until the
        # data is stationary.
        max_trials = 20 # Stop trying to make stationary after some trials.
        trial = 0 # Trial counter.
        d = TEST_DATA # Data to differentiate.
        print('Checking/Making Stationary')
        while trial < max_trials:
            # Update no. of remaining trials.
            trial += 1
            print(f'Trial {trial}')

            # Check if data is stationary.
            response = requests.post(
                url = "http://127.0.0.1:8001/tsa/stationarity/",
                json = {"data": d['data']}
            )
            response_json = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertIn("Success.", response_json['message'])
            self.assertIn("is_stationary", response_json['data'].keys())
            self.assertIn("adf", response_json['data'].keys())
            self.assertIn("p", response_json['data'].keys())
            self.assertIn("num_lags", response_json['data'].keys())
            if response_json['data']['is_stationary'] == 1:
                break # Stop if data is stationary.
            
            # Else, compute first difference to try and
            # make data stationary. The processed data 
            # should have same format as the input data.
            response = requests.post(
                url="http://127.0.0.1:8001/tsa/first_difference/",
                json={
                    "data": d,
                    "freq": "10min"
                }
            )
            response_json = response.json()
            d = response.json()['data']
            self.assertEqual(response.status_code, 200)
            self.assertIn("Success.", response_json['message'])
            self.assertIn("data", response_json['data'])
            self.assertIn("time", response_json['data'])

        # Failure case.
        # Here, the test fails because data is in
        # an invalid format.
        # Check if data is stationary.
        response = requests.post(
            url = "http://127.0.0.1:8001/tsa/stationarity/",
            json = {"data": {
                'data':[1.3, 3.4, 4.3], 
                'time':['27-03-2024 13:42:00', '27-03-2024 13:52:00', '27-03-2024 14:02:00']
            }}
        )
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertIn("Failure.", response_json['message'])

    def test_04_correlation(self):
        """ 
        This test checks status of the endpoint that
        computes autocorrelation and partial autocorrelation.
        """

        # Success case.
        # Upon successful ACF and PACF computation,
        # computed auto-correlation and partial
        # auto correlation values along with lags
        # considered and confidence interval beyond
        # above which value are significant, must be
        # returned.
        lags = 20
        response = requests.post(
            url="http://127.0.0.1:8001/tsa/correlation/",
            json={
                "data": TEST_DATA,
                "freq": "10min", 
                "lags": lags,
            }
        )
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Success.", response_json['message'])
        self.assertEqual(lags, len(response_json['data']['autocorrelation']))
        self.assertEqual(lags, len(response_json['data']['partial_autocorrelation']))
        self.assertEqual(lags, len(response_json['data']['confidence_interval']))

        # Fail case.
        # If lags provided is > len(data), then it will
        # not be possible to run the Auto Correlation 
        # Function (ACF) and the Partial Auto Correlation
        # (PACF) function. This should throw an error.
        lags = 1000
        response = requests.post(
            url="http://127.0.0.1:8001/tsa/correlation/",
            json={
                "data": TEST_DATA,
                "freq": "10min", 
                "lags": lags,
            }
        )
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertIn("must be an integer < no. of timesteps", response_json['message'])

if __name__ == "__main__":
    print('Module Tests: Time Series Analysis (TSA) Backend.')
    unittest.main()