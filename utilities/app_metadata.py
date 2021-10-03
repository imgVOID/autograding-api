"""
The `utilities` module stores data for formatting metadata in the main.py application file.
"""

tags_metadata = [
    {
        "name": "tasks",
        "description": "Task management with description, solution code, input and output data.",
    },
    {
        "name": "check",
        "description": "Checking if the user's answer is correct: "
                       "running the code safely in a Docker container and comparing the result."
    },
]

app_metadata_description = """
### 🚀 Fast and asynchronous automatic assignments grading API:\n
1. *Based on the FastAPI and Python Docker SDK.*\n
2. *Separated one-time Docker containers for the user input check.*\n
3. *Totally RESTful (CRUD) API for use with a custom frontend.*\n
* **Tasks**: CRUD assignments management.
* **Check**: user input validation by the safely run in a disposable Docker container.
"""
