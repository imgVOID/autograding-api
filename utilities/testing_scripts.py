import aiofiles
import json
from os.path import abspath, dirname, join


async def get_simple_code():
    simple_code = b"""
print("OK")
print("OK")
print("OK")
"""
    return simple_code


async def get_themes_counter():
    async with aiofiles.open(join(dirname(dirname(abspath(__file__))),
                                  'tests', 'data', 'test_themes.json'),
                             mode='r', encoding='utf-8') as f:
        themes = await f.read()
        return json.loads(themes)[0].get("count")
