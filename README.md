# Autograding API
🚀 Fast and asynchronous API for **automated grading of code assignments:**
1. *FastAPI provides support for OpenAPI 3.0 and Swagger.*
2. *Separate disposable Docker containers to inspect and grade potentially unsafe user input.*
3. *Three working modes: "Python Subprocess", "Python on Whales" and "Python Docker SDK"*
4. *Fully RESTful (CRUD) API for use with a custom frontend.*
5. *Authentication based on the Bearer JWT.*
6. *Asynchronous ORM SQLAlchemy support.*
* **tasks**: CRUD for the programming assignments management.
* **topics**: CRUD for the tasks topics management.
* **checks**: validating user input by running securely in a disposable Docker container. 
* **users**: user management system.
