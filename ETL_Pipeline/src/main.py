# from extract import extract
# from transform import transform
# from load import load_to_csv, load_to_db
# import os   
# from transform import DataTransformer 


# def run_etl(source_file_path, destination_path, database_uri=None, table_name=None, to_csv=True, **transform_kwargs):
#     df = extract(source_file_path)
#     df_transformed = transform(df, **transform_kwargs)
#     if to_csv:
#         load_to_csv(df_transformed, destination_path)
#         print(f"Data loaded into {destination_path}")
#     else:
#         load_to_db(df_transformed, database_uri, table_name)
#         print(f"Data loaded into database table {table_name}")

# if __name__ == "__main__":
#     # Add the logic here to decide whether to load to CSV or DB based on your needs
#     # Example call:
#     base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file_path = os.path.join(base_path, 'data', 'input', 'dublinbikes_2020_Q1.csv')
#     output_file_path = os.path.join(base_path, 'data', 'output', 'transformed_data.csv')

# transform_params = {
#     'fill_value': 0,
#     'filter_column': 'STATUS',
#     'filter_value': 'Open',
#     'normalize_columns': ['BIKE STANDS', 'AVAILABLE BIKE STANDS', 'AVAILABLE BIKES'],  # Normalize these columns
#     'encode_columns': ['STATUS'],  # One-hot encode the 'STATUS' column
#     'string_operations': {
#         'NAME': {'case': 'lower'}  # Convert 'NAME' column to lowercase
#     },
#     'feature_rules': {
#         'UTILIZATION_RATE': lambda row: row['AVAILABLE BIKES'] / row['BIKE STANDS'] if row['BIKE STANDS'] > 0 else 0,
#         # Add other feature engineering rules as needed
#     }
# }

# # Run ETL with the defined transformation parameters
# run_etl(
#     input_file_path,
#     output_file_path,
#     to_csv=True,
#     **transform_params
# )


from extract import extract
from transform import DataTransformer  # Ensure this import matches your class definition
from load import load_to_csv, load_to_db
import os

def get_user_decision(prompt):
    """Function to get a yes/no decision from the user."""
    choice = input(f"{prompt} (y/n): ").strip().lower()
    while choice not in ['y', 'n']:
        print("Please enter 'y' for yes or 'n' for no.")
        choice = input(f"{prompt} (y/n): ").strip().lower()
    return choice == 'y'



def run_etl(source_file_path, destination_path, database_uri=None, table_name=None, to_csv=True, **transform_kwargs):
    df = extract(source_file_path)
    print("Initial Data:")
    print(df.head())
    
    print("Initial Data Analysis:")
    duplicates = df.duplicated().sum()
    print(f"Duplicate rows: {duplicates}")
    null_values = df.isnull().sum().sum()
    print(f"Total null values: {null_values}")
    print(df.count())

    
    transformer = DataTransformer(df)  # Initialize the transformer with the extracted DataFrame

    
    # Ask the user if they want to remove duplicates
    if duplicates > 0 and get_user_decision("Do you want to remove duplicate rows?"):
        transformer.remove_duplicates()

    # Ask the user how they want to handle null values
    if null_values > 0:
        print("Options for handling null values:")
        print("1. Drop rows with any null values")
        print("2. Fill null values with the mean (for numerical columns)")
        choice = input("Please enter your choice (1 or 2): ").strip()
        while choice not in ['1', '2']:
            print("Invalid choice. Please enter '1' or '2'.")
            choice = input("Please enter your choice (1 or 2): ").strip()
        transformer.handle_null_values(strategy=int(choice))


    transformer.transform_data(**transform_kwargs)  # Apply transformations
    df_transformed = transformer.df  # Get the transformed DataFrame
    
    if to_csv:
        load_to_csv(df_transformed, destination_path)
        print(f"Data loaded into {destination_path}")
        print("\nTransformed Data:")
        print(transformer.df.head())
        print(transformer.df.count())

    else:
        load_to_db(df_transformed, database_uri, table_name)
        print(f"Data loaded into database table {table_name}")

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file_path = os.path.join(base_path, 'data', 'input', 'dublinbikes_2020_Q1.csv')
    output_file_path = os.path.join(base_path, 'data', 'output', 'transformed_data.csv')

    # Define transformation parameters
    transform_params = {
        'null_strategy': 2,  
        'columns_to_keep': [
        'STATION ID: int',  # Convert 'STATION ID' to integer
        'TIME',  # Keeping original data type
        'LAST UPDATED',  # Keeping original data type
        'NAME: int',
        'BIKE STANDS: int',  # Convert 'BIKE STANDS' to integer
        'AVAILABLE BIKE STANDS: int',  # Convert 'AVAILABLE BIKE STANDS' to integer
        'AVAILABLE BIKES: int',  # Convert 'AVAILABLE BIKES' to integer
        'STATUS',  # Keeping original data type
        'LATITUDE: float',  # Convert 'LATITUDE' to float
        'LONGITUDE: int'  # Convert 'LONGITUDE' to float
    ] 
    }
    
    run_etl(
        input_file_path,
        output_file_path,
        to_csv=True,
        **transform_params
    )
