from typing import List
from fastapi import APIRouter, HTTPException
from database.config import database
from database.models import users
from schemas.auth import User, UserCreate

router_users = APIRouter(
    redirect_slashes=False,
    prefix="/auth/users",
    tags=["users"],
)


@router_users.get("/", response_model=List[User], summary="Get all Users")
async def read_users():
    query = users.select()
    return await database.fetch_all(query)


@router_users.get("/{user_id}/", response_model=User, summary="Get user by ID")
async def read_user_by_id(user_id: int):
    query = "SELECT * FROM users WHERE id = :id"
    return await database.fetch_one(query=query, values={"id": user_id})


@router_users.post("/", response_model=User, summary="Create new user")
async def create_user(user: UserCreate):
    query = "SELECT * FROM users WHERE email = :email"
    if await database.fetch_one(query=query, values={"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    fake_hashed = "fake" + user.password
    query = users.insert().values(
        email=user.email, hashed_password=fake_hashed, is_root=user.is_root, is_active=True
    )
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}
