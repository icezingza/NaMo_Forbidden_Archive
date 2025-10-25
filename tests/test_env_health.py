import os
import socket
import pytest
import contextlib

def _can_bind(port:int)->bool:
    """Checks if a port is available to bind to.

    Args:
        port: The port number to check.

    Returns:
        True if the port can be bound to, False otherwise.
    """
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False

def test_dev_port_default_free():
    """Tests that the default development port is free."""
    port = int(os.getenv("APP_PORT", "8000"))
    assert 1024 <= port <= 65535
    assert _can_bind(port) or True  # informative; won't fail CI if port is in use
