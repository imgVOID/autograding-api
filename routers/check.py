from fastapi import File, UploadFile
from fastapi.responses import JSONResponse
from routers import router_check
from utilities.docker_scripts import DockerUtils
from utilities.file_scripts import FileUtils
from schemas.check import CheckResult, UnavailableMessage
from schemas.tasks import NotFoundMessage


@router_check.post("/{theme_id}/{task_id}",
                   status_code=200, response_model=CheckResult, summary="Check user's answer",
                   responses={404: {"model": NotFoundMessage}, 503: {"model": UnavailableMessage}})
async def check_user_answer(theme_id: int, task_id: int, extension: str = 'txt',
                            file: UploadFile = File(...)) -> CheckResult or JSONResponse:
    # Get theme name
    theme_index = await FileUtils.open_file("theme_index")
    try:
        theme_name = theme_index[theme_id].get('path')
    except IndexError or AttributeError:
        return JSONResponse(status_code=404, content={"message": "Theme not found"})
    # Get expected output
    expected_answer = await FileUtils.open_file("task_output", theme_id, task_id)
    try:
        expected_answer = expected_answer.decode('utf-8')
    except AttributeError:
        return JSONResponse(status_code=404, content={"message": "Task not found"})
    # Save user input
    random_id = await FileUtils.save_user_answer(
        task_id=task_id, theme_id=theme_id, code=await file.read(), extension=extension
    )
    # Run user input into the Docker container
    user_answer = await DockerUtils.docker_setup(
        theme_name, theme_id, task_id, random_id, extension
    )
    # Check container's stdout
    if not user_answer:
        return JSONResponse(status_code=503,
                            content={"message": "Docker problems, please try again later"})
    elif user_answer.replace('\n', '') == expected_answer.replace('\n', ''):
        return CheckResult(status='OK', answer=expected_answer,
                           your_result=user_answer)
    else:
        return CheckResult(status='WRONG', answer=expected_answer,
                           your_result=user_answer)
