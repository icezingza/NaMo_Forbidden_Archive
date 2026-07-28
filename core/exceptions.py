"""Custom exceptions and helpers for consistent, client-safe error handling.

All application errors surfaced through the API inherit from ``NamoAPIError``.
Each carries a stable ``error_code`` (machine-readable) and an HTTP ``status_code``.
The ``message`` is safe, user-facing text; ``detail`` holds diagnostic context that
is only exposed to clients when running in debug mode.
"""


class NamoAPIError(Exception):
    """Base class for errors that map to a structured API response."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str = "Something went wrong", *, detail: str | None = None):
        super().__init__(message)
        self.message = message
        self.detail = detail


class AuthenticationError(NamoAPIError):
    """Missing or invalid credentials."""

    status_code = 401
    error_code = "AUTHENTICATION_ERROR"


class RateLimitError(NamoAPIError):
    """Client exceeded the configured request rate."""

    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"


class EngineError(NamoAPIError):
    """A persona engine failed to produce a response."""

    status_code = 502
    error_code = "ENGINE_ERROR"


class MemoryServiceError(NamoAPIError):
    """The memory service is unavailable or returned an error."""

    status_code = 502
    error_code = "MEMORY_SERVICE_ERROR"


def error_payload(error: str, error_code: str, detail: str | None = None) -> dict[str, object]:
    """Build the canonical error response body.

    ``detail`` is omitted entirely when ``None`` so production responses never leak
    diagnostic context or stack traces.
    """
    body: dict[str, object] = {"success": False, "error": error, "error_code": error_code}
    if detail is not None:
        body["detail"] = detail
    return body
