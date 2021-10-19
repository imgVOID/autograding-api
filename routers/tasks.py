from fastapi import Response, status, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from routers import router_tasks
from schemas.tasks import Task, TaskUpdate, TaskCreate, NotFoundMessage
from utilities.file_scripts import FileUtils


@router_tasks.get("/", status_code=200,
                  summary="Read syllabus")
async def read_task_list():
    """
    The `list of tasks` endpoint.
    """
    return JSONResponse(status_code=200,
                        content=await FileUtils.open_file('theme_index'))


@router_tasks.get("/{theme_id}/{task_id}",
                  status_code=200, responses={404: {"model": NotFoundMessage}},
                  response_model=Task, summary="Read task by ID")
async def read_task(theme_id: int, task_id: int) -> Task or JSONResponse:
    """The `read task` CRUD endpoint."""
    try:
        # Get task info, inputs and outputs.
        description = await FileUtils.open_file('task_info', theme_id, task_id)
        inputs = await FileUtils.open_file_values('task_input', theme_id, task_id)
        outputs = await FileUtils.open_file_values('task_output', theme_id, task_id)
    except FileNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Task not found"})
    except IndexError:
        return JSONResponse(status_code=404, content={"message": "Theme not found"})
    else:
        return Task(**description, input=list(inputs), output=list(outputs))


# TODO: create parameter theme_id
@router_tasks.post("/", status_code=201,
                   response_model=Task, summary="Create new task")
async def create_task(task: TaskCreate, code: UploadFile = File(...)) -> Task or JSONResponse:
    """The `create task` CRUD endpoint."""
    # If this is a test mode, the actual data will be protected from changes.
    try:
        themes_json = await FileUtils.open_file('theme_index', theme_id=task.theme_id)
    except IndexError:
        return JSONResponse(status_code=404, content={"message": "Theme not found"})
    # Create new task
    task = Task(
        id=themes_json[task.theme_id].get("count") + 1, **task.dict()
    )
    # New task's info dictionary
    task_description = {key: value for key, value in task
                        if key in ("id", "theme_id", "title", "description")}
    # Save task info
    await FileUtils.save_file(
        'task_info', content=task_description, theme_id=task.theme_id, task_id=task.id
    )
    # Save task's input values
    await FileUtils.save_file_values(
        "task_input", content_sequence=task.input, theme_id=task.theme_id, task_id=task.id
    )
    # Save task code's output values
    await FileUtils.save_file_values(
        "task_output", content_sequence=task.output, theme_id=task.theme_id, task_id=task.id
    )
    # Save task's code
    await FileUtils.save_file(
        "task_code", content=await code.read(), theme_id=task.theme_id, task_id=task.id
    )
    # Update the theme tasks count
    themes_json[task.theme_id]["count"] += 1
    await FileUtils.save_file('theme_index', content=themes_json)
    return task


@router_tasks.put("/{theme_id}/{task_id}",
                  status_code=200, responses={404: {"model": NotFoundMessage}},
                  response_model=TaskUpdate, response_model_exclude_none=True,
                  summary="Update task by ID")
async def update_task(theme_id: int, task_id: int, task: TaskUpdate,
                      code: UploadFile = File(None)) -> TaskUpdate or JSONResponse:
    """The `update task` CRUD endpoint.\n
    You can update description, code, inputs and outputs,
    one at a time, or all at once.\n
    If you want to change only the code, please send an empty dict,
    and uncheck the "Send empty value" checkbox
    if you are using the API through a Swagger Docs.
    """
    task.theme_id = theme_id
    task.id = task_id
    task_update_encoded = jsonable_encoder(task)
    # Update task's description
    if task_update_encoded.get("description"):
        try:
            # Get task info
            task_description = await FileUtils.open_file(
                "task_info", theme_id=theme_id, task_id=task_id
            )
        except FileNotFoundError:
            return JSONResponse(status_code=404, content={"message": "Task not found"})
        task_description["description"] = task_update_encoded.get("description")
        # Save task info
        await FileUtils.save_file(
            "task_info", content=task_description, theme_id=task.theme_id, task_id=task.id
        )
    # Update task's input values
    if task_update_encoded.get("input"):
        try:
            await FileUtils.save_file_values(
                "task_input", content_sequence=task_update_encoded.get("input"),
                theme_id=theme_id, task_id=task.id,
            )
        except FileNotFoundError:
            return JSONResponse(status_code=404, content={"message": "Task not found"})
    # Update task answer's output values
    if task_update_encoded.get("output"):
        try:
            await FileUtils.save_file_values(
                "task_output", content_sequence=task_update_encoded.get("output"),
                theme_id=theme_id, task_id=task.id,
            )
        except FileNotFoundError:
            return JSONResponse(status_code=404, content={"message": "Task not found"})
    # Update task's code file
    if code:
        try:
            await FileUtils.save_file(
                "task_code", content=await code.read(), theme_id=theme_id, task_id=task.id
            )
        except FileNotFoundError:
            return JSONResponse(status_code=404, content={"message": "Task not found"})
    return task_update_encoded


@router_tasks.delete("/{theme_id}/{task_id}",
                     status_code=204, responses={404: {"model": NotFoundMessage}},
                     summary="Delete task by ID")
async def delete_task(task_id: int, theme_id: int) -> Response or JSONResponse:
    """The `delete task` CRUD endpoint."""
    files = ("task_info", "task_input", "task_output", "task_code")
    for title in files:
        try:
            await FileUtils.remove_file(title, theme_id=theme_id, task_id=task_id)
        except FileNotFoundError:
            return JSONResponse(status_code=404, content={"message": "Task not found"})
    # Open themes info
    themes = await FileUtils.open_file('theme_index')
    # Update the theme tasks count
    themes[theme_id]["count"] -= 1
    await FileUtils.save_file('theme_index', content=themes, theme_id=theme_id, task_id=task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
