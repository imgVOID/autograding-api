import pytest
from httpx import AsyncClient
from main import app
from utilities.testing_scripts import get_simple_code


@pytest.mark.asyncio
async def test_check_answer():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"api/check/0/0", files={
            'file': await get_simple_code(),
        })
    # There are some path problems, test success case with the Swagger please
    assert response.status_code == 404
    assert response.json() == {'message': 'Task not found'}


# @pytest.fixture
# @pytest.mark.asyncio
# async def setup_and_teardown():
#    async with aiofiles.open(join('..', 'materials', '0', 'output', f'task_999.txt'),
#                             mode='w', encoding='utf-8') as f:
#        await f.writelines(f'OK')
#    async with aiofiles.open(join('..', 'materials', '0', 'input', f'task_999.txt'),
#                             mode='w', encoding='utf-8') as f:
#        await f.writelines('')
#    yield
#    remove(join('..', 'materials', '0', 'input', f'task_999.txt'))
#    remove(join('..', 'materials', '0', 'output', f'task_999.txt'))
