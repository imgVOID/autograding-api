from fastapi import status, File, UploadFile, APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from schemas.tasks import Task, TaskUpdate, TaskCreate
from schemas.errors import NotFoundTopic, NotFoundTask, EmptyRequest
from schemas.auth import User
from utilities.file_scripts import FileUtils
from utilities.auth_scripts import get_current_active_user

router_tasks = APIRouter(
    redirect_slashes=False,
    prefix="/api/tasks",
    tags=["tasks"],
)


@router_tasks.get(
    "/{topic_id}/{task_id}", status_code=200, summary="Read task by ID",
    response_model=Task, responses={404: {"model": NotFoundTask}},
)
async def read_task(topic_id: int, task_id: int) -> Task or JSONResponse:
    """The `read task` CRUD endpoint."""
    try:
        # Get task info, inputs and outputs.
        description = await FileUtils.open_file('task_info', topic_id, task_id)
        inputs = await FileUtils.open_file_values('task_input', topic_id, task_id)
        outputs = await FileUtils.open_file_values('task_output', topic_id, task_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=NotFoundTask().error)
    except IndexError:
        raise HTTPException(status_code=404, detail=NotFoundTopic().error)
    else:
        return Task(**description, input=list(inputs), output=list(outputs))


@router_tasks.post(
    "/{topic_id}", status_code=201, summary="Create new task",
    response_model=Task, responses={404: {"model": NotFoundTopic}}
)
async def create_task(
        topic_id: int, task: TaskCreate or UploadFile, background_tasks: BackgroundTasks,
        code: UploadFile = File(...), current_user: User = Depends(get_current_active_user)
) -> Task or JSONResponse:
    """The `create task` CRUD endpoint."""
    # If this is a test mode, the actual data will be protected from changes.
    try:
        topics_json = await FileUtils.open_file('topic_index', topic_id=topic_id)
    except IndexError:
        raise HTTPException(status_code=404, detail=NotFoundTopic().error)
    if isinstance(task, UploadFile):
        task = TaskCreate(**jsonable_encoder(task))
    # Get ID
    task_id = topics_json[topic_id].get("count") + 1
    # Create new task
    task = Task(
        id=task_id, topic_id=topic_id, **task.dict()
    )
    # New task's info dictionary
    task_description = {key: value for key, value in task
                        if key in ("id", "topic_id", "title", "description")}
    saving_config = {
        "topic_id": topic_id, "task_id": task.id
    }
    # Save task info
    background_tasks.add_task(FileUtils.save_file, 'task_info', content=task_description, **saving_config)
    # Save task's input values
    background_tasks.add_task(FileUtils.save_file_values, "task_input", content=task.input, **saving_config)
    # Save task code's output values
    background_tasks.add_task(FileUtils.save_file_values, "task_output", content=task.output, **saving_config)
    # Save task's code
    background_tasks.add_task(FileUtils.save_file, "task_code", content=await code.read(), **saving_config)
    # Update the topic tasks count
    topics_json[topic_id]["count"] = task_id
    background_tasks.add_task(FileUtils.save_file, 'topic_index', content=topics_json)
    return task


@router_tasks.patch(
    "/{topic_id}/{task_id}", status_code=200, summary="Update task by ID",
    response_model=TaskUpdate, response_model_exclude_none=True,
    responses={404: {"model": NotFoundTask}}
)
async def update_task(
        topic_id: int, task_id: int, task: TaskUpdate, background: BackgroundTasks,
        code: UploadFile = File(None), current_user: User = Depends(get_current_active_user)
) -> Task or JSONResponse:
    """The `update task` CRUD endpoint.\n
    You can update description, code, inputs and outputs,
    one at a time, or all at once.\n
    Please uncheck "Send empty value" in Swagger UI!
    """
    if not any(task.dict().values()):
        raise HTTPException(status_code=422, detail=EmptyRequest().error)

    saving_config = {"topic_id": topic_id, "task_id": task_id}
    code = await code.read()
    task = TaskUpdate(**jsonable_encoder(task))
    task.id = task_id
    task.topic_id = topic_id

    # Update task's description
    if any([task.title, task.description]):
        try:
            # Get task info
            task_info = await FileUtils.open_file("task_info", **saving_config)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=NotFoundTask().error)
        except IndexError:
            raise HTTPException(status_code=404, detail=NotFoundTopic().error)
        else:
            # Update task's description
            task_info["title"] = task.title if task.title else task_info["title"]
            task_info["description"] = task.description if task.description else task_info["description"]
            background.add_task(FileUtils.save_file, "task_info", content=task_info, **saving_config)
    # Update task's input values
    if task.input:
        try:
            background.add_task(FileUtils.save_file_values, "task_input", content=task.input, **saving_config)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=NotFoundTask().error)
    # Update task answer's output values
    if task.output:
        try:
            background.add_task(FileUtils.save_file_values, "task_output", content=task.output, **saving_config)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=NotFoundTask().error)
    # Update task's code file
    if code:
        try:
            background.add_task(FileUtils.save_file, "task_code", content=code, **saving_config)
        except IndexError:
            raise HTTPException(status_code=404, detail=NotFoundTopic().error)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=NotFoundTask().error)
    return Task(task_id=task.id, **task.dict())


@router_tasks.delete(
    "/{topic_id}/{task_id}", status_code=204, summary="Delete task by ID",
    responses={404: {"model": NotFoundTask}}
)
async def delete_task(
        task_id: int, topic_id: int, background: BackgroundTasks,
        current_user: User = Depends(get_current_active_user)
) -> Response or JSONResponse:
    """The `delete task` CRUD endpoint."""
    files = ("task_info", "task_input", "task_output", "task_code")
    for title in files:
        try:
            await FileUtils.remove_file(title, topic_id=topic_id, task_id=task_id)
        except IndexError:
            raise HTTPException(status_code=404, detail=NotFoundTopic().error)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=NotFoundTask().error)
    # Open topic info
    topics = await FileUtils.open_file('topic_index')
    # Update the topic tasks count
    topics[topic_id]["count"] -= 1
    background.add_task(FileUtils.save_file, "topic_index", content=topics, topic_id=topic_id, task_id=task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
