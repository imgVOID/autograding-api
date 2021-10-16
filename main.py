import os
from fastapi import FastAPI
from utilities.docker_scripts import DockerUtils
from routers.tasks import router_tasks
from routers.check import router_check
from utilities.app_metadata import tags_metadata, app_metadata_description

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DockerUtils.fix_docker_bug()

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

app.include_router(router_tasks)
app.include_router(router_check)
