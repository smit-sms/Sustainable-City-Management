import dill
import base64
from typing import Callable

class Task:
    """ A class that defines a pipeline task. """

    def __init__(self, 
        name:str='', 
        function:Callable=None,
        args:list=[],
    ):
        """ 
        Constructor. 
        @param name: Name of the task.
        @param function: Function that this task handles.
        @param args: Function arguments.
        """
        self.name = name
        self.function = function
        self.args = args

    def serialize(self):
        """ 
        Serializes this function.
        @return: Base 64 encoded byte string.
        """
        return base64.b64encode(dill.dumps(self)).decode('utf-8')
    
    def deserialize(self, serialized_str):
        """ 
        Updates this object using data provided
        as a base 64 encoded serialized byte string.
        @param serialized_str: Given serialized string.
        """
        serialized_obj = base64.b64decode(serialized_str.encode('utf-8'))
        obj = dill.loads(serialized_obj)
        self.name = obj.name
        self.function = obj.function
        self.args = obj.args

    def run(self):
        if self.function is not None:
            self.function(*self.args)