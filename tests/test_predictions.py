import pytest
import sys
import jwt
import datetime
from pymongo import MongoClient, errors
from unittest.mock import patch

sys.path.insert(0, 'E:/FInal Project Proposal/heartguardian backend')
from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = '20127'
    
    # Use a test MongoDB database
    flask_app.config['MONGO_URI'] = 'mongodb://localhost:27017/heartGuardian_test'
    with flask_app.app_context():
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def clean_db():
    client = MongoClient('mongodb://localhost:27017/')
    client.drop_database('heartGuardian_test')
    yield

def test_get_prediction_as_guest(client):
    response = client.post('/predict', json={
        'age': 47,
        'sex': 1,
        'cp': 2,
        'trestbps': 130,
        'chol': 350,
        'fbs': 1,
        'thalach': 120
    })
    assert response.status_code == 200
    assert response.json['success'] == True


def test_get_prediction_missing_values(client):
    response = client.post('/predict', json={
        'age': 29,
        'sex': 1,
        'cp': 0,
        'trestbps': 130,
        'chol': 250
        # Missing 'fbs' and 'thalach'
    })
    assert response.status_code == 400
    assert response.json['success'] == False
    assert 'Missing required fields' in response.json['error']


def test_get_prediction_no_values(client):
    response = client.post('/predict', json={})
    assert response.status_code == 400
    assert response.json['success'] == False


def test_expired_token(client):
    # Create an expired token
    expired_token = jwt.encode({
        'email': 'testuser@example.com',
        'username': 'testuser',
        'exp': datetime.datetime.utcnow() - datetime.timedelta(hours=1)  # Token expired 1 hour ago
    }, flask_app.config['SECRET_KEY'], algorithm='HS256')

    response = client.post('/predict', json={
        'age': 29,
        'sex': 1,
        'cp': 0,
        'trestbps': 130,
        'chol': 250,
        'fbs': 1,
        'thalach': 170
    }, headers={'Authorization': f'Bearer {expired_token}'})
    
    assert response.status_code == 401
    assert response.json['success'] == False
    assert response.json['error'] == 'Token has expired'


def test_invalid_token(client):
    invalid_token = "ThisIsAnInvalidToken"

    response = client.post('/predict', json={
        'age': 29,
        'sex': 1,
        'cp': 0,
        'trestbps': 130,
        'chol': 250,
        'fbs': 1,
        'thalach': 170
    }, headers={'Authorization': f'Bearer {invalid_token}'})
    
    assert response.status_code == 403, f"Unexpected response: {response.json}" 
    assert response.json['success'] == False
    assert response.json['error'] == 'Invalid token'