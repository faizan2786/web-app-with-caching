# helper class for database methods

import psycopg # postgres SQL api
import redis # redis api

import os
from yaml import load, Loader

# load config from the yaml file
def get_db_config():
    with open("config.yaml", "r") as f:
        return load(f, Loader=Loader)['db']

def get_redis_config():
    with open("config.yaml", "r") as f:
        return load(f, Loader=Loader)['redis']

class SingletonClass(type):
    _instances = {} # dict of class type to it singleton instance
    def __call__(self):
        if self not in self._instances:
            self._instances[self] = super().__call__()
        return self._instances[self]

# Singleton connector to Redis server
class RedisConnector(metaclass = SingletonClass):
    def __init__(self):
        redis_config = get_redis_config()
        self.host = redis_config['host_name']
        self.port = redis_config['port']
        # connect to redis
        self.connection = redis.Redis(self.host, self.port, decode_responses=True)  # redis connection instance

# Singleton connector to the DB
class DBConnector(metaclass = SingletonClass): # derive from the Singleton type class
    def __init__(self) -> None:       
        # Database configuration
        db_config = get_db_config()
        self.db_host = db_config['host_name']
        self.db_port = db_config['port']
        self.db_name = db_config['db_name']

        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")

        # throw if required env variable are not set
        if None in (self.db_user, self.db_password):
            raise RuntimeError("DB user and/or password not set by environment variables.")

        # Connect to PostgreSQL
        self.connection = psycopg.connect(
            host = self.db_host,
            port = self.db_port,
            dbname = self.db_name,
            user = self.db_user,
            password = self.db_password
        )

    # get user by its id from the Postgres database
    def get_user_by_username(self, uname: str, skip_nulls=True):
        # Query data from PostgreSQL
        cursor = self.connection.execute(f'SELECT * FROM Users WHERE username = \'{uname}\';')
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

    # get any user field by id
    def get_field_by_username(self, uname: str, field_name: str):
        # get the data from the db
        cursor = self.connection.cursor()
        cursor.execute(f'SELECT {field_name} FROM Users WHERE username = \'{uname}\'')
        value = cursor.fetchone()
        cursor.close()
        return value

    # get user's username by their email
    # (can be used to support login by user's emails)
    def get_username_by_email(self, email: str) -> str:
        
        # first, retrieve the username from the redis cache 
        # (i.e. key = username:<email>, value = user_name of the user with given email)
        key = f"user_name:{email}"
        uname = RedisConnector().connection.get(key)
        if uname:
            return uname

        # get the data from db
        cursor = self.connection.execute(f'SELECT username FROM Users WHERE email = \'{email}\'')
        uname = cursor.fetchone()
        cursor.close()

        # save the mapping to the cache if valid value is retrieved
        if uname:
            RedisConnector().connection.set(key, uname[0])

        return uname
