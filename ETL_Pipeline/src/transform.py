

# import pandas as pd
# import numpy as np

# class DataTransformer:
#     def __init__(self, dataframe):
#         self.df = dataframe

#     def handle_null_values(self, strategy=0):
#         """
#         Handle null values based on the strategy.
#         0: Do nothing
#         1: Drop rows with any null values
#         2: Fill null values with the mean of the column (for numerical columns only)
#         """
#         if strategy == 1:
#             print(f"Rows with null values before drop: {self.df.isnull().any(axis=1).sum()}")
#             self.df.dropna(inplace=True)
#             print("Rows with null values dropped.")
#         elif strategy == 2:
#             numerical_cols = self.df.select_dtypes(include=np.number).columns
#             for col in numerical_cols:
#                 self.df[col].fillna(self.df[col].mean(), inplace=True)
#             print("Null values filled with column mean for numerical columns.")
#         elif strategy == 0:
#             print("No Null Values.")

#     def remove_duplicates(self):
#         """
#         Remove duplicate rows and print the number of duplicates removed.
#         """
#         duplicates = self.df.duplicated().sum()
#         if duplicates:
#             self.df.drop_duplicates(inplace=True)
#             print(f"{duplicates} duplicate rows removed.")
#         else:
#             print("No duplicate rows found.")

#     def filter_columns(self, columns_to_keep=None):
#         """
#         Keep only the specified columns. If no columns are specified, keep all.
#         """
#         if columns_to_keep:
#             self.df = self.df[columns_to_keep]

#     def transform_data(self, null_strategy=0, columns_to_keep=None):
#         """
#         Apply transformations: handle nulls, remove duplicates, and filter columns.
#         """
#         self.handle_null_values(strategy=null_strategy)
#         self.remove_duplicates()
#         if columns_to_keep is not None:
#             self.filter_columns(columns_to_keep=columns_to_keep)



import pandas as pd
import numpy as np

class DataTransformer:
    def __init__(self, dataframe):
        self.df = dataframe

    def handle_null_values(self, strategy=0):
        """
        Handle null values based on the strategy.
        0: Do nothing
        1: Drop rows with any null values
        2: Fill null values with the mean of the column (for numerical columns only)
        """
        if strategy == 1:
            print(f"Rows with null values before drop: {self.df.isnull().any(axis=1).sum()}")
            self.df.dropna(inplace=True)
            print("Rows with null values dropped.")
        elif strategy == 2:
            numerical_cols = self.df.select_dtypes(include=np.number).columns
            for col in numerical_cols:
                self.df[col].fillna(self.df[col].mean(), inplace=True)
            print("Null values filled with column mean for numerical columns.")
        elif strategy == 0:
            print("No Null Values.")

    def remove_duplicates(self):
        """
        Remove duplicate rows and print the number of duplicates removed.
        """
        duplicates = self.df.duplicated().sum()
        if duplicates:
            self.df.drop_duplicates(inplace=True)
            print(f"{duplicates} duplicate rows removed.")
        else:
            print("No duplicate rows found.")


    def convert_data_types(self, columns_with_types):
        """
        Convert data types of specified columns.
        `columns_with_types` should be a dict with column names as keys and target data types as values.
        Attempts to convert each specified column to its new data type,
        catching and reporting any errors due to incompatible type conversions.
        """
        for col, new_type in columns_with_types.items():
                try:
                    self.df.loc[:, col] = self.df[col].astype(new_type)
                except ValueError as e:
                    print(f"Sorry, irrelevant type conversion cannot convert '{col}' to {new_type}. Error: {e}")    

    def filter_columns(self, columns_to_keep=None):
        """
        Keep only the specified columns and convert their data types if specified.
        If no columns are specified, keep all.
        """
        if columns_to_keep:
            columns_with_types = {}
            columns_only = []

            for col in columns_to_keep:
                if ':' in col:
                    col_name, col_type = col.split(':')
                    columns_with_types[col_name.strip()] = col_type.strip()
                    columns_only.append(col_name.strip())
                else:
                    columns_only.append(col.strip())

            missing_cols = set(columns_only) - set(self.df.columns)
            if missing_cols:
                print(f"Warning: The following columns were not found in the DataFrame and will be ignored: {', '.join(missing_cols)}")

            self.df = self.df[[col for col in columns_only if col in self.df.columns]]
            if columns_with_types:
                self.convert_data_types(columns_with_types)

    def transform_data(self, null_strategy=0, columns_to_keep=None):
        """
        Apply transformations: handle nulls, remove duplicates, and filter columns.
        """
        self.handle_null_values(strategy=null_strategy)
        self.remove_duplicates()
        if columns_to_keep is not None:
            self.filter_columns(columns_to_keep=columns_to_keep)