import pytest
from httpx import AsyncClient
from main import app


async def get_simple_code():
    simple_code = b'print("OK")\nprint("OK")\nprint("OK")\n'
    return simple_code


@pytest.mark.asyncio
async def test_check_theme_not_found():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"api/check/999/999", files={
            'file': b""
        })
    assert response.status_code == 404
    assert response.json() == {'message': 'Theme not found'}


@pytest.mark.asyncio
async def test_check_task_not_found():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"api/check/0/999", files={
            'file': b""
        })
    assert response.status_code == 404
    assert response.json() == {'message': 'Task not found'}


@pytest.mark.asyncio
async def test_check_answer_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Please write this content: "OK\nOK\nOK'
        # in the output file materials/0_test/output/task_1.txt
        response = await ac.post(f"api/check/0/1", files={
            'file': b"print(input())"
        })
    assert response.status_code == 200
    assert response.json() == {'answer': 'Hello, World!',
                               'status': 'OK',
                               'your_result': 'Hello, World!'}


@pytest.mark.asyncio
async def test_check_answer_fail():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Please write this content: "OK\nOK\nOK'
        # in the output file materials/0_test/output/task_1.txt
        response = await ac.post(f"api/check/0/1", files={
            'file': b'print("OK")'
        })
    assert response.status_code == 200
    assert response.json() == {'answer': 'Hello, World!',
                               'status': 'WRONG',
                               'your_result': 'OK'}
