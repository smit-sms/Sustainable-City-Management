import time
import threading
import unittest
import requests
from etl_pipeline_ggn1_ase_g5 import ETLTask, base64encode_obj

class TestETLPipeline(unittest.TestCase):
    """ Class that tests the ETLPipeline. """

    def test_01_server_up(self):
        """ Check if the server is running. """
        response = requests.get("http://127.0.0.1:8003/docs")
        self.assertEqual(response.status_code, 200)

    def test_02_create_task(self):
        """ 
        This test checks status of the task creation
        endpoint. Both success and failure case.
        """
        # Success case.
        # Ensure a task with name "task1" does not already
        # exist in the DB before running this test.
        task_success = ETLTask(
            name="task1",
            fun_data_load=load_data_bikes,
            fun_data_transform=transform_data_bikes,
            fun_data_save=save_data_bikes,
            repeat_time_unit='seconds',
            repeat_interval=10
        )
        task_str = base64encode_obj(task_success)
        response = make_post_request(
            url="http://127.0.0.1:8003/task", 
            data={"task_str": task_str}
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("Success. Task created and scheduled", response['message'])

        # Failure case.
        # Fails because save function tried to save
        # data to a path that does not exist.
        # Such faults with provided functions should
        # throw errors and also ensure that partially
        # processed tasks are not in the DB.
        task_failure = ETLTask(
            name="task2",
            fun_data_load=load_toy_data,
            fun_data_transform=transform_toy_data,
            fun_data_save=save_toy_data_fail,
            repeat_time_unit='seconds',
            repeat_interval=1
        )
        task_str = base64encode_obj(task_failure)
        response = make_post_request(
            url="http://127.0.0.1:8003/task", 
            data={"task_str": task_str}
        ).json()
        self.assertEqual(response['status'], 400)
        self.assertIn("Failure", response['message'])
        response = make_get_request(
            url="http://127.0.0.1:8003/task", 
            data={"task_name": "task2"}
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("Success. No such task", response['message'])

        # Success case.
        task_success = ETLTask(
            name="task2",
            fun_data_load=load_toy_data,
            fun_data_transform=transform_toy_data,
            fun_data_save=save_toy_data,
            repeat_time_unit='seconds',
            repeat_interval=1
        )
        task_str = base64encode_obj(task_success)
        response = make_post_request(
            url="http://127.0.0.1:8003/task", 
            data={"task_str": task_str}
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("Success", response['message'])

        # Failure case.
        # Fails because task id is not unique.
        task_failure = ETLTask(
            name="task1",
            fun_data_load=load_toy_data,
            fun_data_transform=transform_toy_data,
            fun_data_save=save_toy_data,
            repeat_time_unit='seconds',
            repeat_interval=5
        )
        task_str = base64encode_obj(task_failure)
        response = make_post_request(
            url="http://127.0.0.1:8003/task", 
            data={"task_str": task_str}
        ).json()
        self.assertEqual(response['status'], 400)
        self.assertIn("Failure. Could not create task", response['message'])
        self.assertIn("UNIQUE", response['message']) 

    def test_03_read_task(self):
        """ 
        Tests API endpoints that facilitate 
        task reading from the DB.
        """
        # Failure case.
        # Requested task does not exist.
        # Should return status 200 as this is not an 
        # error but returned message should state that
        # the task does not exist.
        response = make_get_request(
            url="http://127.0.0.1:8003/task", 
            data={"task_name": "task3"}
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("Success. No such task", response['message'])

        # Success case.
        # Retrieve fields of a task that does exist.
        response = make_get_request(
            url="http://127.0.0.1:8003/task", 
            data={
                "task_name": "task2", 
                "fields":"repeat_time_unit repeat_interval"
            }
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("Success.", response['message'])
        self.assertIn("repeat_time_unit", response['data'].keys())

        # Success case.
        # Retrieve all data.
        response = make_get_request(url="http://127.0.0.1:8003/task/all").json()
        self.assertEqual(response['status'], 200)
        self.assertIn("Success.", response['message'])
        self.assertEqual(2, len(response['data']))

    def test_04_update_task(self):
        """ 
        Tests API endpoint that facilitate 
        updating a task.
        """
        # Failure case.
        # Trying to update a task that is not stopped
        # should result in a response that prompts for this.
        response = make_put_request(
            url="http://127.0.0.1:8003/task",
            task_name="task2",
            data={
                "repeat_time_unit": "seconds", 
                "repeat_interval": "5"
            }
        ).json()
        self.assertEqual(response['status'], 400)
        self.assertIn("Please stop", response['message'])

        # Stop task.
        response = make_put_request(
            url="http://127.0.0.1:8003/task/stop",
            task_name="task2"
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("stopped", response['message'])

        # Failure case.
        # If an invalid field is tried to be updated, then
        # a failure occurs.
        response = make_put_request(
            url="http://127.0.0.1:8003/task",
            task_name="task2",
            data={
                "invalid_field": "invalid_field", 
            }
        ).json()
        self.assertEqual(response['status'], 400)
        self.assertIn("Failure.", response['message'])

        # Success case.
        response = make_put_request(
            url="http://127.0.0.1:8003/task",
            task_name="task2",
            data={
                "repeat_time_unit": "seconds", 
                "repeat_interval": "5"
            }
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("Success", response['message'])
        response = make_put_request(
            url="http://127.0.0.1:8003/task/start",
            task_name="task2"
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("Started", response['message'])

    def test_05_task_start_stop(self):
        """ 
        Tests the functionality that 
        allows one to start and stop a task.
        """
        # Success.
        # Stop a task.
        response = make_put_request(
            url="http://127.0.0.1:8003/task/stop",
            task_name="task1"
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("stopped", response['message'])

        # Failure case.
        # Trying to stop a task that does not exist
        # or is not currently scheduled should return
        # a message that informs about this without
        # throwing a error.
        response = make_put_request(
            url="http://127.0.0.1:8003/task/stop",
            task_name="task3"
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("is not running or scheduled", response['message'])

        # Success.
        # Start a task.
        response = make_put_request(
            url="http://127.0.0.1:8003/task/start",
            task_name="task1"
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("Started", response['message'])

        # Success case.
        # Starting a task that is already running
        # should return a message that informs about this.
        response = make_put_request(
            url="http://127.0.0.1:8003/task/start",
            task_name="task2"
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("is already scheduled/running", response['message'])

        # Failure case.
        # Trying to start a task that does not exist
        # should inform that this task does not exist
        # without throwing an error.
        response = make_put_request(
            url="http://127.0.0.1:8003/task/start",
            task_name="task3"
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("No such task", response['message'])

    def test_06_scheduler_start_stop(self):
        """ 
        Tests the functionality that 
        allows one to start and stop the scheduler.
        """
        # Failure case.
        # Trying to start an already running
        # scheduler will result in a message
        # informing the user of this without
        # throwing an error.
        response = make_get_request(
            url="http://127.0.0.1:8003/scheduler/start"
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("already running", response['message'])

        # Success case.
        # Stop scheduler
        response = make_get_request(
            url="http://127.0.0.1:8003/scheduler/stop"
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("stopped", response['message'])

        # Failure case.
        # Trying to stop a scheduler that's
        # already not running results in a
        # message should return a message that 
        # informs of the scheduler's state 
        # without throwing an error.
        response = make_get_request(
            url="http://127.0.0.1:8003/scheduler/stop"
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("not running", response['message'])

        # Success case.
        # Start scheduler
        response = make_get_request(
            url="http://127.0.0.1:8003/scheduler/start"
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("started", response['message'])

    def test_07_delete_task(self):
        """ 
        This test checks status of the task deletion
        endpoint. Both success and failure case.
        """
        # Failure case.
        # Fails because a scheduled task must be 
        # stopped before it can be deleted.
        response = make_delete_request(
            url="http://127.0.0.1:8003/task", 
            data={"task_name": "task2"}
        ).json()
        self.assertEqual(response['status'], 400)
        self.assertIn("stop it before deleting", response['message'])

        # Stop task 1.
        response = make_put_request(
            url="http://127.0.0.1:8003/task/stop",
            task_name="task1",
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("stopped", response['message'])

        # Success case.
        # Delete task 1.
        response = make_delete_request(
            url="http://127.0.0.1:8003/task", 
            data={"task_name": "task1"}
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("has been deleted", response['message'])

        # Stop task 2.
        response = make_put_request(
            url="http://127.0.0.1:8003/task/stop",
            task_name="task2",
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("stopped", response['message'])

        # Success case.
        # Delete task 2.
        response = make_delete_request(
            url="http://127.0.0.1:8003/task", 
            data={"task_name": "task2"}
        ).json()
        self.assertEqual(response['status'], 200)
        self.assertIn("has been deleted", response['message'])

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

def make_put_request(url, task_name, data={}):
    """
    Makes a put request.
    @param url: URL to post to.
    @data: Request body data.
    @return: Response.
    """
    response = requests.put(
        url=url, 
        params={"task_name": task_name}, 
        json=data
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
        + 'ETLPipeline/tests/data.csv'
    )
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['timestamp', 'description'])
        writer.writerows([[str(datetime.now()), "toy data"]])
    print(f'Saved data {data}.')

def save_toy_data_fail(data): 
    """ A toy placeholder save data function. """
    import os
    import csv
    from datetime import datetime
    csv_file = ( # Invalid path.
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