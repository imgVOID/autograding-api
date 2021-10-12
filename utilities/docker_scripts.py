"""
The `docker_scripts` module stores utilities for creating and maintaining disposable containers. 
"""
import docker
from pathlib import Path
import os


class DockerUtils:
    """
    `DockerUtils` is a collection of utilities for creating and maintaining disposable containers.
    Class attribute `client` stores the client Docker application.
    """
    try:
        client = docker.from_env()
    except docker.errors.DockerException as e:
        print("Docker won't load correctly. \ndocker.errors.DockerException:", e, sep='')

    @staticmethod
    def fix_docker_bug():
        """
        `DockerUtils.fix_docker_bug()` staticmethod making it possible to dynamically define dockerfiles with the BytesIO.
        """
        docker.api.build.process_dockerfile = lambda file, path: ('Dockerfile', file)

    @classmethod
    async def docker_setup(cls, theme_id, task_id, user_input, random_id):
        """
        `DockerUtils.docker_setup()` classmethod returns the result of executing a file in a container.
        """
        answer = ""
        container = None
        dockerfile = f'''
        FROM python:3.9-slim-buster
        COPY {Path().parent}/temp/task_{task_id}_{random_id}.py /
        COPY {Path().parent}/materials/{theme_id}/input/task_{task_id}.txt /
        CMD cat ./task_{task_id}.txt | python -u ./task_{task_id}_{random_id}.py'''
        image = cls.client.images.build(path='.', dockerfile=dockerfile,
                                        nocache=True, rm=True, forcerm=True,
                                        tag=f'task_{theme_id}_{task_id}_{random_id}')[0]
        try:
            container = cls.client.containers.run(image, detach=True, remove=True,
                                                  name=f'task_{theme_id}_{task_id}_{random_id}')
        except docker.errors.ContainerError:
            pass  # TODO: write error message
        finally:
            if Path(user_input).is_file():
                Path(user_input).unlink()
            for line in container.logs(stream=True):
                answer += line.decode('utf-8').strip()
            cls.client.containers.prune()
            cls.client.images.remove(image.id, force=True)
            return answer