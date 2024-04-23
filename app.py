from flask import Flask, jsonify
from flask.json.provider import DefaultJSONProvider
import datetime

from db import DBHelper

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
    user = DBHelper().get_user_by_id(id)
    if user:
        return jsonify(user), 200
    else:
        return jsonify(Errors.user_not_found(id)), 404

@app.route('/user/email/<int:id>', methods=['GET'])
def get_email(id: int):
    val = DBHelper().get_field_by_id(id, 'email')
    if val:
        return jsonify(val), 200
    else:
        return jsonify(Errors.user_not_found(id)), 404

# run the app
if __name__ == '__main__':
    app.json = CustomJSONEncoder(app) # use custom json encode for handling dates correctly
    app.run(debug=False)