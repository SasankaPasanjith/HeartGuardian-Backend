import pytest
import sys
sys.path.insert(0, 'D:\Final project\heartguardian backend')
from flask import Flask
from pymongo import MongoClient
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