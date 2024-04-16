import time
import requests
from etl_pipeline_ggn1_ase_g5.etl_task import ETLTask
from etl_pipeline_ggn1_ase_g5.utility import base64encode_obj


def load_data_bikes():
    """ 
    Loads last 30 min snapshot of dublin bike stands. 
    """
    import requests
    data = []
    try:
        res = requests.get(f"https://data.smartdublin.ie/dublinbikes-api/last_snapshot")  
        data = res.json()
    except Exception as e:
          data = []
          print(f'Failed to fetch dublin bikes data from source: {e}')
          raise Exception(f'Failed to fetch dublin bikes data from source: {e}')
    return data


def transform_data_bikes(data):
    """
    Transforms bikes data to be in a desireable format for saving.
    @param data: Data to be transformed.
    """
    import pytz
    import pandas as pd
    from datetime import datetime

    df = pd.DataFrame(data)
    df['usage_percent'] = df['available_bikes']/df['bike_stands']
    df['usage_percent'] = df['usage_percent'].round(2)
    df['status'] = df['status'].str.lower()
    df = df[[
        'station_id', 'bike_stands', 
        'available_bikes', 'usage_percent', 
        'last_update', 'status'
    ]]
    print("Bike data transformed. Usage % computed and last update made lowercase.")
    return df.to_dict(orient='records')


def save_data_bikes(data):
    """ 
    Saves given data to csv file. 
    @param data: Data to be saved.
    """
    import requests
    try:
        res = requests.post(
            url="http://0.0.0.0:8000/city_services/dublin-bikes/", 
            json={'dublin_bikes':data}
        )
        return res
    except Exception as e:
        print(f'Failed to save bikes data. {e}')
        raise Exception(f'Failed to save bikes data. {e}')


def make_post_request(url, data={}):
    """
    Makes a post request.
    @param url: URL to post to.
    @data: Request body data.
    @return: Response.
    """
    response = requests.post(url, params=data)
    return {'status': response.status_code, 'message': response.json()['message']}


task = ETLTask(
    name="Dublin_Bikes_Data_Pipeline",
    fun_data_load=load_data_bikes,
    fun_data_transform=transform_data_bikes,
    fun_data_save=save_data_bikes,
    repeat_time_unit='seconds',
    repeat_interval=1800            # 30 minutes
)

# Wait for 5 seconds for the etl_pipeline process to start 
# and then submit the task
time.sleep(5)
task_str = base64encode_obj(task)
res = make_post_request(url="http://0.0.0.0:8003/task", data={"task_str": task_str})
