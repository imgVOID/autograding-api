from pydantic import BaseModel
from typing import List
from schemas.tasks import Task


class Theme(BaseModel):
    """
    `Theme` is a pydantic model defining the schema
    for getting a full theme info (including task list) via GET requests.
    """
    theme_id: int
    theme_name: str
    tasks_count: int
    tasks: List[Task]
