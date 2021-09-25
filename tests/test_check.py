import pytest
import aiofiles
import json
from os.path import abspath, dirname, join
from io import BytesIO
from httpx import AsyncClient

from main import app
from utilities.testing_scripts import get_simple_code, get_themes_counter


@pytest.fixture
@pytest.mark.asyncio
async def setup_and_teardown():
    async with aiofiles.open(join(dirname(abspath(__file__)),
                                  'data', 'new_task.json'),
                             mode='r', encoding='utf-8') as f:
        name = f.name
        description = await f.read()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/tasks", files={
            'task': (None, bytes(description, 'utf-8')),
            'code': (f'{name}', BytesIO(await get_simple_code())),
        }, params={"test": True})
    assert response.status_code == 201
    yield
    async with aiofiles.open(join(dirname(abspath(__file__)),
                                  'data', 'test_themes.json'),
                             mode='r', encoding='utf-8') as f:
        themes = await f.read()
        count = json.loads(themes)[0].get("count")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(f"/api/tasks/0/{count}", params={"test": True})
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_check_answer(setup_and_teardown):
    count = await get_themes_counter()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"api/check/0/{count}", files={
            'file': (None, BytesIO(await get_simple_code())),
        })
    assert response.status_code == 200
    assert response.json() == {
        "answer": "OK\nOK\nOK\n",
        "your_result": "OKOKOK",
        "status": "OK"
    }
