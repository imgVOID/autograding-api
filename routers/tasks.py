import json
import aiofiles
from os.path import dirname, abspath, join, exists
from os import remove
from fastapi import (Response, status, HTTPException,
                     File, UploadFile)
from fastapi.responses import FileResponse
from fastapi.encoders import jsonable_encoder
from models import Task, TaskUpdate
from routers import router_tasks
from utilities.file_scripts import get_filepath

APP_ROOT = dirname(dirname(abspath(__file__)))


@router_tasks.get("/")
async def read_syllabus():
    return FileResponse(join(APP_ROOT, 'materials', 'themes.json'))


@router_tasks.post("/", status_code=201)
async def create_task(task: Task, test: bool = False,
                      code: UploadFile = File(...)):
    if not test:
        themes_path = join(APP_ROOT, 'materials', 'themes.json')
    else:
        themes_path = join(APP_ROOT, 'tests', 'data', 'test_themes.json')

        # Open themes info
    async with aiofiles.open(themes_path,
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
            await f.writelines(f'{value}\n')

    # Save task answer's output values
    async with aiofiles.open(get_filepath("task_output", task.theme_id, task.id),
                             mode='w', encoding='utf-8') as f:
        for value in task.output:
            await f.writelines(f'{value}\n')

    # Save task's code
    async with aiofiles.open(get_filepath("task_code", task.theme_id, task.id),
                             mode='w', encoding='utf-8') as f:
        code = await code.read()
        await f.write(code.decode('utf-8'))

    # Update the theme tasks count
    async with aiofiles.open(themes_path,
                             encoding='utf-8', mode='w') as f:
        themes_json[task.theme_id]["count"] += 1
        await f.write(json.dumps(themes_json, ensure_ascii=False))
    return task


@router_tasks.get("/{theme_id}/{task_id}")
async def read_task(theme_id, task_id) -> str:
    filename = join(APP_ROOT, 'materials', f'{theme_id}',
                    'description', f'task_{task_id}.json')
    try:
        async with aiofiles.open(filename, mode='r', encoding='utf-8') as f:
            contents = await f.read()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Task not found") from e
    else:
        return json.loads(contents.encode('utf-8'))


@router_tasks.put("/{theme_id}/{task_id}", status_code=200,
                  response_model_exclude_none=True)
async def update_task(theme_id: int, task_id: int, task: TaskUpdate,
                      code: UploadFile = File(None)):
    task.theme_id = theme_id
    task.id = task_id
    update_task_encoded = jsonable_encoder(task)

    # Update task's description
    if update_task_encoded.get("description"):
        # Get task info
        filename = join(get_filepath("task_info", theme_id, task_id))
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
    if update_task_encoded.get("input"):
        filename = join(get_filepath("task_input", theme_id, task_id))
        try:
            async with aiofiles.open(filename, mode='w', encoding='utf-8') as f:
                for input_value in update_task_encoded.get("input"):
                    await f.write(f'{input_value}\n')
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail="Task not found") from e

    # Update task answer's output values
    if update_task_encoded.get("output"):
        filename = join(get_filepath("task_output", theme_id, task_id))
        try:
            async with aiofiles.open(filename, mode='w', encoding='utf-8') as f:
                for output_value in update_task_encoded.get("output"):
                    await f.write(f'{output_value}\n')
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail="Task not found") from e

    # Update task's code file
    if code:
        filename = join(get_filepath("task_code", theme_id, task_id))
        try:
            async with aiofiles.open(filename, mode='w', encoding='utf-8') as f:
                code = await code.read()
                await f.write(code.decode('utf-8'))
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail="Task not found") from e

    return update_task_encoded


@router_tasks.delete("/{theme_id}/{task_id}", status_code=204)
async def delete_task(task_id: int, theme_id: int, test: bool = False) -> Response:
    if not test:
        themes_path = join(APP_ROOT, 'materials', 'themes.json')
    else:
        themes_path = join(APP_ROOT, 'tests', 'data', 'test_themes.json')

    filesystem = {
        "task_info": get_filepath("task_info", theme_id, task_id),
        "task_input": get_filepath("task_input", theme_id, task_id),
        "task_output": get_filepath("task_output", theme_id, task_id),
        "task_code": get_filepath("task_code", theme_id, task_id),
    }
    for filepath in filesystem:
        if exists(filesystem.get(filepath)):
            remove(filesystem.get(filepath))
    # Open themes info
    async with aiofiles.open(themes_path,
                             encoding='utf-8', mode='r') as f:
        contents = await f.read()
    themes_json = json.loads(contents)
    # Update the theme tasks count
    async with aiofiles.open(themes_path,
                             encoding='utf-8', mode='w') as f:
        themes_json[theme_id]["count"] -= 1
        await f.write(json.dumps(themes_json, ensure_ascii=False))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
