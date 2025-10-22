import pytest
import json
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_predict_valid_input(client):
    data = {
        'nitrogen': 90,
        'phosphorus': 42,
        'potassium': 43,
        'temperature': 20.87,
        'humidity': 82.00,
        'ph': 6.50,
        'rainfall': 202.93
    }
    response = client.post('/predict',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 200
    assert 'predicted_crop' in response.json

def test_predict_invalid_input(client):
    data = {
        'nitrogen': -10,  # Invalid: negative value
        'phosphorus': 42,
        'potassium': 43,
        'temperature': 20.87,
        'humidity': 150,  # Invalid: >100
        'ph': 6.50,
        'rainfall': 202.93
    }
    response = client.post('/predict',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 400