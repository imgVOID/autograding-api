import pytest
import aiofiles
import json
from io import BytesIO
from os.path import abspath, dirname, join
from httpx import AsyncClient
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


async def get_themes_counter():
    async with aiofiles.open(join(dirname(abspath(__file__)),
                                  'data', 'test_themes.json'),
                             mode='r', encoding='utf-8') as f:
        themes = await f.read()
        return json.loads(themes)[0].get("count")


@pytest.mark.asyncio
async def test_task_list():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/tasks")

    assert response.status_code == 200

    for theme in response.json():
        assert isinstance(theme.get("id"), int)
        assert isinstance(theme.get("name"), str)
        assert isinstance(theme.get("path"), str)
        assert isinstance(theme.get("count"), int)


@pytest.mark.asyncio
async def test_task_create():
    async with aiofiles.open(join(dirname(abspath(__file__)),
                                  'data', 'new_task.json'),
                             mode='r', encoding='utf-8') as f:
        name = f.name
        description = await f.read()
        code = BytesIO(b"print('OK')")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/tasks", files={
            'task': (None, bytes(description, 'utf-8')),
            'code': (f'{name}', code),
        }, params={"test": True})
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_task_read():
    count = await get_themes_counter()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/tasks/0/{count}")
    content = response.json()

    assert response.status_code == 200

    assert isinstance(content["id"], int)
    assert isinstance(content["theme_id"], int)
    assert isinstance(content["description"], list)


@pytest.mark.asyncio
async def test_task_update():
    count = await get_themes_counter()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        files = {"task": b'{"description": ["string"], "input": [""], "output": ["OK"]}',
                 "code": b'print("OK")'}
        response = await ac.put(f"/api/tasks/0/{count}", files=files)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_task_delete():
    count = await get_themes_counter()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(f"/api/tasks/0/{count}", params={"test": True})
    assert response.status_code == 204
