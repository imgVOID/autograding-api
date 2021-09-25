import os
from fastapi import FastAPI
from utilities.docker_scripts import DockerUtils
from routers.tasks import router_tasks
from routers.check import router_check


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = FastAPI()
app.include_router(router_tasks)
app.include_router(router_check)
DockerUtils.fix_docker_bug()

