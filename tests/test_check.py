import pytest
from httpx import AsyncClient
from .mixins import TestAuthMixin
from os import path
from sys import path as sys_path
from main import app


class TestCheck(TestAuthMixin):
    sys_path.insert(0, path.join(path.dirname(__file__), '..'))

    @pytest.mark.asyncio
    async def test_check_not_found(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response_topic = await ac.post(
                "api/checks/999/999", files={'file': b""}, headers=self.headers
            )
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response_task = await ac.post(
                "api/checks/0/999", files={'file': b""}, headers=self.headers
            )
        assert response_topic.status_code == 404
        assert response_task.status_code == 404
        assert response_topic.json() == {'detail': 'Topic not found by ID'}
        assert response_task.json() == {'detail': 'Task not found by ID'}

    @pytest.mark.asyncio
    async def test_check_answer(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Please write this content: "Hello, World!'
            # in the output file materials/0_test/output/task_1.txt
            answer_true = await ac.post(
                f"api/checks/0/1", files={'file': b"print(input())"}, headers=self.headers
            )
            answer_true_status = answer_true.status_code
            answer_true = tuple(answer_true.json().values())

        async with AsyncClient(app=app, base_url="http://test") as ac:
            answer_false = await ac.post(
                f"api/checks/0/1", files={'file': b'print("Fail!")'}, headers=self.headers
            )
            answer_false_status = answer_false.status_code
            answer_false = tuple(answer_false.json().values())

        assert all([answer_true_status == 200, answer_false_status == 200])

        assert answer_true == ('Hello, World!', 'Hello, World!', 'OK')
        assert answer_false == ('Hello, World!', 'Fail!', 'WRONG')

    @pytest.mark.asyncio
    async def test_check_answer_limit(self):
        # Please check that route's rate limit set to 2 requests per minute
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                f"api/checks/0/1", files={'file': b'print("OK")'}, headers=self.headers
            )
        assert response.status_code == 429
        assert response.json() == {'error': 'Rate limit exceeded: 2 per 1 minute'}
