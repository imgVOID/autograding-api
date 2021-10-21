from fastapi.responses import JSONResponse
from routers import router_themes
from schemas.themes import Theme
from schemas.tasks import Task
from schemas.errors import NotFoundTheme
from utilities.file_scripts import FileUtils


@router_themes.get(
    "/{theme_id}", status_code=200, summary="Read theme syllabus",
    responses={404: {"model": NotFoundTheme}}
)
async def read_theme(theme_id: int) -> Theme or JSONResponse:
    """
    The `list of tasks` endpoint.
    """
    try:
        themes_json = await FileUtils.open_file('theme_index', theme_id=theme_id)
    except IndexError:
        return JSONResponse(status_code=404, content=NotFoundTheme().dict())
    # Get theme by ID
    theme = themes_json[theme_id]
    # Create new theme info object
    theme = Theme(
        theme_id=theme_id, theme_name=theme.get("name"),
        tasks_count=theme.get("count"), tasks=[]
    )
    # Get info about theme's tasks
    for task_id in range(1, theme.tasks_count + 1):
        description = await FileUtils.open_file('task_info', theme_id, task_id)
        inputs = await FileUtils.open_file_values('task_input', theme_id, task_id)
        outputs = await FileUtils.open_file_values('task_output', theme_id, task_id)
        theme.tasks.append(Task(**description, input=list(inputs), output=list(outputs)))
    return theme
