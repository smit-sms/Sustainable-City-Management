from datetime import datetime, timedelta

def datetime_to_unix_timestamp(dt: datetime):
    '''
    Function to convert the datetime to unix timestamp
    '''
    return int(dt.timestamp())

def unix_timestamp_to_datetime(timestamp: int) -> datetime:
    '''
    Function to convert a Unix timestamp back into a datetime object.
    '''
    return datetime.fromtimestamp(timestamp)
