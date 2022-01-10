from os.path import abspath, dirname, join
from ..mixins import TestAuthMixin


class TestTasksCRUDSync(TestAuthMixin):
    def test_task_create(self):
        with open(join(dirname(abspath(__file__)), 'data', 'new_task.json'),
                  mode='r', encoding='utf-8') as f:
            name = f.name
            description = f.read()
        files = {
            'task': (None, bytes(description, 'utf-8')),
            'code': (f'{name}', b'print("OK")\nprint("OK")\nprint("OK")\n'),
        }

        response = self.client.post("/api/tasks/0", files=files, headers=self.headers)
        self.__class__.tasks_count = response.json()["id"]

        assert response.status_code == 201
        assert response.json().get("title") == 'string'
        assert response.json().get("topic_id") == 0

    def test_task_read(self):
        response = self.client.get(
            f"/api/tasks/0/1"
        )
        content = response.json()

        assert response.status_code == 200
        assert isinstance(content["id"], int)
        assert isinstance(content["topic_id"], int)
        assert isinstance(content["description"], list)

    def test_task_update(self):
        files = {"task": (None, b'{"title": "", "description": ["test"], '
                                b'"input": [], "output": []}'),
                 "code": b'print("OK")\nprint("OK")\nprint("OK")\n'}

        response = self.client.patch(
            f"/api/tasks/0/{self.tasks_count}", files=files, headers=self.headers
        )
        content = response.json()

        assert response.status_code == 200
        assert content.get("id") == self.tasks_count
        assert content.get("topic_id") == 0
        assert content.get("description") == ["test"]
        assert not content.get("title")
        assert not content.get("input")
        assert not content.get("output")

    def test_task_delete(self):
        response = self.client.delete(
            f"/api/tasks/0/{self.tasks_count}", params={"test": True}, headers=self.headers
        )
        assert response.status_code == 204


class TestTasksErrorsSync(TestAuthMixin):
    def test_task_read_not_found(self):
        response_not_found_task = self.client.get(f"/api/tasks/0/9999")

        response_not_found_topic = self.client.get(f"/api/tasks/9999/9999")

        assert response_not_found_task.status_code == 404
        assert response_not_found_topic.status_code == 404
        assert response_not_found_task.json()["detail"] == "Task not found by ID"
        assert response_not_found_topic.json()["detail"] == "Topic not found by ID"

    def test_task_create_not_found(self):
        with open(join(dirname(abspath(__file__)), 'data', 'new_task.json'),
                  mode='r', encoding='utf-8') as f:
            name = f.name
            description = f.read()
            response_not_found_topic = self.client.post("/api/tasks/9999", files={
                'task': (None, bytes(description, 'utf-8')),
                'code': (f'{name}', b'print("OK")\nprint("OK")\nprint("OK")\n'),
            }, headers=self.headers)
        assert response_not_found_topic.status_code == 404
        assert response_not_found_topic.json()["detail"] == "Topic not found by ID"

    def test_task_update_not_found(self):
        files = {"task": (None, b'{"title": "", "description": ["string"], '
                                b'"input": [], "output": []}'),
                 "code": b''}
        response_not_found_task = self.client.patch(
            f"/api/tasks/0/9999", files=files, headers=self.headers
        )

        files = {"task": (None, b'{"title": "", "description": ["string"], '
                                b'"input": [], "output": []}'),
                 "code": b''}
        response_not_found_topic = self.client.patch(
            f"/api/tasks/9999/9999", files=files, headers=self.headers
        )

        assert response_not_found_task.status_code == 404
        assert response_not_found_topic.status_code == 404
        assert response_not_found_task.json()["detail"] == "Task not found by ID"
        assert response_not_found_topic.json()["detail"] == "Topic not found by ID"

    def test_task_delete_not_found(self):
        response_not_found_task = self.client.delete(
            f"/api/tasks/0/999", params={"test": True}, headers=self.headers
        )
        response_not_found_topic = self.client.delete(
            f"/api/tasks/999/999", params={"test": True}, headers=self.headers
        )
        assert response_not_found_task.status_code == 404
        assert response_not_found_task.json()["detail"] == "Task not found by ID"
        assert response_not_found_topic.status_code == 404
        assert response_not_found_topic.json()["detail"] == "Topic not found by ID"

    def test_task_update_empty_request(self):
        files = {"task": (None, b'{"title": "", "description": [], '
                                b'"input": [], "output": []}'),
                 "code": b''}
        response_not_found_task = self.client.patch(
            f"/api/tasks/0/999", files=files, headers=self.headers
        )

        assert response_not_found_task.status_code == 422
        assert response_not_found_task.json()["detail"] == "The request was empty"
