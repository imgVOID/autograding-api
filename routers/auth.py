from typing import List
from fastapi import APIRouter, HTTPException, Depends
from database.config import database
from database.models import users
from schemas.auth import User, UserCreate
from utilities.auth_scripts import get_password_hash
from utilities.auth_scripts import get_current_active_user

router_users = APIRouter(
    redirect_slashes=False,
    prefix="/auth/users",
    tags=["users"],
)


@router_users.get("/", response_model=List[User], summary="Read users index")
async def read_users():
    query = "SELECT * FROM users"
    return await database.fetch_all(query)


@router_users.get("/{user_id}/", response_model=User, summary="Read user information by ID")
async def read_user_by_id(user_id: int):
    query = "SELECT * FROM users WHERE id = :id"
    return await database.fetch_one(query=query, values={"id": user_id})


@router_users.get("/me", summary="Read information about the logged in user")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router_users.post("/", response_model=User, summary="Create new user")
async def create_user(user: UserCreate):
    query = "SELECT * FROM users WHERE email = :email"
    if await database.fetch_one(query=query, values={"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    fake_hashed = get_password_hash(password=user.password)
    query = users.insert().values(
        email=user.email, hashed_password=fake_hashed, is_root=user.is_root, is_active=True
    )
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}
