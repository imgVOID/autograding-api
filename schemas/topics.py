from pydantic import BaseModel
from typing import List
from schemas.tasks import Task


class Topic(BaseModel):
    """
    `Topic` is a pydantic model defining the schema
    for getting a full topic info (including task list) via GET requests.
    """
    topic_id: int
    topic_name: str
    tasks_count: int
    tasks: List[Task]
