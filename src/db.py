# helper class for database methods

from typing import Tuple
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

    # update the key (NOT the value) in redis
    def update_key_if_exist(self, key: str, new_key: str) -> bool:
        if self.connection.exists(key):
            val = self.connection.get(key) # get the value
            self.connection.delete(key)  # delete current key
            self.connection.set(new_key, val) # add value with new key
            return True
        return False

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
        # save the info to the cache if valid value is retrieved
        if uname:
            RedisConnector().connection.set(key, uname[0])
        return uname
    
    # update user's email by its username
    # (also updates the email in cache if it exists)
    # returns the True if update is successful and the error message if failed.
    def update_user_email(self, uname: str, email: str) -> Tuple[bool, str]:
        uname = uname.lower()
        email = email.lower()
        current_email = self.get_field_by_username(uname, 'email')[0]

        # return if provided email is same as current one
        if current_email.lower() == email:
            return (True, "OK")

        # update the email in DB
        cursor = self.connection.execute(f'UPDATE Users SET email = \'{email}\' WHERE username = \'{uname}\'')

        if cursor.rowcount == 1: # if the update is successful
            # commit the change
            self.connection.commit()
            cursor.close()

            # update the cache for given email
            current_key = f"user_name:{current_email}"
            new_key = f"user_name:{email}"
            RedisConnector().update_key_if_exist(current_key, new_key)
            
            return (True, "OK")
        else:
            self.connection.rollback()
            cursor.close()
            return (False, "Something went wrong while updating record in the DB!")
