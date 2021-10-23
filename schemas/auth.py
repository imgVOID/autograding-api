from pydantic import BaseModel, EmailStr


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
