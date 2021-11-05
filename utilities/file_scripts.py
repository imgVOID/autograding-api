"""
`file_scripts` module stores tasks I/O utilities.
"""
import aiofiles
from tempfile import gettempdir
from os import remove, mkdir
from os.path import abspath, join, normpath, dirname
from json import loads, dumps
from random import randint
from typing import List, Iterable


class FileUtils:
    """
    `FileUtils` class stores utilities for saving user input files and file paths.
    """

    @classmethod
    async def _get_filepath(
            cls: 'FileUtils', title: str, topic_id: int = None, task_id: int = None
    ) -> str or None:
        """
        `FileUtils._get_filepath` private class method returns the path to a file by path name.
        It takes three parameters (excluding cls):
        1. `title` has four variants: task_info, task_input, task_output, task_code.
        2. `topic_id` means an id of the topic and the directory name.
        3. `task_id means` an id of the task in a topic and a part of the file name.
        """
        topic_path = None
        if topic_id is not None:
            topic_index = await cls.open_file('topic_index')
            topic_path = topic_index[topic_id].get("path")

        filesystem = {
            "task_info": normpath(abspath(
                join('materials', f'{topic_path}', 'description', f'task_{task_id}.json')
            )),

            "task_input": normpath(abspath(
                join('materials', f'{topic_path}', 'input', f'task_{task_id}.txt')
            )),

            "task_output": normpath(abspath(
                join('materials', f'{topic_path}', 'output', f'task_{task_id}.txt')
            )),

            "task_code": normpath(abspath(
                join('materials', f'{topic_path}', 'code', f'task_{task_id}.txt')
            )),

            "topic_index": normpath(abspath(
                join('materials', f'topics.json')
            ))
        }
        try:
            return filesystem[title]
        except KeyError as e:
            raise ValueError(f'No such get_filepath() mode like "{title}"') from e

    @staticmethod
    async def _write_user_answer_temp(code: bytes) -> str:
        """
        `FileUtils._write_user_answer_temp` private static method
        returns the user input's temp file name.
        It takes one parameter: code, type: bytes.
        """
        async with aiofiles.tempfile.NamedTemporaryFile(
                'wb', delete=False, dir='./temp/'
        ) as f:
            await f.write(code)
            return f.name.split('temp')[1]

    @classmethod
    async def open_file(
            cls: 'FileUtils', title: str, topic_id: int = None, task_id: int = None
    ) -> dict or str:
        """
        `FileUtils.open_file` public class method accesses
        topic index, task description or task code.
        It returns the content of the file read.
        It takes three parameters (excluding cls):
        1. `title` has 3 variants - topic_index, task_info, task_code.
        2. `topic_id` means an id of the topic and the directory name.
        3. `task_id` means an id of the task in a topic and a part of the file name.
        """
        path = await cls._get_filepath(title, topic_id, task_id)
        try:
            async with aiofiles.open(path, encoding='utf-8', mode='r') as f:
                content = await f.read()
                content = content.encode('utf-8')
                if '.json' in f.name:
                    return loads(content)
                elif '.txt' in f.name:
                    return content
                else:
                    raise ValueError('Wrong file extension.')
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f'File not found: title={title}, topic_id={topic_id}, task_id={task_id}'
            ) from e

    @classmethod
    async def open_file_values(
            cls: 'FileUtils', title: str, topic_id: int = None, task_id: int = None
    ) -> List[bytes]:
        """
        `FileUtils.open_file_values` public class method accesses
        task input and task output values.
        It returns the content of the file read, separated by a newline.
        It takes three parameters (excluding cls):
        1. `title` has 2 variants - task_input, task_output.
        2. `topic_id` means an id of the topic and the directory name.
        3. `task_id` means an id of the task in a topic and a part of the file name.
        """
        path = await cls._get_filepath(title, topic_id, task_id)
        async with aiofiles.open(path, encoding='utf-8', mode='r') as f:
            if f.name.endswith('.txt'):
                content = await f.read()
                return content.encode('utf-8').split(b'\n')
            else:
                raise ValueError('Wrong file extension.')

    @classmethod
    async def save_file(
            cls: 'FileUtils', title: str, content: bytes or dict,
            topic_id: int = None, task_id: int = None
    ) -> None:
        """
        `FileUtils.save_file` public class method writes
        topic index, task description or task code to file.
        It takes four parameters (excluding cls):
        1. `title` has 3 variants - topic_index, task_info, task_code.
        2. `content` is the text that will be written to a file.
        3. `topic_id` means an id of the topic and the directory name.
        4. `task_id` means an id of the task in a topic and a part of the file name.
        """
        path = await cls._get_filepath(title, topic_id, task_id)
        async with aiofiles.open(path, encoding='utf-8', mode='w') as f:
            if f.name.endswith('.json'):
                content = dumps(content, ensure_ascii=False)
            elif f.name.endswith('.txt'):
                content = content.decode('utf-8')
            else:
                raise ValueError('Wrong file extension.')
            await f.write(content)

    @classmethod
    async def save_file_values(
            cls: 'FileUtils', title: str, content: Iterable[str],
            topic_id: int = None, task_id: int = None
    ) -> None:
        """
        `FileUtils.save_file_values` public class method writes
        task input and task output values to file.
        It takes four parameters:
        1. `title` has 2 variants - task_input, task_output.
        2. `content` is the text that will be written to a file.
        3. `topic_id` means an id of the topic and the directory name.
        4. `task_id` means an id of the task in a topic and a part of the file name.
        """
        path = await cls._get_filepath(title, topic_id, task_id)
        async with aiofiles.open(path, mode='w', encoding='utf-8') as f:
            if not f.name.endswith('.txt'):
                raise ValueError('Wrong file extension.')
            else:
                for value in content:
                    await f.writelines(f'{value}\n')

    @classmethod
    async def remove_file(
            cls: 'FileUtils', title: str, topic_id: int, task_id: int
    ) -> None:
        """
        `FileUtils.remove_file` public class method removes
        any file related to a task.
        It takes three parameters:
        1. `title` has 5 variants - topic_index, task_info, task_code, task_input, task_output.
        3. `topic_id` means an id of the topic and the directory name.
        4. `task_id` means an id of the task in a topic and a part of the file name.
        """
        path = await cls._get_filepath(title, topic_id, task_id)
        try:
            remove(path)
        except OSError as e:
            raise FileNotFoundError(f'File path can not be removed: {path}') from e

    @classmethod
    async def get_user_answer_temp(
            cls: 'FileUtils', code: bytes,
    ) -> str:
        """
        `FileUtils.save_user_input` public class method saves user input on a disk.
        It returns the name of a file uploaded by the user, and a random number.
        It takes one parameter (excluding cls): code, type: bytes.
        """
        try:
            return await cls._write_user_answer_temp(code)
        except FileNotFoundError:
            try:
                mkdir("./temp")
            except Exception as e:
                raise FileNotFoundError("Something went wrong until the input saving") from e
            else:
                return await cls._write_user_answer_temp(code)

    @classmethod
    async def get_user_answer_file(
            cls: 'FileUtils', topic_id: int, task_id: int, code: bytes, extension: str
    ) -> int:
        """
        `FileUtils.save_user_input` public class method saves user input on a disk.
        It returns the name of a file uploaded by the user, and a random number.
        It takes three parameters (excluding cls):
        1. `code` is the bytes object with the user input untrusted code.
        2. `topic_id` means an id of the topic and the directory name.
        3. `task_id` means an id of the task in a topic and a part of the file name.
        """
        random_id = randint(0, 100000)
        path = abspath(normpath(join(
            'temp', f'task_{topic_id}_{task_id}_{random_id}.{extension}'
        )))
        try:
            async with aiofiles.open(path, encoding='utf-8', mode='w') as f:
                await f.write(code.decode('utf-8'))
        except FileNotFoundError:
            try:
                mkdir("./temp")
            except FileExistsError:
                raise FileNotFoundError("Something went wrong until the input saving")
            else:
                async with aiofiles.open(path, encoding='utf-8', mode='w') as f:
                    await f.write(code.decode('utf-8'))
        finally:
            return random_id
