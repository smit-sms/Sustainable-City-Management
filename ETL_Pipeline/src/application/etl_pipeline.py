import dill
import time
import uvicorn
import sqlite3
import schedule
import argparse
import threading
from typing import List
from etl_task import ETLTask
from datetime import datetime, timedelta
from fastapi import FastAPI, Query, Body
from etl_db_manager import ETLDataBaseManager
from utility import base64encode_obj, base64decode_obj

# Global variables.
DB_MANAGER = None
HOST = None
PORT = None
SCHEDULER_RUNNING = False
SCHEDULED_JOBS = {}

# Utility functions.
def run_scheduler():
    """ Runs the task scheduler on a separate thread than main. """
    while SCHEDULER_RUNNING == True:
        print("[DEBUG]")
        schedule.run_pending()
        time.sleep(1)  # Sleep time = 1 second.

def start_tasks():
    """
    Restarts periodic running of all saved tasks
    whose repeat time is overdue.
    """
    global SCHEDULED_JOBS
    global HOST
    global PORT
    print('Started existing scheduled tasks.')
    for task in DB_MANAGER.load_tasks(filters={'status':'scheduled'}):
        # if not task.name in SCHEDULED_JOBS:
        task.schedule(schedule=schedule, host=HOST, port=PORT)
            # job = task.schedule(schedule=schedule, host=HOST, port=PORT)
            # SCHEDULED_JOBS[task.name] = job # Keep a reference of this scheduled job.

# Initialize FastAPI app.
app = FastAPI()

# Create a task.
@app.post("/task/", summary="Create new ETL task.", description="Create a new ETL task, add it to the DB and schedule it.")
def create_task(task_str:str):
    """
    Creates a new ETL task, adds it to the DB and schedules it.
    @param task_str: Base64 encoded byte string of an ETL Task object.
    @return: Response to request.
    """
    response = {'status': 200, 'message': f'', 'data':[]}
    try:
        if SCHEDULER_RUNNING == False:
            start_scheduler()
        task = base64decode_obj(task_str) # Get ETL Task from base64 encoded string.
        DB_MANAGER.create_task(task) # Add task into DB.
        # task.schedule(schedule=schedule, host=HOST, port=PORT)
        job = task.schedule(schedule=schedule, host=HOST, port=PORT) # Schedule task.
        SCHEDULED_JOBS[task.name] = job # Keep a reference of this scheduled job.
        response['message'] = f"Success. Task created and scheduled {task.name}."
    except Exception as e:
        response['status'] = 400
        response['message'] = f"Failure. Could not create task. {e}"
    return response

@app.delete("/task/")
def delete_task(task_name: str):
    """
    Deletes a task with given name if it exists.
    @param task_name: Name of task to delete.
    """
    global DB_MANAGER
    global SCHEDULED_JOBS
    response = {'status': 200, 'message': f'', 'data':[]}
    try:
        if task_name in SCHEDULED_JOBS:
            stop_task(task_name)
            DB_MANAGER.delete_task(name=task_name)
            del(SCHEDULED_JOBS[task_name])
    except Exception as e:
        response['status'] = 400
        response['message'] = f"Failure. Could not delete task {task_name}. {e}"
    response["message"] = f"Success. Deleted task {task_name}."
    return response

@app.get("/task/")
def read_task(task_name:str, fields:str=''):
    """
    Get a task with given name if it exists.
    @param task_name: Name of task to delete.
    @param fields: Fields of data that is to be returned as a string
                   separated by spaces. By default, all fields are returned.
    @return: Response to request.
    """
    response = {'status': 200, 'message': f'', 'data':[]}
    if fields == '':
        fields = [
            "name", "fun_data_load", "fun_data_save",
            "repeat_time_unit", "repeat_interval", 
            "time_run_last_start", "time_run_last_end", 
            "num_runs", "status", "config"
        ]
    else:
        fields = fields.split(' ')
    try:
        task = DB_MANAGER.read_task(name=task_name, fields=fields)
        response["data"] = task
        response["message"] = f"Success. Retrieved task {task_name}."
    except Exception as e:
        response['status'] = 400
        response['message'] = f"Failure. Could not get task {task_name}. {e}"
    return response

@app.get("/task/all/")
def read_all_tasks():
    """
    Get all tasks (name, status) currently in the DB.
    @return: Response to request.
    """
    response = {'status': 200, 'message': f'', 'data':[]}
    try:
        response["data"] = []
        for task in DB_MANAGER.load_tasks():
            response["data"].append({
                'name': task.name,
                'status': task.status,
                'num_runs': task.num_runs,
                'repeat_time_unit': task.repeat_time_unit,
                'repeat_interval': task.repeat_interval,
                'time_run_last_start': str(task.time_run_last_start),
                'time_run_last_end': str(task.time_run_last_end)
            })
        response["message"] = f"Success. Retrieved tasks."
    except Exception as e:
        response['status'] = 400
        response['message'] = f"Failure. Could not get tasks. {e}"
    return response

@app.put("/task/")
def update_task(task_name: str, new_values: dict):
    """
    Update status of a task in DB with given name 
    and stataus if it exists.
    @param task_name: Name of task to update.
    @param new_values:New values that should replace old ones.
                      Keys of this dictionary are field names
                      and values are new data for these fields.
    @return: Response to request.
    """
    response = {'status': 200, 'message': f'', 'data':[]}
    try:
        DB_MANAGER.update_task(name=task_name, new_values=new_values)
    except Exception as e:
        response['status'] = 400
        response['message'] = f"Failure. Could not update status of task {task_name}. {e}"
    response["message"] = f"Success. Status of task {task_name} updated with new values {new_values}."
    return response

@app.put("/task/stop")
def stop_task(task_name: str):
    """
    Stops a currently scheduled task.
    @param task_name: Name of task to stop.
    @return: Response to request.
    """
    global SCHEDULED_JOBS
    response = {'status': 200, 'message': f'', 'data':[]}
    try:
        if task_name in SCHEDULED_JOBS:
            schedule.cancel_job(job=SCHEDULED_JOBS[task_name])
            DB_MANAGER.update_task(name=task_name, new_values={'status': 'stopped'})
            print(f"Task {task_name} stopped.")
            response['message'] = 'Success. Task has been stopped.'
    except Exception as e:
        response['status'] = 400
        print(f"Task {task_name} could not be stopped.")
        response['message'] = f"Failure. Could not stop task {task_name}. {e}"
    response["message"] = f"Success. Task {task_name} has been stopped."
    return response

@app.get("/start_scheduler")
def start_scheduler():
    """ Start the task scheduler thread. """
    global SCHEDULER_RUNNING
    response = {"status": 200, "message": "", "data":[]}
    try: # Start the scheduler in a separate thread.
        if SCHEDULER_RUNNING == True: 
            response["status"] = 200
            print('Scheduler is already running.')
            response['message'] = 'Scheduler is already running.'
        else:
            SCHEDULER_RUNNING = True
            threading.Thread(target=run_scheduler).start()
            start_tasks()
            print('Scheduler started.')
            response["status"] = 200
            response["message"] = f"Scheduler started."
    except Exception as e:
        response["status"] = 400
        response["message"] = f"Scheduler could not be started. {e}"
    return response

@app.get("/stop_scheduler")
def stop_scheduler():
    """ Stop the task scheduler. """
    global SCHEDULER_RUNNING
    response = {"status": 200, "message": "", "data":[]}
    try: # Start the scheduler in a separate thread.
        if SCHEDULER_RUNNING == False:
            response["status"] = 200
            print("Scheduler is not running.")
            response["message"] = "Scheduler is not running."
        else:
            SCHEDULER_RUNNING = False
            response["status"] = 200
            print("Scheduler stopped.")
            response["message"] = "Scheduler stopped."
    except Exception as e:
        response["status"] = 400
        response["message"] = f"Scheduler could not be stopped. {e}"
    return response

if __name__ == "__main__":
    # Received DB name and path as cmd arguments.
    parser = argparse.ArgumentParser(description='ETL Pipeline argument parser. Please input path to the data base containing ETLTask status and its name.')
    parser.add_argument('--db-name', type=str, required=True, help='Name of the data base.')
    parser.add_argument('--db-path', type=str, default='.', help='Path to the data base.')
    parser.add_argument('--host', type=str, default="127.0.0.1", help='Name of host where this app shall run.')
    parser.add_argument('--port', type=int, default=8003, help='Name of port where this app shall run.')
    args = parser.parse_args()

    # Prepare app for running.
    # Set up ETL Tasks DB.
    HOST = args.host
    PORT = args.port
    DB_MANAGER = ETLDataBaseManager(db_name=args.db_name, db_path=args.db_path)

    uvicorn.run(app, host=args.host, port=args.port)