from fastapi import File, UploadFile, APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, Response
from fastapi.requests import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from schemas.errors import NotFoundTask, NotFoundTopic, RateLimitExceeded, DockerUnavailable
from schemas.checks import CheckResult
from schemas.auth import User
from utilities.docker_scripts import DockerUtils
from utilities.file_scripts import FileUtils
from utilities.auth_scripts import get_current_active_user

router_checks = APIRouter(
    redirect_slashes=False,
    prefix="/api/checks",
    tags=["checks"],
)

limiter = Limiter(key_func=get_remote_address)


@router_checks.post(
    "/{topic_id}/{task_id}", status_code=200, summary="Check user's answer",
    response_model=CheckResult, responses={
        404: {"model": NotFoundTask}, 429: {"model": RateLimitExceeded},
        503: {"model": DockerUnavailable}
    }
)
@limiter.limit("2/minute")
async def check_user_answer(
        request: Request, response: Response, topic_id: int, task_id: int,
        background_tasks: BackgroundTasks, current_user: User = Depends(get_current_active_user),
        file: UploadFile = File(...)
) -> CheckResult or JSONResponse:
    # Get topic name
    topic_index = await FileUtils.open_file("topic_index")
    try:
        topic_name = topic_index[topic_id].get('path')
    except IndexError or AttributeError:
        raise HTTPException(status_code=404, detail=NotFoundTopic().error)
    # Get expected output
    try:
        expected_answer = await FileUtils.open_file("task_output", topic_id, task_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=NotFoundTask().error)
    else:
        expected_answer = expected_answer.decode('utf-8').replace('\n', '').strip()
    # Save user input
    temp_name = await FileUtils.get_user_answer_temp(code=await file.read())
    background_tasks.add_task(
        DockerUtils.image_remove, topic_name, task_id, 'process'
    )
    background_tasks.add_task(FileUtils.remove_user_answer_file, temp_name)
    # Run user input into the Docker container
    user_answer, id_random = await DockerUtils.docker_check_user_answer(
        topic_name, task_id, temp_name
    )
    # Check container's stdout
    if not user_answer:
        raise HTTPException(status_code=404, detail=DockerUnavailable().error)
    elif user_answer.strip().replace('\n', '') == expected_answer:
        return CheckResult(status='OK', answer=expected_answer,
                           your_result=user_answer)
    else:
        return CheckResult(status='WRONG', answer=expected_answer,
                           your_result=user_answer)
