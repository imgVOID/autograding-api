import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_task_list():
    async with AsyncClient(app=app, base_url="https://") as ac:
        response = await ac.get("/api/themes/0")

    assert response.status_code == 200
    assert response.json()["theme_id"] == 0
    assert response.json()['tasks_count'] == len(response.json()["tasks"])


@pytest.mark.asyncio
async def test_task_list_not_found():
    async with AsyncClient(app=app, base_url="https://") as ac:
        response_not_found_theme = await ac.get("/api/themes/999")

    assert response_not_found_theme.status_code == 404
    assert response_not_found_theme.json()["message"] == "Theme not found"
