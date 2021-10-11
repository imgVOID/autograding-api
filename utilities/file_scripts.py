"""
The `file_scripts` module stores utilities for saving user input files and file pathes. 
"""
import random
import aiofiles
import json
from os.path import dirname, abspath, join, sep, normpath

APP_ROOT = dirname(dirname(abspath(__file__)))


class FileUtils:

    @staticmethod
    def get_filepath(title, theme_id, task_id):
        """
        `get_filepath` static method returns the path to a file by path name.
        It takes three parameters:
        1. `title` has four variants: "task_info", "task_input", "task_output", "task_code".
        2. `theme_id` means an id of the theme and the directory name.
        3. `task_id means` an id of the task in a theme and a part of the file name.
        """
        filesystem = {
            "task_info": normpath(abspath(
                join('materials', f'{theme_id}', 'description', f'task_{task_id}.json')
            )).replace("\\tests", ""),
            "task_input": normpath(abspath(
                join('materials', f'{theme_id}', 'input', f'task_{task_id}.txt')
            )).replace("\\tests", ""),
            "task_output": normpath(abspath(
                join('materials', f'{theme_id}', 'output', f'task_{task_id}.txt')
            )).replace("\\tests", ""),
            "task_code": normpath(abspath(
                join('materials', f'{theme_id}', 'code', f'task_{task_id}.txt')
            )).replace("\\tests", ""),
        }
        return filesystem.get(title)

    @classmethod
    async def save_user_answer(cls, task_id, code, extension):
        """
        `save_user_input` class method saves user input on a disk.
        It returns the name of a file uploaded by the user, and a random number.
        It takes three parameters:
        1. `code` is the bytes object with the user input untrusted code.
        2. `theme` means an id of the theme and the directory name.
        3. `task_id` means an id of the task in a theme and a part of the file name.
        """
        random_id = random.randint(0, 100000)
        path = abspath(normpath(join(
            'temp', f'task_{task_id}_{random_id}.{extension}'
        ))).replace("\\tests", "")
        async with aiofiles.open(path, encoding='utf-8', mode='w') as f:
            await f.write(code.decode('utf-8'))
        return path, random_id

    @staticmethod
    async def open_file(path):
        async with aiofiles.open(path, encoding='utf-8', mode='r') as f:
            content = await f.read()
            content = content.encode('utf-8')
            if '.json' in f.name:
                return json.loads(content)
            elif '.txt' in f.name:
                return content
            else:
                raise ValueError('Wrong file extension.')

    @staticmethod
    async def save_file(path, content):
        async with aiofiles.open(path, encoding='utf-8', mode='w') as f:
            if '.json' in f.name:
                content = json.dumps(content, ensure_ascii=False)
            elif '.txt' in f.name:
                try:
                    content = content.decode('utf-8')
                except AttributeError:
                    pass
            else:
                raise ValueError('Wrong file extension.')
            try:
                await f.write(content)
            except Exception as e:
                print(e)

    @staticmethod
    async def open_file_values(path):
        async with aiofiles.open(path, encoding='utf-8', mode='r') as f:
            if '.txt' in f.name:
                content = await f.read()
                content = content.encode('utf-8').split(b'\n')
                return content
            else:
                raise ValueError('Wrong file extension.')

    @staticmethod
    async def save_file_values(path, content_sequence):
        async with aiofiles.open(path, mode='w', encoding='utf-8') as f:
            if '.txt' in f.name:
                for value in content_sequence:
                    try:
                        await f.writelines(f'{value}\n')
                    except Exception as e:
                        print(e)
            else:
                raise ValueError('Wrong file extension.')
