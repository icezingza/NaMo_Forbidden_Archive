import json
import os
import sys

# Ensure project root is on sys.path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

from memory_service import MemoryManager, app, get_memory_manager

# Use a separate test memory file to avoid interfering with the main one
TEST_MEMORY_FILE = "test_memory_protocol.json"


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Sets up and tears down the test environment.

    This fixture runs for every test. It ensures the test memory file
    is clean before each test and removes it after the test completes.
    It also patches the MemoryManager to use this test file.
    """
    # Setup: Ensure the test memory file doesn't exist
    if os.path.exists(TEST_MEMORY_FILE):
        os.remove(TEST_MEMORY_FILE)

    # Patch the dependency to use the test file
    test_manager = MemoryManager(file_path=TEST_MEMORY_FILE)
    original_override = app.dependency_overrides.get(get_memory_manager)
    app.dependency_overrides[get_memory_manager] = lambda: test_manager

    yield  # This is where the test runs

    # Teardown: Clean up the test memory file
    if os.path.exists(TEST_MEMORY_FILE):
        os.remove(TEST_MEMORY_FILE)

    # Restore original dependency if it was there
    if original_override is not None:
        app.dependency_overrides[get_memory_manager] = original_override
    elif get_memory_manager in app.dependency_overrides:
        del app.dependency_overrides[get_memory_manager]


def test_recall_with_no_memory_records():
    """Tests the /recall endpoint with no memory records."""
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
    """Tests the /recall endpoint with an empty memory file."""
    # Arrange: Create a completely empty file
    with open(TEST_MEMORY_FILE, "w"):
        pass  # Write nothing

    client = TestClient(app)

    # Act
    response = client.post("/recall", json={"query": "anything"})

    # Assert
    assert response.status_code == 200
    assert response.json() == []


def test_recall_with_one_memory_record():
    """Tests the /recall endpoint with one memory record."""
    # Arrange: Create a memory file with one record
    with open(TEST_MEMORY_FILE, "w") as f:
        json.dump({"records": [{"content": "test"}]}, f)

    client = TestClient(app)

    # Act
    response = client.post("/recall", json={"query": "anything"})

    # Assert
    assert response.status_code == 200
    assert response.json() == []


def test_store_and_recall_returns_previous_entries():
    """Tests that recalling skips the latest message but returns earlier ones."""
    client = TestClient(app)

    first = client.post("/store", json={"content": "first"}).json()
    assert first["content"] == "first"

    second = client.post("/store", json={"content": "second"}).json()
    assert second["content"] == "second"

    response = client.post("/recall", json={"query": "anything", "limit": 10})
    assert response.status_code == 200
    data = response.json()
    # Latest record is skipped, so only the first should appear
    assert len(data) == 1
    assert data[0]["content"] == "first"


def test_recall_filters_by_memory_type():
    """Tests that the /recall endpoint correctly filters by memory_types."""
    client = TestClient(app)

    # Arrange: Store records with different types
    client.post("/store", json={"content": "short term memory", "type": "short-term"})
    client.post("/store", json={"content": "long term memory", "type": "long-term"})
    client.post("/store", json={"content": "contextual memory", "type": "contextual"})
    # This last one will be skipped by recall
    client.post("/store", json={"content": "another short term", "type": "short-term"})

    # Act: Recall with a filter for 'long-term'
    response = client.post("/recall", json={"memory_types": ["long-term"]})
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["content"] == "long term memory"
    assert data[0]["type"] == "long-term"


def test_recall_filters_by_dark_concepts():
    """Tests that the /recall endpoint correctly filters by dark_concepts_filter."""
    client = TestClient(app)

    # Arrange: Store records with different dharma_tags
    client.post(
        "/store", json={"content": "obsession memory", "dharma_tags": ["metta"]}
    )  # -> Obsession  # noqa: E501
    client.post(
        "/store", json={"content": "suffering memory", "dharma_tags": ["dukkha"]}
    )  # -> Managed Suffering  # noqa: E501
    client.post(
        "/store", json={"content": "detachment memory", "dharma_tags": ["upekkha"]}
    )  # -> Cold Detachment  # noqa: E501
    # This last one will be skipped by recall
    client.post("/store", json={"content": "another obsession", "dharma_tags": ["metta"]})

    # Act: Recall with a filter for 'Obsession' and 'Managed Suffering'
    response = client.post(
        "/recall", json={"dark_concepts_filter": ["Obsession", "Managed Suffering"]}
    )  # noqa: E501
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert len(data) == 2
    # The order is chronological
    contents = {item["content"] for item in data}
    assert "obsession memory" in contents
    assert "suffering memory" in contents
    assert "detachment memory" not in contents


def test_recall_with_combined_filters():
    """Tests that the /recall endpoint works with combined filters."""
    client = TestClient(app)

    # Arrange
    client.post(
        "/store",
        json={"content": "long term obsession", "type": "long-term", "dharma_tags": ["metta"]},
    )  # noqa: E501
    client.post(
        "/store",
        json={"content": "short term obsession", "type": "short-term", "dharma_tags": ["metta"]},
    )  # noqa: E501
    client.post(
        "/store",
        json={"content": "long term suffering", "type": "long-term", "dharma_tags": ["dukkha"]},
    )  # noqa: E501
    # This last one will be skipped by recall
    client.post("/store", json={"content": "another record"})

    # Act: Recall with filters for type 'long-term' and concept 'Obsession'
    response = client.post(
        "/recall", json={"memory_types": ["long-term"], "dark_concepts_filter": ["Obsession"]}
    )  # noqa: E501
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["content"] == "long term obsession"


def test_recall_with_filter_that_matches_nothing():
    """Tests that recall returns an empty list when filters match no records."""
    client = TestClient(app)

    # Arrange
    client.post("/store", json={"content": "record 1", "type": "type-A"})
    client.post("/store", json={"content": "record 2", "type": "type-B"})
    # This last one will be skipped by recall
    client.post("/store", json={"content": "record 3"})

    # Act: Recall with a filter that won't match anything
    response = client.post("/recall", json={"memory_types": ["type-C"]})
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data == []


def test_get_memory_manager_returns_instance():
    """get_memory_manager() returns a MemoryManager instance directly."""
    manager = get_memory_manager()
    assert isinstance(manager, MemoryManager)


def test_store_returns_500_on_internal_error():
    """store endpoint returns HTTP 500 when store_record raises an unexpected error."""
    from unittest.mock import MagicMock

    broken_manager = MagicMock()
    broken_manager.store_record.side_effect = RuntimeError("disk full")

    client = TestClient(app)
    app.dependency_overrides[get_memory_manager] = lambda: broken_manager
    try:
        response = client.post("/store", json={"content": "test"})
        assert response.status_code == 500
        assert "disk full" in response.json()["detail"]
    finally:
        app.dependency_overrides.pop(get_memory_manager, None)


def test_recall_returns_500_on_internal_error():
    """recall endpoint returns HTTP 500 when recall_records raises an unexpected error."""
    from unittest.mock import MagicMock

    broken_manager = MagicMock()
    broken_manager.recall_records.side_effect = RuntimeError("index corrupt")

    client = TestClient(app)
    app.dependency_overrides[get_memory_manager] = lambda: broken_manager
    try:
        response = client.post("/recall", json={"query": "test"})
        assert response.status_code == 500
        assert "index corrupt" in response.json()["detail"]
    finally:
        app.dependency_overrides.pop(get_memory_manager, None)


def test_health_check_endpoint():
    """GET /health returns status ok and memory record count."""
    client = TestClient(app)
    client.post("/store", json={"content": "health test record"})
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["memory_records"], int)
    assert data["memory_records"] >= 1


def test_datetime_encoder_non_datetime_fallback(tmp_path):
    """DateTimeEncoder falls back to base encoder for non-datetime objects."""

    from memory_service import MemoryManager

    manager = MemoryManager(file_path=str(tmp_path / "enc_test.json"))
    # Inject a non-serializable object directly into memory
    manager.memory["records"] = [{"content": "ok"}]
    # Normal save should work fine
    manager.save_memory()

    # Now inject a truly non-serializable object to trigger the fallback branch
    manager.memory["records"] = [{"bad": object()}]
    with pytest.raises((TypeError, Exception)):
        manager.save_memory()
