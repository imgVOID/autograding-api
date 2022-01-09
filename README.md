# Autograding API
🚀 Fast and asynchronous API for **automated grading of code assignments.**

[![Gitter](https://badges.gitter.im/python-autograding-api/community.svg)](https://gitter.im/python-autograding-api/community)
[![Open Source Helpers](https://www.codetriage.com/imgvoid/autograding-api/badges/users.svg)](https://www.codetriage.com/imgvoid/python-autograding-api)

1. *FastAPI provides support for OpenAPI 3.0 and Swagger.*
2. *Separate disposable Docker containers to inspect and grade potentially unsafe user input.*
3. *Three working modes: "Python Subprocess", "Python on Whales" and "Python Docker SDK"*
4. *Fully RESTful (CRUD) API for use with a custom frontend.*
5. *Authentication based on the Bearer JWT.*
6. *Asynchronous ORM SQLAlchemy support.*

## API sections:
* **tasks**: CRUD for the programming assignments management.
* **topics**: CRUD for the tasks topics management.
* **checks**: validating user input by running securely in a disposable Docker container. 
* **users**: user management system.

## Requirements:
1. FastAPI.
2. Python Docker SDK (optional).
3. Python on Whales (optional).
4. Pydantic.
5. Aiofiles.
6. Pytest and pytest-asyncio.
7. Uvicorn.
8. Databases (Python module).
9. Httpx.
10. Python-jose.
11. Passlib.
12. Slowapi (optional).

## TODOs:
1. Finish the "topics" section by analogy with the "tasks" section.
2. Improve the sandboxing algorithm using Docker volumes or Docker bind mounts.
