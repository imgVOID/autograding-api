"""
The `docker_scripts` module stores utilities for creating and maintaining disposable containers. 
"""
from os import remove
from os.path import isfile
from typing import Tuple
from docker import from_env
from docker.api import build
from docker.models.images import Image
from docker.errors import DockerException, ContainerError, NotFound, ImageNotFound, APIError, BuildError


class DockerUtils:
    """
    `DockerUtils` is a collection of utilities for creating and maintaining disposable containers.
    Class attribute `client` stores the client Docker application.
    """
    try:
        client = from_env()
    except DockerException as e:
        print("Error accessing the docker API. Is the Docker running?", e, sep="\n")

    @classmethod
    async def _docker_image_build(
            cls: 'DockerUtils', theme_name: str, theme_id: int,
            task_id: int, random_id: int, extension: str
    ) -> Tuple[Image, str] or None:
        """
        `DockerUtils._docker_image_build()` private class method
        returns an image for the check container.
        """
        user_input_name = f"task_{theme_id}_{task_id}_{random_id}.{extension}"
        user_input_path = f"./temp/{user_input_name}"
        dockerfile = f'''
                    FROM python:3.9-alpine
                    ADD {user_input_path} ./materials/{theme_name}/input/task_{task_id}.txt /
                    CMD cat task_{task_id}.txt | python -u {user_input_name}
                    '''
        try:
            image = cls.client.images.build(
                path='.', dockerfile=dockerfile, nocache=True, rm=True,
                forcerm=True, tag=f'task_{theme_name}_{task_id}_{random_id}'
            )[0]
        except BuildError as e:
            print("Failed to build the Docker image.", e)
            return None
        else:
            return image, user_input_path

    @classmethod
    async def _docker_container_run(
            cls: 'DockerUtils', image: Image, theme_name: str, task_id: int, random_id: int
    ) -> str:
        """
        `DockerUtils._docker_container_run()` private class method requires a Docker-image
        and returns the result of executing user input in the container.
        """
        answer = ""
        try:
            container = cls.client.containers.run(
                image, detach=True, auto_remove=True,
                name=f'task_{theme_name}_{task_id}_{random_id}'
            )
        except ContainerError as e:
            print("Failed to run container:", e)
        except ImageNotFound as e:
            print("Failed to find image:", e)
        except NotFound as e:
            print("File not found in the container:", e)
        except APIError as e:
            print("Unhandled error:", e)
        else:
            for line in container.logs(stream=True):
                answer += line.decode('utf-8').strip()
        finally:
            cls.client.images.remove(image.id, force=True)
            return answer

    @classmethod
    async def docker_check_user_answer(
            cls: 'DockerUtils', theme_name: str, theme_id: int,
            task_id: int, random_id: int, extension: str
    ) -> str:
        """
        `DockerUtils.docker_check_user_answer()` class method is a public interface method,
        returns the result of executing user input in the container.
        """
        image, user_input_path = await cls._docker_image_build(
            theme_name, theme_id, task_id, random_id, extension
        )
        answer = await cls._docker_container_run(image, theme_name, task_id, random_id)
        remove(user_input_path) if isfile(user_input_path) else None
        return answer

    @staticmethod
    def fix_docker_bug() -> None:
        """
        `DockerUtils.fix_docker_bug()` staticmethod making it possible
        to dynamically define dockerfiles with the BytesIO.
        """
        build.process_dockerfile = lambda file, path: ('Dockerfile', file)
