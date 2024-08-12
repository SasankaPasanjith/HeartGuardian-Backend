from flask import Flask, jsonify, request
import pickle
import numpy as np
from pymongo import MongoClient, errors
from flask_cors import CORS,cross_origin
from werkzeug.security import generate_password_hash , check_password_hash
import jwt
import datetime

app = Flask(__name__)
CORS(app, origins="http://localhost:5173")

app.config['SECRET_KEY'] = '20127'  

# Load the pickled model
with open('model\HeartPrediction.pkl', 'rb') as file:
    model = pickle.load(file)


client = MongoClient('mongodb://localhost:27017/')
db = client['heartGuardian']                         #MongoDB database
users_collection = db['users']
predictions_collection = db['predictions']
records_collection = db['records']                   #Collections

def make_response(success, message=None, data=None, error=None):
    response = {
        'success': success,
        'message': message,
        'data': data,
        'error': error
    }
    return jsonify(response)

@app.route('/register', methods=['POST'])            #User Registration function
@cross_origin()
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    mobile_number = data.get('mobile_number')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    
    if not all([username, password, confirm_password, email, mobile_number]):
        return make_response(False, error='Missing some required fields'), 400

    if password != confirm_password:
        return make_response(False, error='Passwords do not match'), 400

    existing_user = users_collection.find_one({'$or': [{'username': username}, {'email': email}]})
    if existing_user:
        return make_response(False, error='Username or email already exists'), 400

    hashed_password = generate_password_hash(password)

    user_record = {
        'username': username,
        'password': hashed_password,
        'email': email,
        'mobile_number': mobile_number
    }

    try:
        users_collection.insert_one(user_record)
    except errors.PyMongoError as e:
        return make_response(False, error=str(e)), 500

    token = jwt.encode({
        'email': email,
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token valid for 1 hour
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return make_response(True, message='The user successfully registered.', data={'token': token}), 201


@app.route('/login', methods=['POST'])             #User Login function
@cross_origin()
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return make_response(False, error='Missing some required fields'), 400

    user = users_collection.find_one({'email':email})

    if user and check_password_hash(user['password'], password):
        token = jwt.encode({
            'email': email,
            'username': user['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)   # Token valid for 1 hour
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return make_response(True, message='The user successfully logged in.', data={
            'token': token,
            'email': email,
            'username': user['username']
        }), 200
    else:
        return make_response(False, error='Invalid email or password'), 401


@app.route('/predict', methods=['POST'])          #Disease prediction function
@cross_origin()
def predict():

    token = request.headers.get('Authorization')
    user = None
    if token:
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user = users_collection.find_one({'email': data['email']})
        except jwt.ExpiredSignatureError:
            return make_response(False, error='Token has expired'), 401
        except jwt.InvalidTokenError:
            return make_response(False, error='Invalid token'), 403
        except Exception as e:
            return make_response(False, error=str(e)), 500

    data = request.get_json()

    if not data :
        return make_response(False, error='No data provided'), 400
    
    # Get the input data from the form
    age = data.get('age')
    sex = data.get('sex')
    cp = data.get('cp')
    trestbps = data.get('trestbps')
    chol = data.get('chol')
    fbs = data.get('fbs')
    thalach = data.get('thalach')

    # Check if all required fields are present
    if not all([age, sex, cp, trestbps, chol, fbs, thalach]):
        return make_response(False, error='Missing required fields'), 400
    
    #Convert data to a list  of lists for model prediction
    input_data = np.array([age, sex, cp, trestbps, chol, fbs, thalach]).reshape(1, -1)

    try:
        prediction = model.predict(input_data)      # Make prediction using the model
    except Exception as e:
        return make_response(False, error=str(e)), 500

# Convert the prediction to a standard Python type
    prediction = prediction.tolist()

 # Store prediction in to the prediction collection in DB
    prediction_record = {
        'age': age,
        'sex': sex,
        'cp': cp,
        'trestbps': trestbps,
        'chol': chol,
        'fbs': fbs,
        'thalach': thalach,
        'prediction': prediction,
        'username': user['username'] if user else None,  #Add username if user authenticated
        'email': user['email'] if user else None         #Add email if user authenticated
    }

    try:
        predictions_collection.insert_one(prediction_record)     #Handle DB errors
        if user:
            records_collection.insert_one(prediction_record)
    except errors.PyMongoError as e:
        return make_response(False, error=str(e)), 500
    
# Return the prediction as JSON
    return make_response(True, data={'prediction': prediction}), 200


@app.route('/predictions', methods=['GET'])     #Get all past predictions function
@cross_origin()
def get_predictions():
    token = request.headers.get('Authorization')
    if not token:
        return make_response(False, error='The token is missing.'), 403

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return make_response(False, error='The token has expired.'), 403
    except jwt.InvalidTokenError:
        return make_response(False, error='The token is invalid.'), 403
    
    user = users_collection.find_one({'email': data['email']})
    if not user:
        return make_response(False, error='User not found'), 404
    
    try:
        predictions = list(predictions_collection.find({'email': user['email']}))
    except errors.PyMongoError as e:
        return make_response(False, error=str(e)), 500
    
    for prediction in predictions:
        prediction['_id'] = str(prediction['_id'])
        
    return make_response(True, data={'predictions': predictions}), 200

@app.route("/")
def index():
    return "Heart Disease Prediction API running"  #Display message

if __name__ == '__main__':
    app.run(debug=True)