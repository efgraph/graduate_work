from http import HTTPStatus


def test_register(test_client):
    response = test_client.post('/v1/auth/register',
                                query_string={'login': 'user', 'password': '12345', 'email': 'user@admin.com'})
    assert response.status_code == HTTPStatus.OK
    assert b'Account created' in response.data


def test_login(test_client):
    response = test_client.post('/v1/auth/login',
                                query_string={'login': 'user', 'password': '12345'})
    assert response.status_code == HTTPStatus.OK
    assert b'access_token' in response.data
    assert b'refresh_token' in response.data


def test_history(test_client, tokens):
    response = test_client.get('/v1/auth/login-history', query_string={'jwt': tokens[0], 'page_size': 10, 'page_number': 0})
    assert response.status_code == HTTPStatus.OK


def test_edit(test_client, tokens):
    response = test_client.post('/v1/auth/edit-user', query_string={'jwt': tokens[0]},
                                data=dict(email='superuser@admin.com'))
    assert response.status_code == HTTPStatus.OK


def test_refresh_token(test_client, tokens):
    response = test_client.post('/v1/auth/refresh-token', query_string={'jwt': tokens[1]})
    assert response.status_code == HTTPStatus.OK
    assert response.get_json()['refresh_token'] != tokens[1]


def test_logout(test_client, tokens):
    access_token, refresh_token = tokens
    response = test_client.get('/v1/auth/logout', headers={'Access-Token': access_token, 'Refresh-Token': refresh_token})
    assert response.status_code == HTTPStatus.OK
