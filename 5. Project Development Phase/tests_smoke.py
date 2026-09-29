from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_health():
    r=client.get('/health')
    assert r.status_code==200
    assert r.json()['status']=='ok'

def test_pages():
    for path in ['/', '/login', '/register', '/dashboard', '/planner/home','/planner/party','/planner/jewelry','/history']:
        assert client.get(path).status_code==200
