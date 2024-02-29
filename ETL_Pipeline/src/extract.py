import pandas as pd

def extract(file_path):
    """Extracts data from a CSV file into a pandas DataFrame."""
    return pd.read_csv(file_path)
