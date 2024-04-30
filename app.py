from flask import Flask, jsonify, request
import pickle
import numpy as np
from flask_cors import CORS,cross_origin

app = Flask(__name__)
CORS(app, origins="http://localhost:5173")

# Load the pickled model
with open('model\HeartPrediction.pkl', 'rb') as file:
    model = pickle.load(file)

@app.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    data = request.get_json()

    if not data :
        return jsonify({'error': 'No data provided'}), 400
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
        return jsonify({'error': 'Missing required fields'}), 400
    
    #Convert data to a list  of lists for model prediction
    input_data = np.array([age, sex, cp, trestbps, chol, fbs, thalach]).reshape(1, -1)

    print("Input data:", input_data)  # Debug print


   # Make prediction using the model
    prediction = model.predict(input_data)

    print("Prediction:", prediction)

# Convert the prediction to a standard Python type
    prediction = prediction.tolist()

# Return the prediction as JSON
    return jsonify({'prediction': prediction})

@app.route("/")
def index():
    return "Heart Disease Prediction API running"  

if __name__ == '__main__':
    app.run(debug=True)
