# This file contains functions that can receive 
# functions from users that allow from periodic
# loading or saving of data from their choice of
# data source and destination.

# Required packages.
import asyncio 
from typing import Callable
from fastapi import FastAPI, BackgroundTasks

# All tasks.
tasks = {0: {'name': 'test', 'desc': 'test'}} # Sample dictionary mimicking database within which tasks are to be stored.
available_ids = [1] #List of task ids that are currently available for registration.

# Define FastAPI app.
app = FastAPI()

def __is_task_exists_by_id(id:int):
    """
    Returns whether a task with given id it has been registered.
    @param id: Id of the task.
    @return: True if task has been registered and false otherwise.
    """
    return not id is None and id in tasks
        
def __is_task_exists_by_name(name:str):
    """
    Returns whether a task with given name it has been registered.
    @param name: Name of the task.
    @return: True and id of task if it has been registered and false otherwise.
    """
    for id, task in tasks.items():
        if task["name"] == name:
            return True, id
    return False

async def execute_periodically(task, interval, task_id):
    """ 
    Executes given task periodically.
    @param task: Task to execute.
    @interval: Interval in seconds after which the task is to be executed again.
    @task_id: Identifier of task being executed.
    """
    while True:
        await asyncio.sleep(interval)
        task(task_id)

@app.get('/task')
async def get_tasks(id:int=None, name:str=None):
    """
    Function that returns name, id and description of 
    a registered task with given id or name. 
    Id has preference over name. If neither are given,
    returns all tasks.
    @param id: Id of the task.
    @param name: Name of the task.
    @return: List of tasks in the form 
             {"id": -1, "name": "", "desc": ""}.
    """
    task_list = []
    # If id has been give and a task with the given
    if not id is None:
        if __is_task_exists_by_id(id=id):
            t = tasks[id]
            task_list.append({'id': id, 'name': t['name'], 'desc': t['desc']})
    elif not name is None:
        task_exists = __is_task_exists_by_name(name=name)
        if task_exists[0]:
            id = task_exists[1]
            t = tasks[id]
            task_list.append({'id': id, 'name': t['name'], 'desc': t['desc']})
    else:
        for k, v in tasks.items():
            task_list.append({"id": k, "name": v["name"], "desc":v["desc"]})
    return task_list
            
@app.post('/register_task')
async def add_task(
    fun_fetch:Callable, fun_save:Callable, 
    task_name:str, task_desc:str, 
    background_tasks:BackgroundTasks,
    repeat:int=0, task_id:int=None
):
    """
    Function that registers a new task,
    given a function to fetch and save data from/to a desired 
    data source/sink every given interval in seconds. A task
    id and description is also provided to keep track of this task 
    so that it can be started/stopped later.
    @param fun_fetch: Function that fetches data from a data source.
    @param fun_save: Function that saves data to a data sink.
    @param interval: Interval after which this task is to be repeated
                     in seconds. Is 0 seconds by default.
    @param task_desc: Description of the task as a string.
    @param task_id: Integer identifier of this task. If not given, the
                    next available ID is used.
    @param task_name: Name of this task. Can be used to query for ID.
    @return: HttpResponse with registration status.
    """
    # TO DO ...
    pass