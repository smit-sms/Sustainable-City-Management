import os, requests
import pandas as pd
from datetime import datetime, timedelta
import json
from sensors.models import Sensor, Air, Noise
import pytz

# Function to convert datetime to Unix timestamp
def to_unix_timestamp(dt):
    return int(dt.timestamp())

# Function to fetch data for a sensor within a specific time range
def fetch_sensor_data(sensor, start_timestamp, end_timestamp, username, password):
    url = os.getenv('SONITOS_API_URL') + "/api/data"
    data = {
        "username": username,
        "password": password,
        "monitor": sensor,
        "start": start_timestamp,
        "end": end_timestamp
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        if response.status_code == 200 and response.text != '' and response.text != 'error' and type(response.json())==type([]):
            return response.json()
        return []
    except Exception as e:
        print(f"Exception while fetching data for sensor {sensor}: {e}, response received is: {response.text}")
        return []


def fetch_data_over_period(sensor, start_date, end_date, username, password):
    start_timestamp = to_unix_timestamp(start_date)
    end_timestamp = to_unix_timestamp(end_date)
    sensor_data = fetch_sensor_data(sensor, start_timestamp, end_timestamp, username, password)
    return sensor_data

def run():
    username = os.getenv('SONITOS_USERNAME')
    password = os.getenv('SONITOS_PASSWORD')
    sensors = Sensor.objects.all()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)  # 1 month

    for sensor in sensors:
        # model = Air if sensor.sensor_type=='air' else Noise
        print(f"Fetching data for {sensor.sensor_type} sensor:{sensor.serial_number}...")
        sensor_data = fetch_data_over_period(sensor.serial_number, start_date, end_date, username, password)
        for sensor_data_value in sensor_data:
            if len(sensor_data_value) > 1:
                if(sensor.sensor_type=='air'):
                    sensor_value = sensor_data_value.get('pm2_5') if sensor_data_value.get('pm2_5') else sensor_data_value.get('no2')
                    parsed_datetime = datetime.strptime(sensor_data_value.get('datetime'), '%Y-%m-%d %H:%M:%S')

                    # Make the parsed datetime object timezone-aware
                    timezone = pytz.timezone('GMT')  # Replace 'Your_Timezone_Here' with your desired timezone
                    timezone_aware_datetime = timezone.localize(parsed_datetime)
                    try:
                        air_instance = Air.objects.get(sensor=sensor)
                        if air_instance.datetime <= timezone_aware_datetime:
                            air_instance.pm2_5 = sensor_value
                            air_instance.datetime = timezone_aware_datetime
                            air_instance.save()
                    except Air.DoesNotExist:
                        air_instance = Air.objects.create(
                            sensor=sensor,
                            pm2_5=sensor_value,
                            datetime = timezone_aware_datetime
                        )
                else:
                    sensor_value = sensor_data_value.get('laeq')
                    parsed_datetime = datetime.strptime(sensor_data_value.get('datetime'), '%Y-%m-%d %H:%M:%S')

                    # Make the parsed datetime object timezone-aware
                    timezone = pytz.timezone('GMT')  # Replace 'Your_Timezone_Here' with your desired timezone
                    timezone_aware_datetime = timezone.localize(parsed_datetime)
                    try:
                        noise_instance = Noise.objects.get(sensor=sensor)
                        if noise_instance.datetime <= timezone_aware_datetime:
                            noise_instance.laeq = sensor_value
                            noise_instance.datetime = timezone_aware_datetime
                            noise_instance.save()
                    except Noise.DoesNotExist:
                        noise_instance = Noise.objects.create(
                            sensor=sensor,
                            laeq=sensor_value,
                            datetime = timezone_aware_datetime
                        )
