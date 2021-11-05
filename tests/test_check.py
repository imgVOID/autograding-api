import pytest
from httpx import AsyncClient
from main import app
from .mixins import TestAuthMixin


class TestCheck(TestAuthMixin):
    @pytest.mark.asyncio
    async def test_check_not_found(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response_topic = await ac.post(
                f"api/checks/999/999", files={'file': b""}, headers=self.headers
            )
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response_task = await ac.post(
                f"api/checks/0/999", files={'file': b""}, headers=self.headers
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
        async with AsyncClient(app=app, base_url="http://test") as ac:
            answer_false = await ac.post(
                f"api/checks/0/1", files={'file': b'print("Fail!")'}, headers=self.headers
            )
        assert all([answer_true.status_code == 200, answer_false.status_code == 200])
        assert answer_true.json() == {
            'answer': 'Hello, World!', 'status': 'OK', 'your_result': 'Hello, World!'
        }
        assert answer_false.json() == {
            'answer': 'Hello, World!', 'status': 'WRONG', 'your_result': 'Fail!'
        }

    @pytest.mark.asyncio
    async def test_check_answer_limit(self):
        # Please check that route's rate limit set to 2 requests per minute
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                f"api/checks/0/1", files={'file': b'print("OK")'}, headers=self.headers
            )
        assert response.status_code == 429
        assert response.json() == {'error': 'Rate limit exceeded: 2 per 1 minute'}
