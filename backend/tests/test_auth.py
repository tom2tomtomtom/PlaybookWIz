from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_login_success():
    payload = {"email": "demo@playbookwiz.com", "password": "demo123"}
    response = client.post('/api/v1/auth/login', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['access_token'] == 'demo-token-123'
    assert data['token_type'] == 'bearer'


def test_login_failure():
    payload = {"email": "wrong@example.com", "password": "bad"}
    response = client.post('/api/v1/auth/login', json=payload)
    assert response.status_code == 401

