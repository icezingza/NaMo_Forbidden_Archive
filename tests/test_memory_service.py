import os
import json
import pytest
from fastapi.testclient import TestClient
from memory_service import app, MemoryManager

# Use a separate test memory file to avoid interfering with the main one
TEST_MEMORY_FILE = "test_memory_protocol.json"

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """
    Fixture to set up and tear down the test environment.

    This fixture runs for every test. It ensures the test memory file
    is clean before each test and removes it after the test completes.
    It also patches the MemoryManager to use this test file.
    """
    # Setup: Ensure the test memory file doesn't exist
    if os.path.exists(TEST_MEMORY_FILE):
        os.remove(TEST_MEMORY_FILE)

    # Patch the memory_manager instance to use the test file
    original_manager = app.dependency_overrides.get('memory_manager')
    app.dependency_overrides['memory_manager'] = MemoryManager(file_path=TEST_MEMORY_FILE)

    yield  # This is where the test runs

    # Teardown: Clean up the test memory file
    if os.path.exists(TEST_MEMORY_FILE):
        os.remove(TEST_MEMORY_FILE)

    # Restore original dependency if it was there
    if original_manager:
        app.dependency_overrides['memory_manager'] = original_manager
    else:
        # If it wasn't there, remove our override
        if 'memory_manager' in app.dependency_overrides:
            del app.dependency_overrides['memory_manager']


def test_recall_with_no_memory_records():
    """
    Test the /recall endpoint when there are no memory records.

    This test ensures that the endpoint returns an empty list and a 200 OK
    status code when the memory file is empty, preventing an IndexError.
    """
    # Arrange: Create an empty memory file
    with open(TEST_MEMORY_FILE, "w") as f:
        json.dump({"records": []}, f)

    client = TestClient(app)

    # Act
    response = client.post("/recall", json={"query": "anything"})

    # Assert
    assert response.status_code == 200
    assert response.json() == []


def test_recall_with_empty_memory_file():
    """
    Test the /recall endpoint when the memory file is completely empty.

    This test ensures that the service can handle an empty JSON file
    without crashing due to a JSONDecodeError.
    """
    # Arrange: Create a completely empty file
    with open(TEST_MEMORY_FILE, "w") as f:
        pass  # Write nothing

    client = TestClient(app)

    # Act
    response = client.post("/recall", json={"query": "anything"})

    # Assert
    assert response.status_code == 200
    assert response.json() == []

def test_recall_with_one_memory_record():
    """
    Test the /recall endpoint when there is only one memory record.

    According to the logic `searchable_records = self.memory['records'][:-1]`,
    this should also return an empty list because the single record is excluded.
    """
    # Arrange: Create a memory file with one record
    with open(TEST_MEMORY_FILE, "w") as f:
        json.dump({"records": [{"content": "test"}]}, f)

    client = TestClient(app)

    # Act
    response = client.post("/recall", json={"query": "anything"})

    # Assert
    assert response.status_code == 200
    assert response.json() == []
