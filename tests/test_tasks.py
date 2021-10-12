import pytest
from os.path import abspath, dirname, join
from io import BytesIO
from aiofiles import open
from httpx import AsyncClient

from main import app
from utilities.test_scripts import get_simple_code

number = None


@pytest.mark.asyncio
async def test_task_list():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/tasks")
    global number
    number = response.json()[0]['count'] + 1

    assert response.status_code == 200

    for theme in response.json():
        assert isinstance(theme.get("id"), int)
        assert isinstance(theme.get("name"), str)
        assert isinstance(theme.get("path"), str)
        assert isinstance(theme.get("count"), int)


@pytest.mark.asyncio
async def test_task_create():
    async with open(join(dirname(abspath(__file__)),
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


@pytest.mark.asyncio
async def test_task_read():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/tasks/0/{number}")
    content = response.json()

    assert response.status_code == 200

    assert isinstance(content["id"], int)
    assert isinstance(content["theme_id"], int)
    assert isinstance(content["description"], list)


@pytest.mark.asyncio
async def test_task_update():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        files = {"task": b'{"description": ["string"], "input": [""], "output": ["OK"]}',
                 "code": await get_simple_code()}
        response = await ac.put(f"/api/tasks/0/{number}", files=files)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_task_delete():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(f"/api/tasks/0/{number}", params={"test": True})
    assert response.status_code == 204
