"""
The `file_scripts` module stores utilities for saving user input files and file pathes. 
"""
import random
import aiofiles
from os.path import dirname, abspath, join

APP_ROOT = dirname(dirname(abspath(__file__)))


def get_filepath(title, theme_id, task_id):
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
    random_id = random.randint(0, 100000)
    filename = join(APP_ROOT,
                    f'materials/{theme}/inputs/',
                    f'task_{task_id}_{random_id}.py')
    async with aiofiles.open(filename, encoding='utf-8', mode='w') as f:
        await f.write(code)
    return f.name, random_id
