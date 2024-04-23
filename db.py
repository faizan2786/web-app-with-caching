# helper class for database methods

import psycopg2 # postgres SQL api
import os

class DBHelper:
    def __init__(self) -> None:
        # Database configuration
        self.db_host = "localhost"
        self.db_port = "5432"  # Default PostgreSQL port
        self.db_name = "webapp_db"
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.connection = None

        # throw if required env variable are not set
        if None in (self.db_user, self.db_password):
            raise RuntimeError("DB user and/or password not set by environment variables.")

    # initialise db connection object
    def __get_db_connection(self):
        if not self.connection:
            # Connect to PostgreSQL
            self.connection = psycopg2.connect(
                host = self.db_host,
                port = self.db_port,
                dbname = self.db_name,
                user = self.db_user,
                password = self.db_password
            )
        return self.connection

    # get user by its id from the Postgres database
    def get_user_by_id(self, id: int, skip_nulls=True):
        # Query data from PostgreSQL
        cursor = self.__get_db_connection().cursor()
        cursor.execute(f'SELECT * FROM Users WHERE id = {id};')
        result = cursor.fetchone()

        if not result:
            return None

        user = {} # prepare user object with their column labels
        for col, val in zip(cursor.description, result):
            if skip_nulls and val is None: # skip the null values if the option is set
                continue
            user[col[0]] = val

        cursor.close()
        return user

    # get user's email by id
    def get_field_by_id(self, id: int, field_name: str):
        cursor = self.__get_db_connection().cursor()
        cursor.execute(f'SELECT {field_name} FROM Users WHERE id = {id}')
        result = cursor.fetchone()
        cursor.close()
        return result