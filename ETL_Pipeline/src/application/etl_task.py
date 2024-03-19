import requests
import schedule
from typing import Callable
from datetime import datetime

class ETLTaskFunction:
    """ 
    A task that is a combination of
    function and arguments.
    """
    def __init__(self, function:Callable, args:list=[]):
        """
        Constructor.
        @param function: Function.
        @param args: List of arguments for this function.
        """
        self.function = function
        self.args = args

    def run(self):
        """ Runs this function with set arguments. """
        return self.function(*self.args)

class ETLTask:
    """ A class that defines a pipeline task. """

    def __init__(self, 
        name:str, 
        fun_data_load:Callable,
        fun_data_save:Callable,
        repeat_time_unit:str,
        repeat_interval:int,
        num_runs:int=0,
        time_run_last_start:datetime=None,
        time_run_last_end:datetime=None,
        status:str="scheduled",
        config:dict={}
    ):
        """ 
        Constructor. 
        @param name: String identifier.
        @param fun_data_load: Function that loads data from a desired source.
        @param fun_data_save: Function that saves data to a desired destination.
        @param repeat_time_unit: The unit of time for periodic execution 
                                 (seconds, minutes, hours, days).
        @param repeat_interval: The units of time after which this function shall
                                be executed again.
        @param num_runs: No. of times this function has run.
        @param time_run_last_start: Last time at which this function started running.
        @param time_run_last_end: Last time this function finished running.
        @param config: Data extract/transform configurations.
        """
        self.name = name
        self.repeat_time_unit = repeat_time_unit
        self.repeat_interval = repeat_interval
        self.num_runs = num_runs
        self.time_run_last_start = time_run_last_start
        self.time_run_last_end = time_run_last_end
        self.status = status
        self.fun_data_load = fun_data_load
        self.fun_data_save = fun_data_save
        self.config = config

    def run(self, url:str):
        """ 
        Sequence of tasks to repeatedly execute within 
        1 run of this task. 
        @param url: The URL to hit with PUT request to 
                    change status of this task as it runs.
        """
        # Changing task status from scheduled to running as task
        # starts running. Also, time at which this task started 
        # running is recorded.
        self.time_run_last_start = datetime.now().isoformat()
        res = requests.put(url, params={'task_name': self.name}, json={
            'status': 'running',
            'time_run_last_start': self.time_run_last_start
        }).json()
        if res['status'] != 200:
            raise Exception(f"Task {self.name}. Something went wrong. {res}")
        
        # Run the load data function.
        data = self.fun_data_load()

        # Apply transformations as per data config.
        # Transforming data ... TO DO ...
            
        # Run the save data function.
        self.fun_data_save(data)
        
        # Getting no. of times this task has run so far, from the DB.
        res = requests.get(url, params={'task_name': self.name, 'fields': 'num_runs'}).json()
        if res['status'] != 200:
            raise Exception(f"Task {self.name}. Something went wrong. {res}")
        
        # Changing task status from scheduled to running as task
        # starts running. Also, time at which this task started 
        # running is recorded along with new no. of times it has run
        # = old no. of times + 1.
        self.time_run_last_end = datetime.now().isoformat()
        res = requests.put(url, params={'task_name': self.name}, json={
            'status': 'scheduled',
            'time_run_last_end': self.time_run_last_end,
            'num_runs': res['data']['num_runs'] + 1
        }).json()
        if res['status'] != 200:
            raise Exception(f"Task {self.name}. Something went wrong. {res}")

    def schedule(self, schedule:schedule, host:str, port:int):
        """ 
        Schedules a task for repeated running.
        @schedule: Schedule that shall contain this task.
        @host: Host where the ETL application is ruuning.
        @port: Port where the ETL application is running.
        """
        url = f"http://{host}:{port}/task"
        self.run(url) # Run once immediately, then every scheduled time.
        if self.repeat_time_unit == "seconds":
            job = schedule.every(self.repeat_interval).seconds.do(lambda: self.run(url))
        elif self.repeat_time_unit == "minutes":
            job = schedule.every(self.repeat_interval).minutes.do(lambda: self.run(url))
        elif self.repeat_time_unit == "hours":
            job = schedule.every(self.repeat_interval).hours.do(lambda: self.run(url))
        elif self.repeat_time_unit == "days":
            job = schedule.every(self.repeat_interval).days.do(lambda: self.run(url))
        else:
            raise Exception(f'Task "{self.name}: Invalid repeat time unit "{self.repeat_time_unit}".')
        return job