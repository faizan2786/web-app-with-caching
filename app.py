from flask import Flask, jsonify

# in-memory database (in json format) to mimic db data
database = {
    1 : {"id": 1, "name": "Faizan Patel", "Age": "30" },
    2 : {"id": 2, "name": "John Doe", "Age": "42" }
}

class Errors():
    @staticmethod
    def user_not_found(id: int):
        return {"Error": "404", "Message": f'No User found with id {id}'}

app = Flask(__name__) # take the name of the app from the module name i.e. app.py

@app.route("/user/<int:id>")
def get_user(id: int):
    user = database.get(id, None)
    if user:
        return jsonify(user)
    else:
        return jsonify(Errors.user_not_found(id))
    
# run the app
if __name__ == '__main__':
    app.run(debug=True)