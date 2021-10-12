"""
The `file_scripts` module stores utilities for saving user input files and file pathes. 
"""
from os import remove
from os.path import abspath, join, normpath
from aiofiles import open
from json import loads, dumps
from random import randint


class FileUtils:
    @classmethod
    async def _get_filepath(cls, title, theme_id=None, task_id=None):
        """
        `_get_filepath` private class method returns the path to a file by path name.
        It takes three parameters:
        1. `title` has four variants: "task_info", "task_input", "task_output", "task_code".
        2. `theme_id` means an id of the theme and the directory name.
        3. `task_id means` an id of the task in a theme and a part of the file name.
        """
        if theme_id is not None:
            theme_index = await cls.open_file('theme_index')
            theme_path = theme_index[theme_id].get("path")
        else:
            theme_path = None
        filesystem = {
            "task_info": normpath(abspath(
                join('materials', f'{theme_path}', 'description', f'task_{task_id}.json')
            )).replace("\\tests", ""),

            "task_input": normpath(abspath(
                join('materials', f'{theme_path}', 'input', f'task_{task_id}.txt')
            )).replace("\\tests", ""),

            "task_output": normpath(abspath(
                join('materials', f'{theme_path}', 'output', f'task_{task_id}.txt')
            )).replace("\\tests", ""),

            "task_code": normpath(abspath(
                join('materials', f'{theme_path}', 'code', f'task_{task_id}.txt')
            )).replace("\\tests", ""),

            "theme_index": normpath(abspath(
                join('materials', f'themes.json')
            )).replace("\\tests", ""),

            "theme_index_test": normpath(abspath(
                join('tests', 'data', 'test_themes.json')
            )).replace("\\tests", "")
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
        random_id = randint(0, 100000)
        path = abspath(normpath(join(
            'temp', f'task_{task_id}_{random_id}.{extension}'
        ))).replace("\\tests", "")
        async with open(path, encoding='utf-8', mode='w') as f:
            await f.write(code.decode('utf-8'))
        return path, random_id

    @classmethod
    async def open_file(cls, title, theme_id=None, task_id=None):
        path = await cls._get_filepath(title, theme_id, task_id)
        if path is None:
            raise ValueError(f'No such get_filepath() mode like "{title}"')
        async with open(path, encoding='utf-8', mode='r') as f:
            content = await f.read()
            content = content.encode('utf-8')
            if '.json' in f.name:
                return loads(content)
            elif '.txt' in f.name:
                return content
            else:
                raise ValueError('Wrong file extension.')

    @classmethod
    async def open_file_values(cls, title, theme_id, task_id):
        path = await cls._get_filepath(title, theme_id, task_id)
        if path is None:
            raise ValueError(f'No such get_filepath() mode like "{title}"')
        async with open(path, encoding='utf-8', mode='r') as f:
            if '.txt' in f.name:
                content = await f.read()
                content = content.encode('utf-8').split(b'\n')
                return content
            else:
                raise ValueError('Wrong file extension.')

    @classmethod
    async def save_file(cls, title, content, theme_id=None, task_id=None):
        path = await cls._get_filepath(title, theme_id, task_id)
        if path is None:
            raise ValueError(f'No such get_filepath() mode like "{title}"')
        async with open(path, encoding='utf-8', mode='w') as f:
            if '.json' in f.name:
                content = dumps(content, ensure_ascii=False)
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

    @classmethod
    async def save_file_values(cls, title, theme_id, task_id, content_sequence):
        path = await cls._get_filepath(title, theme_id, task_id)
        if path is None:
            raise ValueError(f'No such get_filepath() mode like "{title}"')
        async with open(path, mode='w', encoding='utf-8') as f:
            if '.txt' in f.name:
                for value in content_sequence:
                    try:
                        await f.writelines(f'{value}\n')
                    except Exception as e:
                        print(e)
            else:
                raise ValueError('Wrong file extension.')

    @classmethod
    async def remove_file(cls, title, theme_id, task_id):
        path = await cls._get_filepath(title, theme_id, task_id)
        if path is None:
            raise ValueError(f'No such get_filepath() mode like "{title}"')
        try:
            remove(path)
        except:
            raise FileNotFoundError(f'File not found: {path}')
