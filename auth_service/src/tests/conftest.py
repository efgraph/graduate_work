import pytest

from app import app


@pytest.fixture(scope='module')
def test_client():
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

@pytest.fixture(scope='module')
def tokens(test_client):
    test_client.post('/v1/auth/register',
                     query_string={'login': 'user', 'password': '12345', 'email': 'admin@admin.com'})
    response = test_client.post('/v1/auth/login',
                                query_string={'login': 'user', 'password': '12345'})
    yield response.get_json()['access_token'], response.get_json()['refresh_token']


@pytest.fixture(scope='module')
def admin_tokens(test_client):
    response = test_client.post('/v1/auth/login',
                                query_string={'login': 'admin', 'password': 'admin'})
    yield response.get_json()['access_token'], response.get_json()['refresh_token']
