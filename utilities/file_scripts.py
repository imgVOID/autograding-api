"""
The `file_scripts` module stores utilities for saving user input files and file pathes. 
"""
import random
import aiofiles
from os.path import dirname, abspath, join

APP_ROOT = dirname(dirname(abspath(__file__)))


def get_filepath(title, theme_id, task_id):
    """
    `get_filepath` function returns the path to a file by path name.
    It takes three parameters: 
    1. `title` has four variants: "task_info", "task_input", "task_output", "task_code".
    2. `theme_id` means an id of the theme and the directory name.
    3. `task_id means` an id of the task in a theme and a part of the file name.
    """
    filesystem = {
        "task_info": join(APP_ROOT,
                          'materials', f'{theme_id}',
                          'description', f'task_{task_id}.json'),
        "task_input": join(APP_ROOT,
                           'materials', f'{theme_id}',
                           'input', f'task_{task_id}.txt'),
        "task_output": join(APP_ROOT,
                            'materials', f'{theme_id}',
                            'output', f'task_{task_id}.txt'),
        "task_code": join(APP_ROOT,
                          'materials', f'{theme_id}',
                          'code', f'task_{task_id}.txt'),
    }
    return filesystem.get(title)


async def save_user_input(code, theme, task_id):
    """
    `save_user_input` function  saves user input on a disk.
    It returns the name of a file uploaded by the user, and a random number.
    It takes three parameters: 
    1. `code` is the bytes object with the user input untrusted code.
    2. `theme` means an id of the theme and the directory name.
    3. `task_id` means an id of the task in a theme and a part of the file name.
    """
    random_id = random.randint(0, 100000)
    filename = join(APP_ROOT,
                    f'materials/{theme}/inputs/',
                    f'task_{task_id}_{random_id}.py')
    async with aiofiles.open(filename, encoding='utf-8', mode='w') as f:
        await f.write(code)
    return f.name, random_id
