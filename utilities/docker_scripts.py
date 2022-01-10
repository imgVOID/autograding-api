"""
The `docker_scripts` module stores utilities for creating and maintaining disposable containers. 
"""
from typing import Tuple, Optional
from subprocess import Popen, PIPE
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE
from random import randint
from docker import from_env
from docker.api import build
from docker.models.images import Image
from docker.errors import DockerException, ContainerError, NotFound, ImageNotFound, APIError, BuildError
from python_on_whales import docker as whale


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
    def _image_build(
            cls: 'DockerUtils', topic_name: str, task_id: int, temp_name: str, id_random
    ) -> Tuple[Image, str] or None:
        """
        `DockerUtils._docker_image_build` private class method
        returns an image for the check container.
        """
        user_input_path = f"./temp/{temp_name}"
        dockerfile = f'''
            FROM python:3.9-alpine
            LABEL type=check
            WORKDIR /
            COPY {user_input_path} ./materials/{topic_name}/input/task_{task_id}.txt /
            CMD cat task_{task_id}.txt | python -u {temp_name}
            '''
        image_config = {
            'path': '.', 'dockerfile': dockerfile, 'forcerm': True, 'network_mode': None,
            'tag': f'{topic_name.lower()}_{str(task_id)}_{str(id_random)}'
        }
        try:
            image = cls.client.images.build(**image_config)[0]
        except BuildError as e:
            print("Failed to build the Docker image.", e)
            return None
        else:
            return image, user_input_path

    @classmethod
    async def _container_run_sdk(
            cls: 'DockerUtils', image: Image, topic_name: str, task_id: int, id_random: int
    ) -> str:
        """
        `DockerUtils._container_run_sdk` private class method requires a Docker-image
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
            return answer.strip()

    @classmethod
    async def _container_run_process(
            cls: 'DockerUtils', image: Image, topic_name: str, task_id: int, id_random: int
    ) -> str:
        """
        `DockerUtils._container_run_process` private class method requires a Docker-image
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
            return answer.decode("utf-8").strip()

    @classmethod
    async def _container_run_process_async(
            cls: 'DockerUtils', image: Image, topic_name: str, task_id: int, id_random: int
    ) -> str:
        """
        `DockerUtils._container_run_process_async` private class method requires a Docker-image
        and returns the result of executing user input in the container.
        """
        cmd = f'docker run --rm --read-only --name task_{topic_name.lower()}_{task_id}_{id_random} {image.id}'
        try:
            container = await create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
        except ContainerError as e:
            raise DockerException("Failed to run container:") from e
        except ImageNotFound as e:
            raise DockerException("Failed to find image:") from e
        except NotFound as e:
            raise DockerException("File not found in the container:") from e
        except APIError as e:
            raise DockerException("Unhandled Docker API error:") from e
        else:
            answer, stderr = await container.communicate()
            return answer.decode("utf-8").strip()

    @classmethod
    async def _container_run_whale(
            cls: 'DockerUtils', image: Image, topic_name: str, task_id: int, id_random: int
    ) -> str:
        """
        `DockerUtils._container_run` private class method requires a Docker-image
        and returns the result of executing user input in the container.
        """
        config = {
            "image": image.id,
            "name": f'task_{topic_name.lower()}_{task_id}_{id_random}',
        }
        try:
            with whale.run(**config, detach=True) as container:
                output = container.logs()
        except ContainerError as e:
            raise DockerException("Failed to run container:") from e
        else:
            whale.image.remove(image.id, force=True)
            return output.strip()

    @classmethod
    async def docker_check_user_answer(
            cls: 'DockerUtils', topic_name: str, task_id: int, temp_name: str
    ) -> Optional[Tuple[str, int]]:
        """
        `DockerUtils._check_user_answer` class method is a public interface method,
        returns the result of executing user input in the Docker container.
        """
        id_random = randint(0, 100)
        image, user_input_path = cls._image_build(
            topic_name, task_id, temp_name, id_random
        )

        return (
            await cls._container_run_process_async(image, topic_name, task_id, id_random), id_random
        ) if image else None
        # return (await cls._container_run_process(image, topic_name, task_id, id_random), id_random) if image else None
        # return (await cls._container_run_sdk(image, topic_name, task_id, id_random), id_random) if image else None
        # return (await cls._container_run_whale(image, topic_name, task_id, id_random), id_random) if image else None

    @classmethod
    async def image_remove(
            cls: 'DockerUtils', topic_name: str, task_id: int, mode: str
    ) -> None:
        async def sdk():
            tag = f"{topic_name.lower()}_{str(task_id)}"
            return cls.client.images.remove(tag, force=True)

        async def process():
            Popen(f'docker image prune -a --force --filter "label=type=check"')

        modes = {
            'sdk': sdk, 'process': process, 'whale': None
        }
        try:
            await modes[mode]()
        except TypeError:
            pass
        except KeyError as e:
            raise ValueError("You need to specify the mode: 'whale', 'sdk', 'processing'") from e

    @staticmethod
    def fix_docker_bug() -> None:
        """
        `DockerUtils.fix_docker_bug` staticmethod making it possible
        to dynamically define dockerfiles with the BytesIO.
        """
        build.process_dockerfile = lambda file, path: ('Dockerfile', file)
