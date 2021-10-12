import pytest
from httpx import AsyncClient
from main import app
from utilities.test_scripts import get_simple_code


@pytest.mark.asyncio
async def test_check_not_found():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"api/check/999/999", files={
            'file': await get_simple_code()
        })
    assert response.status_code == 404
    assert response.json() == {'message': 'Task not found'}


@pytest.mark.asyncio
async def test_check_answer_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Please write this content: "OK\nOK\nOK'
        # in the output file materials/0_test/output/task_1.txt
        response = await ac.post(f"api/check/0/1", files={
            'file': await get_simple_code()
        })
    assert response.status_code == 200
    assert response.json() == {'answer': 'OK\nOK\nOK',
                               'status': 'OK',
                               'your_result': 'OKOKOK'}


@pytest.mark.asyncio
async def test_check_answer_fail():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Please write this content: "OK\nOK\nOK'
        # in the output file materials/0_test/output/task_1.txt
        response = await ac.post(f"api/check/0/1", files={
            'file': b'print("OK")'
        })
    assert response.status_code == 200
    assert response.json() == {'answer': 'OK\nOK\nOK',
                               'status': 'WRONG',
                               'your_result': 'OK'}
