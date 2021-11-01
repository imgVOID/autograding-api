import pytest
from httpx import AsyncClient
from main import app


class TestCheck:
    @pytest.mark.asyncio
    async def test_check_not_found(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response_theme = await ac.post(f"api/check/999/999", files={
                'file': b""
            })
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response_task = await ac.post(f"api/check/0/999", files={
                'file': b""
            })
        assert response_theme.status_code == 404
        assert response_task.status_code == 404
        assert response_theme.json() == {'detail': 'Theme not found by ID'}
        assert response_task.json() == {'detail': 'Task not found by ID'}

    @pytest.mark.asyncio
    async def test_check_answer(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Please write this content: "Hello, World!'
            # in the output file materials/0_test/output/task_1.txt
            answer_true = await ac.post(f"api/check/0/1", files={
                'file': b"print(input())"
            })
        async with AsyncClient(app=app, base_url="http://test") as ac:
            answer_false = await ac.post(f"api/check/0/1", files={
                'file': b'print("Fail!")'
            })
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
            response = await ac.post(f"api/check/0/1", files={
                'file': b'print("OK")'
            })
        assert response.status_code == 429
        assert response.json() == {'error': 'Rate limit exceeded: 2 per 1 minute'}
