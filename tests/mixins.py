from json import loads
from fastapi.testclient import TestClient
from os.path import abspath, dirname, join
from main import app


class TestAuthMixin:
    @classmethod
    def setup_class(cls):
        client = TestClient(app)
        # Please create new user with the "credentials.json" info
        with open(join(dirname(abspath(__file__)), 'data', 'credentials.json'),
                  mode='r', encoding='utf-8') as f:
            example_user = loads(f.read())
            response = client.post(f"/auth/token", data={
                'grant_type': '',
                'username': example_user['email'],
                'password': example_user['password'],
                'scope': '',
                'client_id': '',
                'client_secret': ''
            }, headers={
                'accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
            })

        cls.client = client
        cls.tasks_count = None
        try:
            cls.headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
        except KeyError as e:
            raise ValueError("There is no user who have already registered with this email address.") from e
