import pytest
from os.path import abspath, dirname, join
from aiofiles import open
from httpx import AsyncClient
from main import app


class TestTasksCRUD:
    @classmethod
    def setup_class(cls):
        cls.tasks_count = None

    @pytest.mark.asyncio
    async def test_task_create(self):
        async with open(join(dirname(abspath(__file__)), 'data', 'new_task.json'),
                        mode='r', encoding='utf-8') as f:
            name = f.name
            description = await f.read()
        async with AsyncClient(app=app, base_url="https://") as ac:
            response = await ac.post("/api/tasks/0", files={
                'task': (None, bytes(description, 'utf-8')),
                'code': (f'{name}', b'print("OK")\nprint("OK")\nprint("OK")\n'),
            })
        self.__class__.tasks_count = response.json()["id"]

        assert response.status_code == 201
        assert response.json().get("title") == 'string'
        assert response.json().get("theme_id") == 0

    @pytest.mark.asyncio
    async def test_task_read(self):
        async with AsyncClient(app=app, base_url="https://") as ac:
            response = await ac.get(f"/api/tasks/0/{self.tasks_count}")
        content = response.json()

        assert response.status_code == 200
        assert isinstance(content["id"], int)
        assert isinstance(content["theme_id"], int)
        assert isinstance(content["description"], list)

    @pytest.mark.asyncio
    async def test_task_update(self):
        async with AsyncClient(app=app, base_url="https://") as ac:
            files = {"task": (None, b'{"title": "", "description": ["test"], '
                                    b'"input": [], "output": []}'),
                     "code": b'print("OK")\nprint("OK")\nprint("OK")\n'}
            response = await ac.patch(f"/api/tasks/0/{self.tasks_count}", files=files)
        content = response.json()

        assert response.status_code == 200
        assert content.get("id") == self.tasks_count
        assert content.get("theme_id") == 0
        assert content.get("description") == ["test"]
        assert not content.get("title")
        assert not content.get("input")
        assert not content.get("output")

    @pytest.mark.asyncio
    async def test_task_delete(self):
        async with AsyncClient(app=app, base_url="https://") as ac:
            response = await ac.delete(f"/api/tasks/0/{self.tasks_count}", params={"test": True})
        assert response.status_code == 204


class TestTasksErrors:
    @pytest.mark.asyncio
    async def test_task_read_not_found(self):
        async with AsyncClient(app=app, base_url="https://") as ac:
            response_not_found_task = await ac.get(f"/api/tasks/0/9999")

        async with AsyncClient(app=app, base_url="https://") as ac:
            response_not_found_theme = await ac.get(f"/api/tasks/9999/9999")

        assert response_not_found_task.status_code == 404
        assert response_not_found_theme.status_code == 404
        assert response_not_found_task.json()["detail"] == "Task not found by ID"
        assert response_not_found_theme.json()["detail"] == "Theme not found by ID"

    @pytest.mark.asyncio
    async def test_task_create_not_found(self):
        async with open(join(dirname(abspath(__file__)), 'data', 'new_task.json'),
                        mode='r', encoding='utf-8') as f:
            name = f.name
            description = await f.read()
        async with AsyncClient(app=app, base_url="https://") as ac:
            response_not_found_theme = await ac.post("/api/tasks/9999", files={
                'task': (None, bytes(description, 'utf-8')),
                'code': (f'{name}', b'print("OK")\nprint("OK")\nprint("OK")\n'),
            })
        assert response_not_found_theme.status_code == 404
        assert response_not_found_theme.json()["detail"] == "Theme not found by ID"

    @pytest.mark.asyncio
    async def test_task_update_not_found(self):
        async with AsyncClient(app=app, base_url="https://") as ac:
            files = {"task": (None, b'{"title": "", "description": ["string"], '
                                    b'"input": [], "output": []}'),
                     "code": b''}
            response_not_found_task = await ac.patch(f"/api/tasks/0/9999", files=files)

        async with AsyncClient(app=app, base_url="https://") as ac:
            files = {"task": (None, b'{"title": "", "description": ["string"], '
                                    b'"input": [], "output": []}'),
                     "code": b''}
            response_not_found_theme = await ac.patch(f"/api/tasks/9999/9999", files=files)

        assert response_not_found_task.status_code == 404
        assert response_not_found_theme.status_code == 404
        assert response_not_found_task.json()["detail"] == "Task not found by ID"
        assert response_not_found_theme.json()["detail"] == "Theme not found by ID"

    @pytest.mark.asyncio
    async def test_task_delete_not_found(self):
        async with AsyncClient(app=app, base_url="https://") as ac:
            response_not_found_task = await ac.delete(f"/api/tasks/0/999", params={"test": True})
        async with AsyncClient(app=app, base_url="https://") as ac:
            response_not_found_theme = await ac.delete(f"/api/tasks/999/999", params={"test": True})
        assert response_not_found_task.status_code == 404
        assert response_not_found_task.json()["detail"] == "Task not found by ID"
        assert response_not_found_theme.status_code == 404
        assert response_not_found_theme.json()["detail"] == "Theme not found by ID"

    @pytest.mark.asyncio
    async def test_task_update_empty_request(self):
        async with AsyncClient(app=app, base_url="https://") as ac:
            files = {"task": (None, b'{"title": "", "description": [], '
                                    b'"input": [], "output": []}'),
                     "code": b''}
            response_not_found_task = await ac.patch(f"/api/tasks/0/999", files=files)

        assert response_not_found_task.status_code == 422
        assert response_not_found_task.json()["detail"] == "The request was empty"
