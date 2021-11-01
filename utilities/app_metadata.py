"""
The `app_metadata` module stores data for formatting metadata in the main.py application file.
"""
tags_metadata = [
    {
        "name": "default",
        "description": "Application area-wide settings",
    },
    {
        "name": "check",
        "description": "Checking if the user's answer is correct: "
                       "running the code safely in a Docker container and comparing the result"
    },
    {
        "name": "tasks",
        "description": "Task management with description, solution code, input and output data",
    },
    {
        "name": "themes",
        "description": "Theme management with description and task list"
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
3. *Fully RESTful (CRUD) API for use with a custom frontend.*\n
4. *Authentication based on Bearer JWT.*\n
5. *Support for asynchronous ORM SQLAlchemy.*\n
* **check**: validating user input by running securely in a disposable Docker container. 
* **tasks**: CRUD for the programming assignments management.
* **themes**: CRUD for the tasks topics management.
* **users**: user management system.
"""
