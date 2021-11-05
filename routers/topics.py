from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from schemas.topics import Topic
from schemas.tasks import Task
from schemas.errors import NotFoundTopic
from utilities.file_scripts import FileUtils

router_topic = APIRouter(
    redirect_slashes=False,
    prefix="/api/topics",
    tags=["topics"],
)


@router_topic.get(
    "/{topic_id}", status_code=200, summary="Read topic syllabus",
    responses={404: {"model": NotFoundTopic}}
)
async def read_topic(topic_id: int) -> Topic or JSONResponse:
    """
    The `list of tasks` endpoint.
    """
    try:
        topics_json = await FileUtils.open_file('topic_index', topic_id=topic_id)
    except IndexError:
        raise HTTPException(status_code=404, detail=NotFoundTopic().error)
    # Get topic by ID
    topic = topics_json[topic_id]
    # Create new topic info object
    topic = Topic(
        topic_id=topic_id, topic_name=topic.get("name"),
        tasks_count=topic.get("count"), tasks=[]
    )
    # Get info about topic's tasks
    for task_id in range(1, topic.tasks_count + 1):
        description = await FileUtils.open_file('task_info', topic_id, task_id)
        inputs = await FileUtils.open_file_values('task_input', topic_id, task_id)
        outputs = await FileUtils.open_file_values('task_output', topic_id, task_id)
        topic.tasks.append(Task(**description, input=list(inputs), output=list(outputs)))
    return topic
