import pandas as pd
import numpy as np
import requests
from django.shortcuts import render
from django.core.cache import cache
from django.http import JsonResponse
import pickle
# Load the model
class DublinBikesModel:
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super(DublinBikesModel, cls).__new__(cls)
            # Initialize your variable here to ensure it's only done once.
            print('Load Dublin Bikes Usage predictor model')
            cls.model = pickle.load(open("dublinBikesPrediction/assets/Resources/RFmodel.pkl", 'rb'))
            cls.df_stations = pd.read_csv('dublinBikesPrediction/assets/STATION ID - BIKE STANDS.csv')
            print('Model load complete')
        return cls._instance


    # def set_some_variable(self, value):
    #     Singleton.some_variable = value

    def get_model(self):
        return DublinBikesModel.model

dublinBikesModel = DublinBikesModel()

# cache.set('dublinBikesUsage_model', model)

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

    df_stations = pd.read_csv('dublinBikesPrediction/assets/STATION ID - BIKE STANDS.csv')
    res['dummy'] = 1
    df_stations['dummy'] = 1
    res = pd.merge(df_stations, res, on='dummy')
    res = res.drop(columns='dummy')
    res = res.reset_index(drop=True)
    return res

def predict(request):
    data = prepare_query_for_model()
    prediction = dublinBikesModel.get_model().predict(data)
    data['prediction'] = prediction
    return JsonResponse({'prediction': data.to_json()})
