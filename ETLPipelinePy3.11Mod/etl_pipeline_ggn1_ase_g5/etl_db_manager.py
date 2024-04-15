import dill
import base64
import sqlite3
from typing import List
from datetime import datetime
from .etl_task import ETLTask

def process_value_for_db(value):
    """
    Given a python value returns the processed version of it that is 
    right for entering into the SQLite DB or for SQL queries.
    @param value: Value to be processed.
    @return: Value in desired format for SQL.
    """
    # If the value is an integer, float or string return as is.
    if type(value) in [int, float, str]:
        return value
    
    # If the value is date time, return it in isoformat.
    if type(value) == datetime:
        return value.isoformat()

    # If the value is some other object (ETLFunction, dict),
    # return it in sqlite binary format.
    else: return sqlite3.Binary(dill.dumps(value))

def process_value_from_db(t:tuple, fields=List[str]):
    """
    Given a tuple retrieved from the DB, returns the processed 
    version of it that can be returned via the API.
    @param t: Tuple from DB to be processed.
    @param fields: Fields in received tuple.
    @return: Tuple as an ETLTask object.
    """
    to_return = {}
    for i in range(len(fields)):
        field = fields[i]
        value = t[i]
        if field in [ # Stored as string, integer or float.
            'name', 'repeat_time_unit', 'repeat_interval', 
            'num_runs', 'status'
        ]:
            to_return[field] = value
        elif field in [
            'fun_data_load', 
            'fun_data_transform', 
            'fun_data_save', 
        ]: # Stored as BLOB.
            to_return[field] = base64.b64encode(value).decode('utf-8')
        elif field in [ # Stored as datetime iso string.
            'time_run_last_start', 'time_run_last_end'
        ]: to_return[field] = datetime.strptime(
            value, "%Y-%m-%dT%H:%M:%S.%f"
        ) if value is not None else None
    return to_return

# Set up a database where all scheduled tasks will be stored.
class ETLDataBaseManager:
    """
    A scheduler that leverages a SQLite database to plan and
    execute data ETL tasks.
    """

    def __init__(self, db_name:str, db_path:str):
        """ 
        Constructor.
        @param db_name: Name of associated database.
        @param db_path: Path at which to store db.
        """

        # Check DB availability.
        self.db_name = db_name
        self.db_path = db_path
        self.current_tasks = {}
        self.__connect_db()

    def __connect_db(self):
        """
        Connects to the SQLlite DB that maintains state of all data pipeline tasks.
        If such a DB does not exist, it is created with desied tables added to it.
        """
        # Create a table to store state of tasks if 
        # it does not already exist.
        try:
            self.query(q='''CREATE TABLE IF NOT EXISTS etl_tasks (
                name TEXT PRIMARY KEY,
                fun_data_load BLOB NOT NULL,
                fun_data_transform BLOB,
                fun_data_save BLOB NOT NULL,
                repeat_time_unit TINYTEXT NOT NULL,
                repeat_interval INTEGER NOT NULL,
                time_run_last_start DATETIME,
                time_run_last_end DATETIME,
                num_runs INTEGER NOT NULL,
                status TINYTEXT NOT NULL
            )''')
        except Exception as e:
            print(f"Oops. Something went wrong :( . Error: {e}.")
        print(f"Database '{self.db_path}/{self.db_name}.db' available :) .")

    def query(self, q:str, params:list=[], is_get:bool=False):
        """ 
        Execute a SQL query.
        @param q: Query to execute.
        @param params: Parameters for parameterized queries.
        @param is_get: Whether query result is returnable.
        @return: All results if results are requested. 
                 Returns 1 if the query ran successfully
                 and 0 otherwise.
        """
        # Connect to the SQLite database.
        connection = sqlite3.connect(f"{self.db_path}/{self.db_name}.db")

        # Create a cursor object.
        cursor = connection.cursor()

        try:
            # Execute the SQL query.
            cursor.execute(q, params)
            connection.commit()
            
            # Fetch results if needed.
            if is_get: return cursor.fetchall()
        finally:
            # Close the cursor and the connection.
            cursor.close()
            connection.close()

    def create_task(self, task:ETLTask):
        """
        Add multiple tasks to the list.
        @param task: Task object to be added.
        @param start_run: Date and time at which to start running
                          this task for the first time.
        @repeat_interval_sec: The time interval in seconds after
                              which this task is to be repeated.
        """
        self.query(q=f"""
            INSERT INTO etl_tasks (
                name, 
                fun_data_load, 
                fun_data_transform,
                fun_data_save, 
                repeat_time_unit,
                repeat_interval,
                status,
                num_runs
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?); 
        """, params=[
            process_value_for_db(task.name),
            process_value_for_db(task.fun_data_load),
            process_value_for_db(task.fun_data_transform),
            process_value_for_db(task.fun_data_save),
            process_value_for_db(task.repeat_time_unit),
            process_value_for_db(task.repeat_interval),
            process_value_for_db(task.status),
            process_value_for_db(task.num_runs),
        ])

    def read_task(self, name:str, fields:List[str]=[
        "name", "fun_data_load", "fun_data_transform", 
        "fun_data_save", "repeat_time_unit", "repeat_interval", 
        "time_run_last_start", "time_run_last_end", 
        "num_runs", "status"
    ]):
        """
        Returns the task in the DB with given name if it exists. 
        @param name: Name of the task.
        @param fields: Fields of data that is to be returned.
                       By default, this is all fields from the table.
        @return: List of tasks in the DB.
        """
        task_details = self.query(
            f"SELECT {','.join(fields)} FROM etl_tasks WHERE name='{name}';", 
            is_get=True
        )
        # If such a task does not exist, return -1.
        if len(task_details) == 0: return -1
        task_details = task_details[0]
        task_details = process_value_from_db(
            t=task_details, 
            fields=fields
        ) if len(task_details) > 0 else {}
        return task_details
    
    def update_task(self, new_values={}, name=None):
        """
        Updates the task in the DB having given name
        with given new values if it exists.
        @param new_values: New values that should replace old ones.
                           Keys of this dictionary are field names
                           and values are new data for these fields.
        @param name: Name of the task.
        """
        # If id has been given and a task with that id exists,
        # then return this task. Else return [].
        q = "UPDATE etl_tasks"
        updates = []
        params = []

        if len(new_values) > 0:
            q += " SET "
            for key, val in new_values.items():
                updates += [f"{key}=?"]
                params += [process_value_for_db(val)]
            q += ', '.join(updates)
        
        q += f" WHERE name='{name}'"

        if "SET" in q:
            self.query(q, params)
    
    def delete_task(self, name=None):
        """
        Removes the task from the DB with given id or name. 
        Id has preference over name. If neither are given,
        removes nothing.
        @param id: Id of the task.
        @param name: Name of the task.
        """
        # If a task with given name exists, then delete this task.
        self.query(f"DELETE FROM etl_tasks WHERE name='{name}';")

    def load_tasks(self, filters:dict={}):
        """
        Loads tasks from the DB while respecting given filter
        conditions.
        @param filters: A dictionary of filter conditions where
                        the key is the column in the DB table and
                        the value is the condition to be met.
        @return: ETLTask objects that meet the conditions.
        """
        q = "SELECT * FROM etl_tasks"
        conditions = []
        for k, v in filters.items():
            if type(v)==str: v = f"'{v}'"
            conditions.append(f"{k}={v}")
        if len(conditions) > 0:
            q = q + " WHERE " + " AND ".join(conditions)
        task_details = self.query(q=q, is_get=True)
        tasks = []
        for td in task_details:
            tasks.append(ETLTask(
                name=td[0],
                fun_data_load=dill.loads(td[1]),
                fun_data_transform=dill.loads(td[2]),
                fun_data_save=dill.loads(td[3]),
                repeat_time_unit=td[4],
                repeat_interval=td[5],
                time_run_last_start=td[6],
                time_run_last_end=td[7],
                num_runs=td[8],
                status=td[9]
            ))
        return tasks