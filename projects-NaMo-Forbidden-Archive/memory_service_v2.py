import json
import os
from typing import Any


class MemoryServiceV2:
    def __init__(self, use_gcs: bool = False, bucket_name: str | None = None):
        """
        Pluggable memory service that persists state.
        Supports local file system storage (for local testing/PocketPal)
        or Google Cloud Storage (GCS) (for Google Cloud Run serverless deployment).
        """
        self.use_gcs = use_gcs or os.getenv("USE_GCS", "false").lower() == "true"
        self.bucket_name = bucket_name or os.getenv("GCS_BUCKET_NAME")
        self.local_storage_dir = os.getenv("LOCAL_STORAGE_DIR", "/tmp/sessions")

        if not os.path.exists(self.local_storage_dir) and not self.use_gcs:
            os.makedirs(self.local_storage_dir, exist_ok=True)

        if self.use_gcs:
            if not self.bucket_name:
                print(
                    "Warning: USE_GCS is True, but GCS_BUCKET_NAME is not set. Falling back to local storage."
                )
                self.use_gcs = False
            else:
                try:
                    from google.cloud import storage

                    self.gcs_client = storage.Client()
                    self.bucket = self.gcs_client.bucket(self.bucket_name)
                    print(f"GCS Storage enabled using bucket: {self.bucket_name}")
                except Exception as e:
                    print(
                        f"Warning: Failed to initialize Google Cloud Storage Client: {e}. Falling back to local storage."
                    )
                    self.use_gcs = False

    def _get_local_path(self, session_id: str) -> str:
        return os.path.join(self.local_storage_dir, f"{session_id}.json")

    async def get_session_state(self, session_id: str) -> dict[str, Any]:
        """
        Load the current session state.
        Returns the initial default state if no session exists yet.
        """
        default_state = {
            "session_id": session_id,
            "relationship_stage": 1,
            "stage_progress": "0/25",
            "emotion_state": {
                "arousal": 0.2,
                "trust": 0.4,
                "passion": 0.1,
                "temperament": 0.7,
                "resonance": 0.3,
            },
            "history": [],
        }

        if self.use_gcs:
            try:
                blob = self.bucket.blob(f"sessions/{session_id}.json")
                if blob.exists():
                    data = blob.download_as_text()
                    return json.loads(data)
            except Exception as e:
                print(f"Error reading session {session_id} from GCS: {e}")
        else:
            local_path = self._get_local_path(session_id)
            if os.path.exists(local_path):
                try:
                    with open(local_path, encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    print(f"Error reading session {session_id} from local disk: {e}")

        return default_state

    async def save_interaction(
        self, session_id: str, user_message: str, response_data: dict[str, Any]
    ):
        """
        Save the transaction, update the session history, and persist the new state.
        """
        # Load existing state
        state = await self.get_session_state(session_id)

        # Update core state parameters from the LLM response
        state["relationship_stage"] = response_data.get(
            "relationship_stage", state["relationship_stage"]
        )
        state["stage_progress"] = response_data.get("stage_progress", state["stage_progress"])
        state["emotion_state"] = response_data.get("emotion_state", state["emotion_state"])

        # Append new exchange to history (limit to last 20 turns to conserve token budget)
        new_turn = {
            "user": user_message,
            "vipha": response_data.get("narrative", ""),
            "hook": response_data.get("hook", ""),
        }
        state["history"].append(new_turn)
        if len(state["history"]) > 20:
            state["history"] = state["history"][-20:]

        # Save to storage (GCS or Local)
        if self.use_gcs:
            try:
                blob = self.bucket.blob(f"sessions/{session_id}.json")
                blob.upload_from_string(
                    json.dumps(state, ensure_ascii=False, indent=2), content_type="application/json"
                )
            except Exception as e:
                print(f"Error uploading session {session_id} to GCS: {e}")
        else:
            local_path = self._get_local_path(session_id)
            try:
                with open(local_path, "w", encoding="utf-8") as f:
                    json.dump(state, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Error writing session {session_id} to local disk: {e}")

    async def retrieve_context(self, query: str, session_id: str, max_tokens: int = 500) -> str:
        """
        Compiles the historical context from the last few turns of discussion.
        """
        state = await self.get_session_state(session_id)
        history = state.get("history", [])
        if not history:
            return ""

        context_lines = []
        for i, turn in enumerate(history[-5:]):  # Grab the last 5 turns for immediate context
            context_lines.append(
                f"Turn {i + 1}:\nUser: {turn['user']}\nVipha: {turn['vipha']}\nHook: {turn['hook']}"
            )

        return "\n\n".join(context_lines)


# Alias for backward compatibility
MemoryService = MemoryServiceV2
