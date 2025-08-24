import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_endpoint(client):
    """Test the home endpoint returns 200 and contains expected content"""
    rv = client.get('/')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'message' in data
    assert 'CI/CD!' in data['message']

def test_health_endpoint(client):
    """Test the health endpoint"""
    rv = client.get('/health')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'healthy'

def test_ready_endpoint(client):
    """Test the readiness endpoint"""
    rv = client.get('/ready')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'ready'

def test_version_endpoint(client):
    """Test the version endpoint"""
    rv = client.get('/version')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'version' in data
    assert 'build_date' in data
    assert 'git_commit' in data
