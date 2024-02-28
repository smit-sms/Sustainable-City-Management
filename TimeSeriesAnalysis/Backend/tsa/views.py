import json
import numpy as np
import pandas as pd
from scipy.stats import norm
from django.views import View
from django.http import JsonResponse
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

def validate_data_form_dict(data):
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

def validate_data_form_list(data):
    """
    Validates if data is in correct format and return True when it is so. 
    @param data: Input data.
    @return: True if data is in expected form. Throws exception otherwise.
    """
    if type(data) != type([]): 
        raise Exception('Unrecognized form of data.')
    if len(data) <= 0: 
        raise Exception('No data received.')
    if not 'float' in str(type(data[0])): 
        raise Exception('Data must be floats.')
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
    validate_data_form_dict(data)
    data["time"] = pd.to_datetime(data["time"])
    df = pd.DataFrame(data)
    df = df.groupby('time').mean()
    df.reset_index(inplace=True)
    df.set_index("time", inplace=True, drop=False)
    df.index.name = None
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
    decomposition = seasonal_decompose(data, model=model_type, period=period, extrapolate_trend='freq')
    
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

def adf_stationarity_check(data):
    """
    Performs Augmented Dickey Fuller (ADF) test to check for stationarity of data.
    @param data: Data series that is to be tested.
    @return dict: {
        "is_stationary": True if data is stationary and false otherwise.
        "adf": ADF test statistic.
        "p": Hypothesis test p value.
        "num_lags": No. of lags used.
        "num_obs": No. of observations used for ADF regression and critical value computation.
    }
    """
    adf_res = adfuller(data)
    adf = adf_res[0]
    p = adf_res[1]
    num_lags = adf_res[2]
    num_obs = adf_res[3]
    is_stationary = p < 0.05
    return { 
        "is_stationary": int(is_stationary),
        "adf": adf,
        "p": p,
        "num_lags": num_lags,
        "num_obs": num_obs
    }

def compute_first_difference(df):
    """
    Computes first order difference of given data to possibly make it
    stationary.
    @param series: Pandas series that needs to be differenced.
    @return diff: Differenced data.
    """
    series = df.data
    dist = series[(series.index)[0:len(series)-1]].to_numpy()
    diff = series[(series.index)[1:len(series)]].to_numpy() - dist
    return diff.tolist()

def acf_pacf(data, lags):
    """
    Computes autocorrelation and partial autocorrelation 
    between lags for given no. of lags.
    @param data: Data to compute autocorrelation for.
    @param lags: No of lags to consider.
    @return dict: {
        "lag": List of lags from 1 to given max lag.
        "autocorrelation": Autocorrelation computed for each lag.
        "partial_autocorrelation": Partial autocorrelation computed for each lag.
        "confidence_interval": Confidence intervals associated with each lag.
    }
    """
    if type(lags) != int or lags >= len(data):
        raise Exception("Lags must be an integer < no. of timesteps in given data.")
    res_acf = acf(data, nlags=lags)
    res_pacf = pacf(data, nlags=lags)
    num_obs = len(data)

    # Compute the quantile function = inverse cumulative distribution function
    # of the standard normal distribution at 95% confidence level to get z value.
    z_critical = norm.ppf(1 - 0.05 / (2 * num_obs))  # 95% confidence level

    # Calculate confidence intervals for each lag
    # using the formula: Confidence Intervals = Z Score/sqrt(degrees of freedom)
    # wherein the z score is set as the value associated with 95% confidence level.
    conf_intervals = z_critical / np.sqrt(num_obs - np.arange(1, lags + 1))

    return {
        "lag": list(range(1, lags + 1)),
        "partial_autocorrelation": list(res_pacf[1:lags + 1]),
        "autocorrelation": list(res_acf[1:lags + 1]),
        "confidence_interval": list(conf_intervals)
    }

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class Decomposition(View):
    response_message = ''
    response_status = 200
    response_data = {'trend':[], 'seasonal':[], 'residual':[], 'time':[]}
        
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
        try:
            request_json = json.loads(request.body.decode('utf-8'))
            data = request_json['data']
            data["data"] = np.array(data["data"]).astype('float')
            freq = request_json['freq']
            period = request_json['period']
            model_type = request_json['model_type']
            df = make_dataframe(data, freq)
            self.response_data = decompose_time_series(data=df.data, period=period, model_type=model_type)
            self.response_data['time'] = df.time.apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S')).to_list()
            self.response_message = f'Success. Extracted trend, seasonal and residual components.'
        except Exception as e:
            self.response_message = f"Failure. {e}"
        finally:
            return JsonResponse(
                {'message': self.response_message, 'data': self.response_data}, 
                status=self.response_status, safe=True
            )
    
# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class AdfStationarityCheck(View):
    response_message = ''
    response_status = 200
    response_data = {
        "is_stationary": -1,
        "adf": -1,
        "p": -1,
        "num_lags": -1,
        "num_obs": -1
    }
        
    def post(self, request):
        """
        Post request that shall decompose given time series data
        and return it's trend, seasonal and residual components.
        @param data: Data in the form {"time":[<str>...], "data":[<float>...]}
        @param freq: Frequency at which time series values were collected.
        @return dict: A dictionary containing the decomposed components (trend, seasonal, residual).
        """
        try:
            request_json = json.loads(request.body.decode('utf-8'))
            data = request_json['data'] # [<float>, ...]
            data = list(np.array(data).astype('float'))
            validate_data_form_list(data)
            self.response_data = adf_stationarity_check(data)
            self.response_message = f'Success. Augmented Dickey Fuller test complete.'
        except Exception as e:
            self.response_message = f"Failure. {e}"
        finally:
            return JsonResponse(
                {'message': self.response_message, 'data': self.response_data}, 
                status=self.response_status, safe=True
            )
    
@method_decorator(csrf_exempt, name='dispatch')
class FirstDifference(View):
    response_message = ''
    response_status = 200
    response_data = {'data': [], 'time': []}
        
    def post(self, request):
        """
        Post request that shall decompose given time series data
        and return it's trend, seasonal and residual components.
        @param data: Data in the form {"time":[<str>...], "data":[<float>...]}
        @param freq: Frequency at which time series values were collected.
        @return dict: A dictionary containing the decomposed components (trend, seasonal, residual).
        """
        try:
            request_json = json.loads(request.body.decode('utf-8'))
            data = request_json['data']
            data["data"] = np.array(data["data"]).astype('float')
            freq = request_json['freq']
            df = make_dataframe(data, freq)
            self.response_data['data'] = compute_first_difference(df)
            self.response_data['time'] = df.time.iloc[1:].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S')).to_list()
            self.response_message = f'Success. First order difference computed.'
        except Exception as e:
            self.response_message = f"Failure. {e}"
        finally:
            return JsonResponse(
                {'message': self.response_message, 'data': self.response_data}, 
                status=self.response_status, safe=True
            )
    
@method_decorator(csrf_exempt, name='dispatch')
class AcfPacf(View):
    response_message = ''
    response_status = 200
    response_data = {
        "lag": [],
        "partial_autocorrelation": [],
        "autocorrelation": [],
        "confidence_interval": []
    }
        
    def post(self, request):
        """
        Post request that shall decompose given time series data
        and return it's trend, seasonal and residual components.
        @param data: Data in the form {"time":[<str>...], "data":[<float>...]}
        @param freq: Frequency at which time series values were collected.
        @return dict: A dictionary containing the decomposed components (trend, seasonal, residual).
        """
        try:
            request_json = json.loads(request.body.decode('utf-8'))
            data = request_json['data']
            data["data"] = np.array(data["data"]).astype('float')
            freq = request_json['freq']
            lags = request_json['lags']
            df = make_dataframe(data, freq)
            self.response_data = acf_pacf(df.data, lags)
            self.response_message = f'Success. ACF and PACF computed.'
        except Exception as e:
            self.response_message = f"Failure. {e}"
        finally:
            return JsonResponse(
                {'message': self.response_message, 'data': self.response_data}, 
                status=self.response_status, safe=True
            )