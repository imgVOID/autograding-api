from fastapi import File, UploadFile
from fastapi.responses import JSONResponse
from routers import router_check
from utilities.docker_scripts import DockerUtils
from utilities.file_scripts import FileUtils
from schemas.check import CheckResult
from schemas.tasks import NotFoundMessage


@router_check.post("/{theme_id}/{task_id}",
                   status_code=200, responses={404: {"model": NotFoundMessage}},
                   response_model=CheckResult, summary="Check user's answer")
async def check_user_answer(theme_id: int, task_id: int, extension: str = 'txt',
                            file: UploadFile = File(...)) -> CheckResult or JSONResponse:
    try:
        theme_index = await FileUtils.open_file("theme_index")
    except FileNotFoundError:
        return JSONResponse(status_code=404, content={"message": "Themes list file not found"})
    else:
        try:
            theme_name = theme_index[theme_id].get('path')
        except IndexError:
            return JSONResponse(status_code=404, content={"message": "Task not found"})

    expected_answer = await FileUtils.open_file("task_output", theme_id, task_id)
    expected_answer = expected_answer.decode('utf-8')
    path, random_id = await FileUtils.save_user_answer(task_id, await file.read(), extension)

    user_answer = await DockerUtils.docker_setup(
        theme_name, task_id, path, random_id, extension
    )

    if user_answer.replace('\n', '') == expected_answer.replace('\n', ''):
        return CheckResult(status='OK', answer=expected_answer,
                           your_result=user_answer)
    else:
        return CheckResult(status='WRONG', answer=expected_answer,
                           your_result=user_answer)
