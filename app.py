from flask import Flask, jsonify
import psycopg2 # postgres SQL api
import os

from flask.json.provider import DefaultJSONProvider
import datetime

# Database configuration
db_host = "localhost"
db_port = "5432"  # Default PostgreSQL port
db_name = "webapp_db"
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

db_table_name = "users"

if None in (db_user, db_password):
    raise RuntimeError("DB user and/or password not set by environment variables.")

def get_db_connection():
    # Connect to PostgreSQL
    connection = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password = db_password
    )

    return connection

# get user by its id from the Postgres database
def get_user_by_id(id: int, skip_nulls=True):

    # Query data from PostgreSQL
    cursor = get_db_connection().cursor()
    cursor.execute(f'SELECT * FROM {db_table_name} WHERE id = {id};')
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
def get_field_by_id(id: int, field_name: str):
    cursor = get_db_connection().cursor()
    cursor.execute(f'SELECT {field_name} FROM {db_table_name} WHERE id = {id}')
    result = cursor.fetchone()
    cursor.close()
    return result

# define custom json encoder 
# (this is required to prevent the jsonify from automatically
# converting the date objects to a datetime strings)
class CustomJSONEncoder(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')  # Format date as string
        return super().default(obj)

class Errors():
    @staticmethod
    def user_not_found(id: int):
        return {"Error": "404", "Message": f'No User found with id {id}'}

app = Flask(__name__) # take the name of the app from the module name i.e. app.py

@app.route('/user/<int:id>', methods=['GET'])
def get_user(id: int):
    user = get_user_by_id(id)
    if user:
        return jsonify(user), 200
    else:
        return jsonify(Errors.user_not_found(id)), 404

@app.route('/user/email/<int:id>', methods=['GET'])
def get_email(id: int):
    val = get_field_by_id(id, 'email')
    if val:
        return jsonify(val), 200
    else:
        return jsonify(Errors.user_not_found(id)), 404

# run the app
if __name__ == '__main__':
    app.json = CustomJSONEncoder(app) # use custom json encode for handling dates correctly
    app.run(debug=False)