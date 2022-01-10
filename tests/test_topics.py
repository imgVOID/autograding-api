from pytest import mark
from httpx import AsyncClient
from main import app


class TestTopicsCRUDAsync:
    @mark.asyncio
    async def test_themes_read(self):
        async with AsyncClient(app=app, base_url="https://") as ac:
            response = await ac.get("/api/topics/0")

        assert response.status_code == 200
        assert response.json()["topic_id"] == 0
        assert response.json()['tasks_count'] == len(response.json()["tasks"])


class TestTopicsErrorsAsync:
    @mark.asyncio
    async def test_themes_read_not_found(self):
        async with AsyncClient(app=app, base_url="https://") as ac:
            response_not_found_theme = await ac.get("/api/topics/999")

        assert response_not_found_theme.status_code == 404
        assert response_not_found_theme.json()["detail"] == "Topic not found by ID"
