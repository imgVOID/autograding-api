import random
import aiofiles
from os.path import dirname, abspath, join
from fastapi import (HTTPException, File)
from routers import router_check
from utilities.docker_scripts import DockerUtils
from utilities.file_scripts import get_filepath

APP_ROOT = dirname(dirname(abspath(__file__)))


@router_check.post("/{theme_id}/{task_id}")
async def check_user_answer(theme_id, task_id, file: bytes = File(...)):
    filename = join(get_filepath("task_output", theme_id, task_id))
    try:
        async with aiofiles.open(filename, mode='r', encoding='utf-8') as f:
            contents = await f.read()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Task not found") from e
    random_id = random.randint(0, 100000)
    filename = join(APP_ROOT, '../temp', f'task_{task_id}_{random_id}.py')
    async with aiofiles.open(filename, encoding='utf-8', mode='w') as f:
        await f.write(file.decode('utf-8'))

    user_answer = await DockerUtils.docker_setup(theme_id, task_id, filename, random_id)
    if user_answer == contents:
        return {'answer': contents, 'your_result': user_answer, 'status': 'OK'}
    else:
        return {'answer': contents, 'your_result': user_answer, 'status': 'WRONG'}
