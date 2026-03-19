from __future__ import annotations

from abc import ABC, abstractmethod


class BasePersonaEngine(ABC):
    """Shared interface for all NaMo persona engines.

    Every engine must implement process_input() with the standard return shape.
    Override _build_system_prompt() and get_status() as needed.

    Return shape contract for process_input() — do not break:
    {
        "text": str,
        "media_trigger": {
            "image": str | None,
            "audio": str | None,
            "tts":   str | None,
        },
        "system_status": dict,
    }
    """

    @abstractmethod
    def process_input(self, user_input: str, session_id: str | None = None) -> dict:
        """Process user input and return a structured response.

        All persona engines must implement this method and preserve the
        return shape above. server.py depends on this contract.
        """
        ...

    def _build_system_prompt(self, context: str) -> str:
        """Build the system prompt for the current context.

        Override in subclasses to inject persona-specific instructions.
        The default is a no-op placeholder.
        """
        return f"[{self.__class__.__name__}] context: {context}"

    def get_status(self) -> dict:
        """Return current engine status for health/diagnostics endpoints."""
        return {"engine": self.__class__.__name__, "status": "online"}
