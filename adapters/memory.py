import os
from typing import Any

import requests


class MemoryAdapter:
    """
    Adapter for interacting with the external Memory Service.
    """

    def __init__(self):
        self.api_url = os.environ.get("MEMORY_API_URL", "http://localhost:8081/store")
        print(f"[MemoryAdapter]: Initialized. API URL: {self.api_url}")

    def store_interaction(
        self, session_id: str, user_input: str, response: str, desire_map: dict[str, Any]
    ):
        """
        Stores a user interaction in the Memory Service.
        """
        payload = {
            "session_id": session_id,
            "user_input": user_input,
            "response": response,
            "desire_map": desire_map,
        }
        try:
            requests.post(self.api_url, json=payload, timeout=2)
            print(f"[MemoryAdapter]: Stored interaction for session {session_id}.")
        except requests.exceptions.RequestException as e:
            print(f"[MemoryAdapter]: ERROR - Could not store interaction: {e}")
