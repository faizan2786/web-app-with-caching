# helper class for database methods

import psycopg2 # postgres SQL api
import redis # redis api
import os

import redis.connection

class SingletonClass(type):
    _instances = {} # dict of class type to it singleton instance
    def __call__(self):
        if self not in self._instances:
            self._instances[self] = super().__call__()
        return self._instances[self]

# Singleton connector to the DB
class DBConnector(metaclass = SingletonClass): # derive from the Singleton type class
    def __init__(self) -> None:       
        # Database configuration
        self.db_host = "user-api-db" # db server's name (i.e. container name)
        self.db_port = "5432"  # Default PostgreSQL port
        self.db_name = "user_db"
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")

        # throw if required env variable are not set
        if None in (self.db_user, self.db_password):
            raise RuntimeError("DB user and/or password not set by environment variables.")

        # Connect to PostgreSQL
        self.connection = psycopg2.connect(
            host = self.db_host,
            port = self.db_port,
            dbname = self.db_name,
            user = self.db_user,
            password = self.db_password
        )

    # get user by its id from the Postgres database
    def get_user_by_id(self, id: int, skip_nulls=True):
        # Query data from PostgreSQL
        cursor = self.connection.cursor()
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

        # retrieve the field value from the redis cache (i.e. key = user_email:id, value = email of the user with id)
        key = f"user_{field_name}:{id}"
        value = RedisConnector().connection.get(key)
        if value:
            return value

        # get the data from the db
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT {field_name} FROM Users WHERE id = {id}')
        value = cursor.fetchone()
        cursor.close()

        # store the email in cache for future reference
        RedisConnector().connection.set(key, value[0])
        return value


# Singleton connector to Redis server
class RedisConnector(metaclass = SingletonClass):
    def __init__(self):
        self.host = "redis-stack"
        self.port = 6379
        # connect to redis
        self.connection = redis.Redis(self.host, self.port, decode_responses=True)