from pydantic import BaseModel, Extra
from typing import Optional
import json


class Task(BaseModel):
    id: None = None
    theme_id: int
    description: list[str]
    input: list[str]
    output: list[str]
    split_values: bool = False

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class TaskUpdate(BaseModel):
    description: Optional[list[str]] = None
    input: Optional[str] = None
    output: Optional[str] = None

    class Config:
        extra = Extra.allow


class TaskAnswer(BaseModel):
    code: str
    language: str
