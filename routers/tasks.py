import json
import aiofiles
from os.path import dirname, abspath, join
from os import remove
from fastapi import Response, status, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from schemas.tasks import Task, TaskUpdate, TaskCreate, NotFoundMessage
from routers import router_tasks
from utilities.file_scripts import FileUtils

APP_ROOT = dirname(dirname(abspath(__file__)))


@router_tasks.get("/", status_code=200,
                  summary="Read syllabus")
async def read_task_list():
    """
    The `list of tasks` endpoint.
    """
    return FileResponse(join(APP_ROOT, 'materials', 'themes.json'))


@router_tasks.get("/{theme_id}/{task_id}",
                  status_code=200, responses={404: {"model": NotFoundMessage}},
                  response_model=Task, summary="Read task by ID",
                  )
async def read_task(theme_id: int, task_id: int) -> Task or JSONResponse:
    """The `read task` CRUD endpoint."""
    try:
        description = await FileUtils.open_file(
            FileUtils.get_filepath('task_info', theme_id, task_id)
        )
        inputs = await FileUtils.open_file_values(
            FileUtils.get_filepath('task_input', theme_id, task_id)
        )
        outputs = await FileUtils.open_file_values(
            FileUtils.get_filepath('task_output', theme_id, task_id)
        )
    except FileNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Task not found"})
    else:
        return Task(**description, input=list(inputs), output=list(outputs))


@router_tasks.post("/", status_code=201,
                   response_model=Task, summary="Create new task")
async def create_task(task: TaskCreate, test: bool = False, code: UploadFile = File(...)) -> Task:
    """The `create task` CRUD endpoint."""
    # If this is a test mode, the actual data will be protected from changes.
    if not test:
        themes_path = join(APP_ROOT, 'materials', 'themes.json')
    else:
        themes_path = join(APP_ROOT, 'tests', 'data', 'test_themes.json')
    # New task info dictionary
    task_description = {key: value for key, value in task
                        if key in ("id", "theme_id", "description")}
    # Open themes info
    themes_json = await FileUtils.open_file(themes_path)
    # Get the new task's id
    task = Task(**task.dict())
    task.id = themes_json[task.theme_id].get("count") + 1
    # Save task info
    await FileUtils.save_file(
        path=FileUtils.get_filepath("task_info", task.theme_id, task.id),
        content=task_description
    )
    # Save task's input values
    await FileUtils.save_file_values(
        path=FileUtils.get_filepath("task_input", task.theme_id, task.id),
        content_sequence=task.input
    )
    # Save task code's output values
    await FileUtils.save_file_values(
        path=FileUtils.get_filepath("task_output", task.theme_id, task.id),
        content_sequence=task.output
    )
    # Save task's code
    await FileUtils.save_file(
        path=FileUtils.get_filepath("task_code", task.theme_id, task.id),
        content=await code.read()
    )
    # Update the theme tasks count
    themes_json[task.theme_id]["count"] += 1
    await FileUtils.save_file(themes_path, themes_json)
    return task


@router_tasks.put("/{theme_id}/{task_id}",
                  status_code=200, responses={404: {"model": NotFoundMessage}},
                  response_model=TaskUpdate, response_model_exclude_none=True,
                  summary="Update task by ID")
async def update_task(theme_id: int, task_id: int, task: TaskUpdate,
                      code: UploadFile = File(None)) -> TaskUpdate or JSONResponse:
    """The `update task` CRUD endpoint."""
    task.theme_id = theme_id
    task.id = task_id
    task_update_encoded = jsonable_encoder(task)
    # Update task's description
    if task_update_encoded.get("description"):
        # Get task info
        try:
            task_description = await FileUtils.open_file(
                FileUtils.get_filepath("task_info", theme_id, task_id)
            )
        except FileNotFoundError:
            return JSONResponse(status_code=404, content={"message": "Task not found"})
        task_description["description"] = task_update_encoded.get("description")
        # Save task info
        await FileUtils.save_file(
            path=FileUtils.get_filepath("task_info", task.theme_id, task.id),
            content=task_description
        )
    # Update task's input values
    if task_update_encoded.get("input"):
        try:
            await FileUtils.save_file_values(
                path=FileUtils.get_filepath("task_input", theme_id, task.id),
                content_sequence=task_update_encoded.get("input")
            )
        except FileNotFoundError:
            return JSONResponse(status_code=404, content={"message": "Task not found"})
    # Update task answer's output values
    if task_update_encoded.get("output"):
        try:
            await FileUtils.save_file_values(
                path=FileUtils.get_filepath("task_output", theme_id, task.id),
                content_sequence=task_update_encoded.get("output")
            )
        except FileNotFoundError:
            return JSONResponse(status_code=404, content={"message": "Task not found"})
    # Update task's code file
    if code:
        try:
            await FileUtils.save_file(
                path=FileUtils.get_filepath("task_code", theme_id, task.id),
                content=await code.read()
            )
        except FileNotFoundError:
            return JSONResponse(status_code=404, content={"message": "Task not found"})
    return task_update_encoded


@router_tasks.delete("/{theme_id}/{task_id}",
                     status_code=204, responses={404: {"model": NotFoundMessage}},
                     summary="Delete task by ID")
async def delete_task(task_id: int, theme_id: int, test: bool = False) -> Response or JSONResponse:
    """The `delete task` CRUD endpoint."""
    if not test:
        themes_path = join(APP_ROOT, 'materials', 'themes.json')
    else:
        themes_path = join(APP_ROOT, 'tests', 'data', 'test_themes.json')

    filesystem = {
        "task_info": FileUtils.get_filepath("task_info", theme_id, task_id),
        "task_input": FileUtils.get_filepath("task_input", theme_id, task_id),
        "task_output": FileUtils.get_filepath("task_output", theme_id, task_id),
        "task_code": FileUtils.get_filepath("task_code", theme_id, task_id),
    }
    for filepath in filesystem:
        try:
            remove(filesystem.get(filepath))
        except FileNotFoundError:
            return JSONResponse(status_code=404, content={"message": "Task not found"})

    # Open themes info
    async with aiofiles.open(themes_path,
                             encoding='utf-8', mode='r') as f:
        contents = await f.read()
    themes_json = json.loads(contents)
    # Update the theme tasks count
    themes_json[theme_id]["count"] -= 1
    await FileUtils.save_file(themes_path, themes_json)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
