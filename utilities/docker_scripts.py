"""
The `docker_scripts` module stores utilities for creating and maintaining disposable containers. 
"""
from pathlib import Path
from docker import from_env
from docker.api import build
from docker.errors import DockerException, ContainerError


class DockerUtils:
    """
    `DockerUtils` is a collection of utilities for creating and maintaining disposable containers.
    Class attribute `client` stores the client Docker application.
    """
    try:
        client = from_env()
    except DockerException as e:
        print("Docker won't load correctly. \ndocker.errors.DockerException:", e, sep='')

    @staticmethod
    def fix_docker_bug():
        """
        `DockerUtils.fix_docker_bug()` staticmethod making it possible to dynamically define dockerfiles with the BytesIO.
        """
        build.process_dockerfile = lambda file, path: ('Dockerfile', file)

    @classmethod
    async def docker_setup(cls, theme_name, task_id, user_input, random_id, extension):
        """
        `DockerUtils.docker_setup()` class method returns the result of executing a file in a container.
        """
        answer = ""
        container = None
        dockerfile = f'''
            FROM python:3.8-alpine
            ADD {Path().parent}/temp/task_{task_id}_{random_id}.{extension} /
            ADD {Path().parent}/materials/{theme_name}/input/task_{task_id}.txt /
            CMD cat ./task_{task_id}.txt | python -u ./task_{task_id}_{random_id}.{extension}
            '''
        image = cls.client.images.build(path='.', dockerfile=dockerfile,
                                        nocache=True, rm=True, forcerm=True,
                                        tag=f'task_{theme_name}_{task_id}_{random_id}')[0]
        try:
            container = cls.client.containers.run(image, detach=True, auto_remove=True,
                                                  name=f'task_{theme_name}_{task_id}_{random_id}')
        except ContainerError:
            pass  # TODO: write error message
        finally:
            if Path(user_input).is_file():
                Path(user_input).unlink()
            for line in container.logs(stream=True):
                answer += line.decode('utf-8').strip()
            cls.client.images.remove(image.id, force=True)
            return answer
