from fastapi import File, UploadFile, APIRouter, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.requests import Request
from routers import limiter
from utilities.docker_scripts import DockerUtils
from utilities.file_scripts import FileUtils
from schemas.errors import NotFoundTask, NotFoundTheme, RateLimitExceeded, DockerUnavailable
from schemas.check import CheckResult

router_check = APIRouter(
    redirect_slashes=False,
    prefix="/api/check",
    tags=["check"],
)


@router_check.post(
    "/{theme_id}/{task_id}", status_code=200, summary="Check user's answer",
    response_model=CheckResult, responses={
        404: {"model": NotFoundTask}, 429: {"model": RateLimitExceeded},
        503: {"model": DockerUnavailable}
    }
)
@limiter.limit("2/minute")
async def check_user_answer(
        request: Request, response: Response, theme_id: int, task_id: int,
        extension: str = 'txt', file: UploadFile = File(...)
) -> CheckResult or JSONResponse:
    # Get theme name
    theme_index = await FileUtils.open_file("theme_index")
    try:
        theme_name = theme_index[theme_id].get('path')
    except IndexError or AttributeError:
        raise HTTPException(status_code=404, detail=NotFoundTheme().error)
    # Get expected output
    try:
        expected_answer = await FileUtils.open_file("task_output", theme_id, task_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=NotFoundTask().error)
    else:
        expected_answer = expected_answer.decode('utf-8')
    # Save user input
    temp_name = await FileUtils.get_user_answer_temp(code=await file.read())
    # Run user input into the Docker container
    user_answer = await DockerUtils.docker_check_user_answer(
        theme_name, task_id, temp_name
    )
    # Check container's stdout
    if not user_answer:
        raise HTTPException(status_code=404, detail=DockerUnavailable().error)
    elif user_answer.replace('\n', '') == expected_answer.replace('\n', ''):
        return CheckResult(status='OK', answer=expected_answer,
                           your_result=user_answer)
    else:
        return CheckResult(status='WRONG', answer=expected_answer,
                           your_result=user_answer)
