from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from schemas.auth import UserInDB, User, TokenData
from schemas.errors import InactiveUser, NoUserEmail
from database.config import database


class AuthUtils:
    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

    @classmethod
    def _verify_password(cls, plain_password, hashed_password):
        return cls.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def _get_user(email: str):
        query = "SELECT * FROM users WHERE email = :email"
        user = await database.fetch_one(query=query, values={"email": email})
        if not user:
            raise HTTPException(status_code=400, detail=NoUserEmail().error)
        return UserInDB(**user)

    @classmethod
    async def get_current_user(cls, token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = await cls._get_user(token_data.username)
        if user is None:
            raise credentials_exception
        return user

    @classmethod
    def get_password_hash(cls, password):
        return cls.pwd_context.hash(password)

    @classmethod
    async def create_access_token(cls, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt

    @classmethod
    async def authenticate_user(cls, email: str, password: str):
        user = await cls._get_user(email)
        if not user:
            return False
        if not cls._verify_password(password, user.hashed_password):
            return False
        return user


# FastAPI Dependency
async def get_current_active_user(current_user: User = Depends(AuthUtils.get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail=InactiveUser().error)
    return current_user
