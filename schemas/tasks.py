from json import loads
from pydantic import BaseModel
from typing import Optional, List


class Task(BaseModel):
    """
    `Task` is a pydantic model defining the schema
    for getting a full task info via GET requests.
    """
    id: int
    topic_id: int
    title: str
    description: List[str]
    input: List[str]
    output: List[str]

    class Config:
        schema_extra = {
            "example": {
                "id": 0,
                "topic_id": 0,
                "title": "string",
                "description": ["Task's essence.",
                                "Separated by a newline."],
                "input": ["First input", "2"],
                "output": ["First output", "2"],
            }
        }


class TaskCreate(BaseModel):
    """
    `TaskCreate` is a pydantic model defining the schema
    to create a new task via POST requests.
    """
    title: str
    description: List[str]
    input: List[str]
    output: List[str]

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
                "title": "string",
                "description": ["Task's essence.",
                                "Separated by a newline."],
                "input": ["First input", "2"],
                "output": ["First output", "2"],
            }
        }


class TaskUpdate(BaseModel):
    """
    `TaskUpdate` is a pydantic model defining the schema
    to full or partial update a task via PUT requests.
    """
    title: str
    description: Optional[List[str]] = None
    input: Optional[List[str]] = None
    output: Optional[List[str]] = None

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
