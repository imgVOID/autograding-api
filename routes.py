from fastapi import (FastAPI, Response, status,
                     HTTPException, File, UploadFile, Depends)
from utils import DockerUtils
import os
import random
from fastapi.responses import FileResponse
from models import Task, TaskUpdate, TaskAnswer
from fastapi.encoders import jsonable_encoder
import json
import aiofiles

app = FastAPI()
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DockerUtils.fix_docker_bug()


def get_filepath(title, theme_id, task_id):
    filesystem = {
        "task_info": os.path.join(APP_ROOT,
                                  'materials', f'{theme_id}',
                                  'description', f'task_{task_id}.json'),
        "task_input": os.path.join(APP_ROOT,
                                   'materials', f'{theme_id}',
                                   'input', f'task_{task_id}.txt'),
        "task_output": os.path.join(APP_ROOT,
                                    'materials', f'{theme_id}',
                                    'output', f'task_{task_id}.txt'),
        "task_code": os.path.join(APP_ROOT,
                                  'materials', f'{theme_id}',
                                  'code', f'task_{task_id}.txt'),
    }
    return filesystem.get(title)


async def save_user_input(code, theme, id):
    random_id = random.randint(0, 100000)
    filename = os.path.join(APP_ROOT,
                            f'materials/{theme}/inputs/',
                            f'task_{id}_{random_id}.py')
    async with aiofiles.open(filename, encoding='utf-8', mode='w') as f:
        await f.write(code)
    return f.name, random_id


@app.get("/tasks")
async def read_syllabus():
    return FileResponse(os.path.join(APP_ROOT, 'materials', 'themes.json'))


@app.get("/tasks/{theme_id}/{task_id}")
async def read_task(theme_id, task_id) -> str:
    filename = os.path.join(APP_ROOT,
                            'materials', f'{theme_id}',
                            'description', f'task_{task_id}.json')
    try:
        async with aiofiles.open(filename, mode='r', encoding='utf-8') as f:
            contents = await f.read()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Task not found") from e
    else:
        return json.loads(contents.encode('utf-8'))


@app.post("/tasks")
async def create_task(task: Task = Depends(), code: UploadFile = File(...)):
    # Open themes info
    async with aiofiles.open(os.path.join(APP_ROOT, 'materials/themes.json'),
                             encoding='utf-8', mode='r') as f:
        contents = await f.read()
    themes_json = json.loads(contents)
    # Get the new task's id
    task.id = themes_json[task.theme_id].get("count") + 1
    # Save task info
    async with aiofiles.open(get_filepath("task_info", task.theme_id, task.id),
                             mode='w', encoding='utf-8') as f:
        task_description = ("id", "theme_id", "description")
        task_description = {key: value for key, value in task if key in task_description}
        task_json = json.dumps(task_description, ensure_ascii=False)
        await f.write(task_json)

    # Save task's input values
    async with aiofiles.open(get_filepath("task_input", task.theme_id, task.id),
                             mode='w', encoding='utf-8') as f:
        for value in task.input:
            if task.split_values:
                values = value.split(",")
                for sub_value in values:
                    await f.writelines(f'{sub_value}\n')
            else:
                await f.writelines(f'{value}\n')

    # Save task answer's output values
    async with aiofiles.open(get_filepath("task_output", task.theme_id, task.id),
                             mode='w', encoding='utf-8') as f:
        for value in task.output:
            if task.split_values:
                values = value.split(",")
                for sub_value in values:
                    await f.writelines(f'{sub_value}\n')
            else:
                await f.writelines(f'{value}\n')

    # Save task's code
    async with aiofiles.open(get_filepath("task_code", task.theme_id, task.id),
                             mode='w', encoding='utf-8') as f:
        code = await code.read()
        await f.write(code.decode('utf-8'))

    # Update the theme tasks count
    async with aiofiles.open(os.path.join(APP_ROOT, 'materials/themes.json'),
                             encoding='utf-8', mode='w') as f:
        themes_json[task.theme_id]["count"] += 1
        await f.write(json.dumps(themes_json, ensure_ascii=False))

    return task


@app.delete("/tasks/{theme_id}/{task_id}", status_code=204)
async def delete_task(task_id: int, theme_id: int) -> Response:
    filesystem = {
        "task_info": get_filepath("task_info", theme_id, task_id),
        "task_input": get_filepath("task_input", theme_id, task_id),
        "task_output": get_filepath("task_output", theme_id, task_id)
    }
    for filepath in filesystem:
        if os.path.exists(filesystem.get(filepath)):
            os.remove(filesystem.get(filepath))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/tasks/{theme_id}/{task_id}")
async def update_task(task_id: int, theme_id: int, task: TaskUpdate):
    update_task_encoded = jsonable_encoder(task)

    # Update task's description
    if update_task_encoded.get("description") is not None:
        # Get task info
        filename = os.path.join(get_filepath("task_info", theme_id, task_id))
        try:
            async with aiofiles.open(filename, mode='r', encoding='utf-8') as f:
                contents = await f.read()
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail="Task not found") from e
        task_description = json.loads(contents)
        task_description["description"] = update_task_encoded.get("description")
        # Save task info
        async with aiofiles.open(filename, mode='w', encoding='utf-8') as f:
            await f.write(json.dumps(task_description, ensure_ascii=False))

    # Update task's input values
    if update_task_encoded.get("input") is not None:
        filename = os.path.join(get_filepath("task_input", theme_id, task_id))
        try:
            async with aiofiles.open(filename, mode='w', encoding='utf-8') as f:
                await f.write(update_task_encoded.get("input"))
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail="Task not found") from e

    # Update task answer's output values
    if update_task_encoded.get("output") is not None:
        filename = os.path.join(get_filepath("task_output", theme_id, task_id))
        try:
            async with aiofiles.open(filename, mode='w', encoding='utf-8') as f:
                await f.write(update_task_encoded.get("output"))
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail="Task not found") from e

    return update_task_encoded


@app.post("/tasks/check/{theme_id}/{task_id}")
async def check_task_answer(theme_id, task_id, answer: TaskAnswer):
    code = answer.code
    return code


@app.post("/files/{theme_id}/{task_id}")
async def check_user_answer(theme_id, task_id, file: bytes = File(...)):
    filename = os.path.join(get_filepath("task_output", theme_id, task_id))
    try:
        async with aiofiles.open(filename, mode='r', encoding='utf-8') as f:
            contents = await f.read()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Task not found") from e
    random_id = random.randint(0, 100000)
    filename = os.path.join(APP_ROOT, 'temp', f'task_{task_id}_{random_id}.py')
    async with aiofiles.open(filename, encoding='utf-8', mode='w') as f:
        await f.write(file.decode('utf-8'))

    user_answer = await DockerUtils.docker_setup(theme_id, task_id, filename, random_id)
    if user_answer == contents:
        return {'answer': contents, 'your_result': user_answer, 'status': 'OK'}
    else:
        return {'answer': contents, 'your_result': user_answer, 'status': 'WRONG'}
