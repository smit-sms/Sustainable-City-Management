from sqlalchemy import create_engine

def load_to_csv(df, file_path):
    """Loads the DataFrame into a CSV file."""
    df.to_csv(file_path, index=False)

def load_to_db(df, database_uri, table_name, if_exists='replace'):
    """Loads the DataFrame into a database."""
    engine = create_engine(database_uri)
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
