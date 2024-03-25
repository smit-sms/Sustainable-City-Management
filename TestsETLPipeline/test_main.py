import unittest
import requests
from etl_pipeline_ggn1_ase_g5 import ETLTask, base64encode_obj

class TestETLPipeline(unittest.TestCase):
    """ Class that tests the ETLPipeline. """

    def test_server_up(self):
        """ Check if the server is running. """
        response = requests.get("http://127.0.0.1:8003/docs")
        self.assertEqual(response.status_code, 200)

    def test_create_task(self):
        """ 
        This test checks status of the task creation
        endpoint. Both success and failure case.
        """
        task_success = ETLTask(
            name="task1",
            fun_data_load=load_toy_data,
            fun_data_transform=transform_toy_data,
            fun_data_save=save_toy_data,
            repeat_time_unit='seconds',
            repeat_interval=5
        )
        task_str = base64encode_obj(task_success)
        response = make_post_request(
            url="http://127.0.0.1:8003/task", 
            data={"task_str": task_str}
        ).json()
        print('[DEBUG] Response =', response)
        # self.assertEqual(response.status_code, 200)

# Functions that help make requests.
def make_post_request(url, data={}):
    """
    Makes a post request.
    @param url: URL to post to.
    @data: Request body data.
    @return: Response.
    """
    response = requests.post(url, params=data)
    return response

def make_get_request(url, data={}):
    """
    Makes a post request.
    @param url: URL to post to.
    @data: Request body data.
    @return: Response.
    """
    response = requests.get(url, params=data)
    return response

def make_delete_request(url, data={}):
    """
    Makes a delete request.
    @param url: URL to post to.
    @data: Request body data.
    @return: Response.
    """
    response = requests.delete(url, params=data)
    return response

def make_put_request(url, task_name, new_values):
    """
    Makes a put request.
    @param url: URL to post to.
    @data: Request body data.
    @return: Response.
    """
    response = requests.put(
        url=url, 
        params={"task_name": task_name}, 
        json=new_values
    )
    return response

# Sample data load, transform and save function.
def load_data_bikes():
    """ Loads last 30 min snapshot of dublin bike stands. """
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
    import pandas as pd

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
            url="http://localhost:8000/bikes/snapshot/", 
            json={'snapshot':data}
        )
        print(res.json()['message'])
    except Exception as e:
        print(f'Failed to save bikes data. {e}')
        raise Exception(f'Failed to save bikes data. {e}')

def load_toy_data(): 
    """ A toy placeholder load data function. """
    print(f'Loaded data.')
    return 1

def transform_toy_data(data):
    """ A toy placeholder transform data function. """
    data_transformed = data * 10 # Deliberate error to showcase logging.
    print(f'Transformed data {data} into {data_transformed}.')
    return data_transformed

def save_toy_data(data): 
    """ A toy placeholder save data function. """
    import os
    import csv
    from datetime import datetime
    csv_file = (
        'C:/Users/g_gna/Documents/TCD/Modules/'
        + 'CS7CS3_AdvancedSoftwareEngineering/GitHub/'
        + '___TestsETLPipeline/data.csv'
    )
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['timestamp', 'description'])
        writer.writerows([[str(datetime.now()), "toy data"]])
    print(f'Saved data {data}.')

if __name__ == "__main__":
    print('Module Tests: ETL Pipeline')
    unittest.main()