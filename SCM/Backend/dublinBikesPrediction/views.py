import pandas as pd
import numpy as np
import requests
from django.shortcuts import render
from django.core.cache import cache
from django.http import JsonResponse
from sklearn.externals import joblib

# import pickle
# with open("RFmodel.pkl", "rb") as f:
    # model = pickle.load(f)

# Load and Cache the model
print('Load and cache Dublin Bikes Usage predictor model')
model = joblib.load('assets/RFmodel.pkl')
cache.set('dublinBikesUsage_model', model)

APIKEY_OPENWEATHER = 'eef810c9a22776cce17d0de14d316137'
APIKEY_METEOSOURCE = 'wkz9f0gm7xust1d45patrd9uqugwm2qjrtctorxx'

def get_weather_forecast():
    parameters = {'key': APIKEY_METEOSOURCE,
                  'place_id': 'dublin'}
    url = "https://www.meteosource.com/api/v1/free/point"
    data = requests.get(url, parameters).json()
    return data

def prepare_query_for_model(weather_forecast=None):
    if(weather_forecast == None):
        weather_forecast = get_weather_forecast()
        
    res = pd.DataFrame.from_dict(pd.json_normalize(weather_forecast['hourly']['data']), orient='columns')
    res['date'] = pd.to_datetime(res['date'])
    res = res[['date', 'precipitation.total', 'temperature']]
    res.rename(columns={'precipitation.total': 'rain', 'temperature': 'temp', 'date': 'TIME'}, inplace=True)
    
    res['hour'] = res['TIME'].dt.hour
    res['minute'] = res['TIME'].dt.minute
    res['month'] = res['TIME'].dt.month
    res['day'] = res['TIME'].dt.day
    res['dayofweek'] = res['TIME'].dt.dayofweek

    res.drop('TIME', axis=1, inplace=True)

    df_stations = pd.read_csv('assets/STATION ID - BIKE STANDS.csv')
    res['dummy'] = 1
    df_stations['dummy'] = 1
    res = pd.merge(df_stations, res, on='dummy')
    res = res.drop(columns='dummy')
    res = res.reset_index(drop=True)
    
    return res

def predict(request):
    cached_model = cache.get('dublinBikesUsage_model')
    prediction = cached_model.predict(prepare_query_for_model())
    return JsonResponse({'prediction': prediction.tolist()})
