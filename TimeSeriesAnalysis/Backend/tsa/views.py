import json
import numpy as np
import pandas as pd
from scipy.stats import norm
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token

def validate_data_form(data):
    """
    Validates if data is in correct format and return True when it is so. 
    @param data: Input data.
    @return: True if data is in expected form. Throws exception otherwise.
    """
    if type(data) != type({}): 
        raise Exception('Unrecognized form of data.')
    if not 'data' in data.keys(): 
        raise Exception('Unrecognized form of data.')
    if not 'time' in data.keys(): 
        raise Exception('Unrecognized form of data.')
    if len(data['data']) != len(data['time']): 
        raise Exception('Data must have same length data and time values.')
    if len(data['data']) == 0: 
        raise Exception('No data received.')
    if not 'float' in str(type(data['data'][0])): 
        raise Exception('Data must be floats.')
    try: 
        pd.to_datetime(data['time'])
    except Exception as e: 
        raise Exception(f'Time could not be converted into pandas datetime format. {e}')
    return True

def add_freq(idx, freq=None):
    """
    Adds a frequency attribute to idx, through inference or directly.
    @param idx: Index to add frequency to.
    @param freq: Frequency to add.
    @return idx: Copy of given idx with frequency offset information added.
    """
    idx = idx.copy()
    if freq is None:
        if idx.freq is None: freq = pd.infer_freq(idx) # If freq is none, infer it.
        else: return idx
    idx.freq = pd.tseries.frequencies.to_offset(freq) # Set to given frequency offset.
    if idx.freq is None: # If no freq is given and given idx has no freq, throw error.
        raise AttributeError('no discernible frequency found to `idx`.  Specify'
                             ' a frequency string with `freq`.')
    return idx

def make_dataframe(data, freq):
    """ 
    Converts given data into a data frame with the time column
    set as the index with a given frequency.
    A list of valid pandas frequency offsets is available at: 
    https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases.
    Missing values will be filled in using first forward and then backward fill.
    """
    if type(freq) != str:
        raise Exception("Frequency must be a valid pandas frequency offset.")
    validate_data_form(data)
    data["time"] = pd.to_datetime(data["time"])
    df = pd.DataFrame(data)
    df.set_index("time", inplace=True)
    df = df.asfreq(freq)
    df = df.ffill().bfill()
    return df

def decompose_time_series(data, period, model_type='additive'):
    """
    Decomposes a time series into trend, seasonality, and residual components.
    @param data: Data series that is to be decomposed.
    @param period: No. of samples in a season. After how many observation would you like
                   to assume that there are repetitions?
    @param model_type: Type of decomposition (additive or multiplicative).
    @return dict: A dictionary containing the decomposed components (trend, seasonal, residual).
    """
    if type(period) != int:
        raise Exception("Given period must be an integer that indicates the no. of observations after which you would you like to assume that seasonality repeats.")
    if not model_type in ["additive", "multiplicative"]:
        raise Exception("Model type must be one of either 'additive' or 'multiplicative'.")
    # Perform seasonal decomposition.
    if model_type == 'multiplicative' and data.eq(0).any():
        # If there are 0s in the data, then it must be offset by 1
        # in order to perform multiplicative decomposition.
        data = data + 1
    decomposition = seasonal_decompose(data, model=model_type, period=period)
    
    # Extract decomposed components.
    trend = decomposition.trend
    seasonal = decomposition.seasonal
    residual = decomposition.resid
    
    # Convert components to lists for easier manipulation.
    trend_list = trend.values.flatten().tolist()
    seasonal_list = seasonal.values.flatten().tolist()
    residual_list = residual.values.flatten().tolist()
    
    # Return decomposed components as a dictionary.
    return {
        "trend": trend_list,
        "seasonal": seasonal_list,
        "residual": residual_list
    }

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class Decomposition(View):
    response_message = ''
    response_status = 200
    response_data = []
        
    def post(self, request):
        """
        Post request that shall decompose given time series data
        and return it's trend, seasonal and residual components.
        @param data: Data in the form {"time":[<str>...], "data":[<float>...]}
        @param freq: Frequency at which time series values were collected.
        @param period: No. of samples in a season. After how many observation would you like
                       to assume that there are repetitions?
        @param model_type: Type of decomposition to perform ("additive", "multiplicative").
        @return dict: A dictionary containing the decomposed components (trend, seasonal, residual).
        """
        request_json = json.loads(request.body.decode('utf-8'))
        data = request_json['data']
        freq = request_json['freq']
        period = request_json['period']
        model_type = request_json['model_type']

        try:
            df = make_dataframe(data, freq)
            print(df)
            self.response_data = decompose_time_series(data=df.data, period=period, model_type=model_type)
            self.response_status = 200
            self.response_message = f'Success. Extracted trend, seasonal and residual components.'
        except Exception as e:
            self.response_message = f"Failure. {e}"
            self.response_data = []
            self.response_status = 500
        return JsonResponse(
            {'message': self.response_message, 'data': self.response_data}, 
            status=self.response_status, safe=True
        )