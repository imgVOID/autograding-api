import pytest
from httpx import AsyncClient
from json import loads
from fastapi.testclient import TestClient
from os.path import abspath, dirname, join
from main import app


class TestTopicsCRUDAsync:
    def test_bearer_token(self):
        client = TestClient(app)
        # Please create new user with the "credentials.json" info
        with open(join(dirname(abspath(__file__)), 'data', 'credentials.json'),
                  mode='r', encoding='utf-8') as f:
            example_user = loads(f.read())
            data = {
                'username': example_user['email'],
                'password': example_user['password'],
                'grant_type': '', 'scope': '', 'client_id': '', 'client_secret': ''
            }
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = client.post(f"/auth/token", data=data, headers=headers)

        try:
            assert response.status_code == 200
            assert isinstance(response.json()['access_token'], str)
        except (KeyError, AttributeError) as e:
            raise ValueError("There is no user who have already registered with this email address.") from e


class TestTopicsErrorsAsync:
    def test_create_user_fail(self):
        client = TestClient(app)
        data = '{\n  "email": "user@example.com",\n  "password": "string",\n  "is_root": false\n}'

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = client.post(f"/auth/users/", data=data, headers=headers)
        assert response.status_code == 400

    def test_bearer_token_fail(self):
        client = TestClient(app)
        data = {
            'username': 'test', 'password': 'test',
            'grant_type': '', 'scope': '', 'client_id': '', 'client_secret': ''
        }
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = client.post(f"/auth/token", data=data, headers=headers)

        assert response.status_code == 400
        assert response.json()['detail'] == 'There is no user who have already registered with this email address.'

