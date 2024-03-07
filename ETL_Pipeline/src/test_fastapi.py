# This file contains tests for FastApi routes.

# Required packages.
from fetch_save import app
from fastapi.testclient import TestClient

# Define testing client.
client = TestClient(app)

def test_get_tasks():
    """ Tests fetching of tasks. """
    response = client.get("/task")
    assert type(response.json()) == list
    assert response.status_code == 200

if __name__ == "__main__":
    tests_failed = {}
    # Running all tests.
    test_get_tasks()
    print('All tests pass!')
