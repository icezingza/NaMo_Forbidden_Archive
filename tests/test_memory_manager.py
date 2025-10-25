import os
import pytest
from memory_service import MemoryManager

TEST_FILE = "test_direct_memory.json"

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Ensure the test file is cleaned up before and after the test."""
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

def test_load_memory_with_empty_file_is_handled():
    """
    Tests that MemoryManager correctly handles a completely empty file
    by initializing with an empty memory structure.
    """
    # Arrange: Create a completely empty file.
    with open(TEST_FILE, "w") as f:
        pass  # Write nothing.

    # Act: Instantiate the manager. This should not raise an exception.
    manager = MemoryManager(file_path=TEST_FILE)

    # Assert: The memory should be initialized to a default empty state.
    assert manager.memory == {"records": [], "protocol_metadata": {}}
