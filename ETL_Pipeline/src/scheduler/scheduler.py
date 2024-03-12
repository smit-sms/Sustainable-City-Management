import sqlite3

# Set up a database where all scheduled tasks will be stored.
class Scheduler:
    """
    A scheduler that leverages a SQLite database to plan and
    execute tasks.
    """

    def __init__(self, 
        name_db:str,
        path_db:str='.'
    ):
        """ 
        Constructor.
        @param name_db: Name of associated database.
        @param path_db: Path at which to store db.
        """

        # Check DB availability.
        self.name_db = name_db
        self.path_db = path_db
        self.__create_db()

    def __create_db(self):
        """
        Connects to the SQLlite DB that maintains state of all data pipeline tasks.
        If such a DB does not exist, it is created with desied tables added to it.
        """
        # Create necessary table(s) if it does not already exist.
        # A `tasks` table consisting of: 
        # 1. An automatically generated `id` column which shall contain 
        #    integers and be the unique primary key.
        # 2. A `name` column that shall contain a strings and cannot be empty.
        # 3. A `function` column that shall contain bytes and cannot be empty.
        # 4. A `repeat-interval-sec` column that shall contain integers 
        #    and cannot be empty.
        # 5. A `next-run` column that shall contain a date time or be empty.
        # 6. A `last-run` column that shall contain a date time or be empty.
        # 7. A `first-run` columns that shall contain a date time or be empty.
        self.query(q='''CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            function TEXT NOT NULL,
            repeat_interval_sec INTEGER NOT NULL,
            next_run DATETIME,
            last_run DATETIME,
            first_run DATETIME NOT NULL
        )''')
        print(f"Database '{self.path_db}/{self.name_db}.db' available.")

    def query(self, q, is_get:bool=False):
        """ 
        Execute a SQL query.
        @param q: Query to execute.
        @param is_get: Whether query result is returnable.
        @return: All results.
        """
        try:
            # Connect to the SQLite database.
            connection = sqlite3.connect(f"{self.path_db}/{self.name_db}.db")

            # Create a cursor object.
            cursor = connection.cursor()

            # Execute the SQL query.
            cursor.execute(q)

            # Fetch results if needed.
            if is_get:
                results = cursor.fetchall()

            # Close the cursor and the connection
            cursor.close()
            connection.close()
            
            # Returns results if needed.
            if is_get:
                return results

        except Exception as e:
            print(f'Failed to execute query "{q}": "{e}".')