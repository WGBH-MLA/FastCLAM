from fastapi.testclient import TestClient
from fastclam.app import app

client = TestClient(app)


def test_get_home():
    """GET / returns a {'FastCLAM': 'semantic.version.number'} response"""
    response = client.get('/')
    assert response.status_code == 200, 'Home page did not return sucessfully'
    assert 'application/json' in response.headers['content-type'], 'Type is not JSON'
    assert response.json()['FastCLAM'].find('.'), 'No FastCLAM version number found'
