### This files contains functions that all other files use.

import dill
import base64

def base64encode_obj(obj):
    """
    Retruns this object as a base 64 encoded byte string.
    @param obj: Object to encode.
    @return: Base 64 encoded byte string.
    """
    return base64.b64encode(dill.dumps(obj)).decode('utf-8')

def base64decode_obj(base64str:str):
    """
    Deserializes base 64 encoded byte string.
    @param base64str: Base 64 encoded byte string.
    @return: Object that was encoded in the given string.
    """
    return dill.loads((base64.b64decode(base64str.encode('utf-8'))))