import docker
from os.path import dirname, abspath, exists, join
from os import remove


class DockerUtils:
    try:
        client = docker.from_env()
    except docker.errors.DockerException as e:
        print("Docker does not load correctly.\ndocker.errors.DockerException:", e, sep='')

    @staticmethod
    def fix_docker_bug():
        docker.api.build.process_dockerfile = lambda file, path: ('Dockerfile', file)

    @classmethod
    async def docker_setup(cls, theme_id, task_id, user_input, random_id):
        answer = ""
        container = None
        dockerfile = f'''
        FROM python:3.9-slim-buster
        COPY ./temp/task_{task_id}_{random_id}.py /
        COPY ./materials/{theme_id}/input/task_{task_id}.txt /
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
            if exists(user_input):
                remove(user_input)
            for line in container.logs(stream=True):
                answer += line.decode('utf-8').strip()
            cls.client.containers.prune()
            cls.client.images.remove(image.id, force=True)
            return answer
