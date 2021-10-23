"""
`schemas.errors` module defines pydantic models for different error responses.
"""
from pydantic import BaseModel


class NotFoundTask(BaseModel):
    error: str = "Task not found by ID"


class NotFoundTheme(BaseModel):
    error: str = "Theme not found by ID"


class RateLimitExceeded(BaseModel):
    error: str = "Rate limit exceeded: 2 per 1 minute"


class DockerUnavailable(BaseModel):
    error: str = "Docker problems, please try again later."


class EmptyRequest(BaseModel):
    error: str = "The request was empty"


class InactiveUser(BaseModel):
    error: str = "Inactive user"


class EmailAlreadyTaken(BaseModel):
    error: str = "Email already registered"
