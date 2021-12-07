"""
The `docker_scripts` module stores utilities for creating and maintaining disposable containers. 
"""
from os import remove
from os.path import isfile
from typing import Tuple, Optional
from subprocess import Popen, PIPE
from random import randint
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
        raise DockerException("Error accessing the Docker API. Is Docker running?") from e

    @classmethod
    async def _docker_image_build(
            cls: 'DockerUtils', topic_name: str, task_id: int, temp_name: str
    ) -> Tuple[Image, str] or None:
        """
        `DockerUtils._docker_image_build` private class method
        returns an image for the check container.
        """
        user_input_path = f"./temp/{temp_name}"
        dockerfile = f'''
        FROM python:3.9-alpine
        COPY {user_input_path} ./materials/{topic_name}/input/task_{task_id}.txt /
        CMD cat task_{task_id}.txt | python -u {temp_name}
        '''
        image_config = {
            'path': '.', 'dockerfile': dockerfile, 'forcerm': True, 'network_mode': None
        }
        try:
            image = cls.client.images.build(**image_config)[0]
        except BuildError as e:
            print("Failed to build the Docker image.", e)
            return None
        else:
            return image, user_input_path

    @classmethod
    async def _docker_container_run(
            cls: 'DockerUtils', image: Image, topic_name: str, task_id: int, id_random: int
    ) -> str:
        """
        `DockerUtils._docker_container_run` private class method requires a Docker-image
        and returns the result of executing user input in the container.
        """
        answer = ""
        container_config = {
            'detach': True, 'auto_remove': True,
            'stderr': True, 'read_only': True,
            'device_read_iops': 0, 'device_write_iops': 0,
            'name': f'task_{topic_name}_{task_id}_{id_random}'
        }
        try:
            container = cls.client.containers.run(image, **container_config)
        except ContainerError as e:
            raise DockerException("Failed to run container:") from e
        except ImageNotFound as e:
            raise DockerException("Failed to find image:") from e
        except NotFound as e:
            raise DockerException("File not found in the container:") from e
        except APIError as e:
            raise DockerException("Unhandled Docker API error:") from e
        else:
            for line in container.logs(stream=True):
                answer += line.decode('utf-8').strip()
        finally:
            cls.client.images.remove(image.id, force=True)
            return answer

    @classmethod
    async def _docker_container_run_subprocess(
            cls: 'DockerUtils', image: Image, topic_name: str, task_id: int, id_random: int
    ) -> str:
        """
        `DockerUtils._docker_container_run` private class method requires a Docker-image
        and returns the result of executing user input in the container.
        """
        cmd = f'docker run --rm --read-only --name task_{topic_name.lower()}_{task_id}_{id_random} {image.id}'
        try:
            container = Popen(cmd, stdout=PIPE, stderr=PIPE)
        except ContainerError as e:
            raise DockerException("Failed to run container:") from e
        except ImageNotFound as e:
            raise DockerException("Failed to find image:") from e
        except NotFound as e:
            raise DockerException("File not found in the container:") from e
        except APIError as e:
            raise DockerException("Unhandled Docker API error:") from e
        else:
            container.wait()
            answer = b"".join(container.stdout.readlines())
            return answer.decode("utf-8")

    @classmethod
    async def docker_check_user_answer(
            cls: 'DockerUtils', topic_name: str, task_id: int, temp_name: str
    ) -> Optional[str]:
        """
        `DockerUtils.docker_check_user_answer` class method is a public interface method,
        returns the result of executing user input in the Docker container.
        """
        id_random = randint(0, 100)
        image, user_input_path = await cls._docker_image_build(
            topic_name, task_id, temp_name
        )
        if not image:
            return None

        answer = await cls._docker_container_run_subprocess(image, topic_name, task_id, id_random)
        cls.client.images.remove(image.id, force=True)
        remove(user_input_path) if isfile(user_input_path) else None
        return answer

    @staticmethod
    def fix_docker_bug() -> None:
        """
        `DockerUtils.fix_docker_bug` staticmethod making it possible
        to dynamically define dockerfiles with the BytesIO.
        """
        build.process_dockerfile = lambda file, path: ('Dockerfile', file)
