"""
The `app_metadata` module stores data for formatting metadata in the main.py application file.
"""
tags_metadata = [
    {
        "name": "default",
        "description": "Application area-wide settings",
    },
    {
        "name": "tasks",
        "description": "Task management with description, solution code, input and output data",
    },
    {
        "name": "topics",
        "description": "Topic management with description and task list"
    },
    {
        "name": "checks",
        "description": "Checking if the user's answer is correct: "
                       "running the code safely in a Docker container and comparing the result"
    },
    {
        "name": "users",
        "description": "User management section"
    },
]

app_metadata_description = """
### 🚀 Fast and asynchronous API for automated grading of code assignments:\n
1. *FastAPI provides support for OpenAPI 3.0 and Swagger.*\n
2. *Separate disposable Docker containers to inspect and grade potentially unsafe user input.*\n
2. *Three working modes: "Python Subprocess", "Python on Whales" and "Python Docker SDK"*\n
3. *Fully RESTful (CRUD) API for use with a custom frontend.*\n
4. *Authentication based on the Bearer JWT.*\n
5. *Support for asynchronous ORM SQLAlchemy.*\n
* **tasks**: CRUD for the programming assignments management.
* **topics**: CRUD for the tasks topics management.
* **checks**: validating user input by running securely in a disposable Docker container. 
* **users**: user management system.
"""
