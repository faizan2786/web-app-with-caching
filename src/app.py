from flask import Flask, jsonify, request
from flask.json.provider import DefaultJSONProvider
import datetime

from db import DBConnector

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
    def user_not_found(uname: str):
        return {"Error": "404", "Message": f'No User found with username \'{uname}\''}
    
    @staticmethod
    def email_not_found(email: str):
        return {"Error": "404", "Message": f'Email \'{email}\' doesn\'t exist'}

    @staticmethod
    def invalid_request_body():
        return {"Error": "400", "Message": "Invalid request body"}


app = Flask(__name__) # take the name of the app from the module name i.e. app.py
app.json = CustomJSONEncoder(app) # use custom json encode for handling dates correctly

@app.route('/')
def home():
    return "<h2>Welcome to the User API Web-Application!</h2>"

@app.route('/user/<uname>', methods=['GET'])
def get_user(uname: str):
    user = DBConnector().get_user_by_username(uname)
    if user:
        return jsonify(user), 200
    else:
        return jsonify(Errors.user_not_found(uname)), 404

@app.route('/user/email/<uname>', methods=['GET'])
def get_email(uname: str):
    val = DBConnector().get_field_by_username(uname, 'email')
    if val:
        return jsonify(val), 200
    else:
        return jsonify(Errors.user_not_found(uname)), 404

@app.route('/user/username/<email>', methods=['GET'])
def get_username_by_email(email: str) -> str:
    uname = DBConnector().get_username_by_email(email)
    if uname:
        return jsonify(uname), 200
    else:
        return jsonify(Errors.email_not_found(email)), 404

# create a PUT/POST request to update user's email
@app.route('/user/email/<uname>', methods=['PUT', 'POST'])
def update_email(uname: str):
    email = request.json.get('email') # get 'email' field from request's body of type json
    if email:
        res, msg = DBConnector().update_user_email(uname, email)
        if res:
            return jsonify({"Success": f'Email for user \'{uname}\' updated successfully'}), 200
        else:
            return jsonify(msg), 500
    else:
        return jsonify(Errors.invalid_request_body()), 400


# run the app
if __name__ == '__main__':
    app.run(debug=False) # overwrite the host and debug mode with `flask --debug run --host=0.0.0.0 port=5000` command (i.e. to run in a container with auto reload)