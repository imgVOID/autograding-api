from pydantic import BaseModel
from typing import List
from schemas.tasks import Task


class Theme(BaseModel):
    theme_id: int
    theme_name: str
    tasks_count: int
    tasks: List[Task]
