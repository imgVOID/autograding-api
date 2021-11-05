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
                'username': example_user['email'], 'password': example_user['password'],
            })
        cls.client = client
        cls.tasks_count = None
        cls.headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
