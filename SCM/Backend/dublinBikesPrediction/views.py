import json
import pandas as pd
import numpy as np
import requests
from django.shortcuts import render
from django.core.cache import cache
from django.http import JsonResponse
import pickle
# from rest_framework.response import Response
# from rest_framework.decorators import api_view

# Load the model


class DublinBikesModel:
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super(DublinBikesModel, cls).__new__(cls)
            # Initialize your variable here to ensure it's only done once.
            print('Load Dublin Bikes Usage predictor model')
            cls.model = pickle.load(
                open("dublinBikesPrediction/assets/RFmodel_lr.pkl", 'rb'))
            cls.df_stations = pd.read_csv(
                'dublinBikesPrediction/assets/STATION ID - BIKE STANDS.csv')
            cls.df_positions = pd.read_csv(
                'dublinBikesPrediction/assets/STATION ID - POSITION.csv')
            print('Model load complete')
        return cls._instance

    # def set_some_variable(self, value):
    #     Singleton.some_variable = value

    def get_model(self):
        return DublinBikesModel.model

    def get_df_stations(self):
        return DublinBikesModel.df_stations

    def get_df_positions(self):
        return DublinBikesModel.df_positions


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
    if (weather_forecast == None):
        weather_forecast = get_weather_forecast()

    res = pd.DataFrame.from_dict(pd.json_normalize(
        weather_forecast['hourly']['data']), orient='columns')
    res['date'] = pd.to_datetime(res['date'])
    res = res[['date', 'precipitation.total', 'temperature']]
    res.rename(columns={'precipitation.total': 'rain',
               'temperature': 'temp', 'date': 'TIME'}, inplace=True)

    res['hour'] = res['TIME'].dt.hour
    res['minute'] = res['TIME'].dt.minute
    res['day'] = res['TIME'].dt.day
    res['dayofweek'] = res['TIME'].dt.dayofweek

    df_stations = dublinBikesModel.get_df_stations()
    res = merge_dfs_on_stations(df_stations, res)
    res = res.reset_index(drop=True)
    df_return = pd.DataFrame()
    df_return = res.copy()
    df_return.drop(['hour', 'minute', 'day', 'dayofweek'],
                   axis=1, inplace=True)
    res.drop('TIME', axis=1, inplace=True)
    return res, df_return


def merge_dfs_on_stations(df1, df2):
    df1['dummy'] = 1
    df2['dummy'] = 1
    df2 = pd.merge(df1, df2, on='dummy')
    df2 = df2.drop(columns='dummy')
    return df2


def predict(request):
    df_query, df_return = prepare_query_for_model()
    prediction = dublinBikesModel.get_model().predict(df_query)
    df_return['prediction'] = prediction
    positions = dublinBikesModel.get_df_positions()
    return JsonResponse({'prediction': json.loads(df_return.to_json(orient='records')), 'positions': json.loads(positions.to_json(orient='records'))}, safe=False)
