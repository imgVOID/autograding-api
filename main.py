from os.path import dirname, abspath
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from routers.tasks import router_tasks
from routers.checks import router_checks, limiter
from routers.topics import router_topic
from routers.auth import router_users
from database.config import database
from schemas.auth import Token
from utilities.docker_scripts import DockerUtils
from utilities.app_metadata import tags_metadata, app_metadata_description
from utilities.auth_scripts import AuthUtils

# FastAPI app instance
app = FastAPI(title='Autograding-API',
              description=app_metadata_description,
              version='0.0.1',
              contact={
                  "name": "Maria Hladka",
                  "url": "https://github.com/imgVOID",
                  "email": "imgvoid@gmail.com",
              },
              license_info={
                  "name": "Apache 2.0",
                  "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
              }, openapi_tags=tags_metadata)

# Save main app directory
APP_ROOT = dirname(abspath(__file__))
# Fix Docker dockerfile problems on the app startup
DockerUtils.fix_docker_bug()

# Connecting routers to the app
app.include_router(router_tasks)
app.include_router(router_checks)
app.include_router(router_topic)
app.include_router(router_users)
# Connecting rate limiter to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/auth/token", response_model=Token, summary="Grab the Bearer token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await AuthUtils.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=AuthUtils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await AuthUtils.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
