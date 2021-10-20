from json import loads
from pydantic import BaseModel
from typing import Optional, List


class NotFoundMessage(BaseModel):
    message: str = "Task not found"


class Task(BaseModel):
    id: int
    theme_id: int
    title: str
    description: list[str]
    input: list[str]
    output: list[str]

    class Config:
        schema_extra = {
            "example": {
                "id": 0,
                "theme_id": 0,
                "title": "string",
                "description": ["Task's essence.",
                                "Separated by a newline."],
                "input": ["First input", "2"],
                "output": ["First output", "2"],
            }
        }


class TaskList(BaseModel):
    theme_id: int
    theme_name: str
    tasks_count: int
    tasks: List[Task]


class TaskCreate(BaseModel):
    title: str
    description: list[str]
    input: list[str]
    output: list[str]

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**loads(value))
        return value

    class Config:
        schema_extra = {
            "example": {
                "theme_id": 0,
                "title": "string",
                "description": ["Task's essence.",
                                "Separated by a newline."],
                "input": ["First input", "2"],
                "output": ["First output", "2"],
            }
        }


class TaskUpdate(BaseModel):
    title: str
    description: Optional[list[str]] = None
    input: Optional[list[str]] = None
    output: Optional[list[str]] = None

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**loads(value))
        return value

    class Config:
        extra = 'allow'
        schema_extra = {
            "example": {
                "title": "string",
                "description": ["If you want to change only the code",
                                "please send an empty dict."],
                "input": ["First input", "2"],
                "output": ["First output", "2"],
            }
        }
