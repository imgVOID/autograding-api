from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_root: bool = False


class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool = True
    is_root: bool = False

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
