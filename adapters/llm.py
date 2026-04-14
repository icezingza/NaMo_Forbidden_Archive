"""Shared LLM adapter for all NaMo persona engines.

Wraps the OpenAI chat completions API with consistent error handling and a
single point of configuration.  Import and instantiate once per engine:

    from adapters.llm import LLMAdapter
    self.llm = LLMAdapter()

Then call ``llm.complete(messages)`` or iterate over ``llm.stream(messages)``.
"""

from __future__ import annotations

from typing import Any

from config import settings

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore[assignment,misc]


class LLMAdapter:
    """Thin, mockable wrapper around OpenAI chat completions.

    Reads all configuration from ``config.settings``.  If the required
    credentials or package are absent the adapter degrades gracefully:
    ``available`` returns False and every call returns None / yields nothing.
    """

    def __init__(self) -> None:
        self._client = None
        if not settings.namo_llm_enabled:
            return
        if OpenAI is None:
            print("[LLMAdapter]: openai package not installed — LLM disabled.")
            return
        if not settings.openai_api_key:
            print("[LLMAdapter]: OPENAI_API_KEY not set — LLM disabled.")
            return
        try:
            self._client = OpenAI(api_key=settings.openai_api_key)
            print("[LLMAdapter]: OpenAI client ready.")
        except Exception as exc:
            print(f"[LLMAdapter]: init failed: {exc}")

    @property
    def available(self) -> bool:
        """True when the underlying OpenAI client is initialised and ready."""
        return self._client is not None

    def complete(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str | None:
        """Send a single chat completion request.

        Returns the assistant content string, or ``None`` on any failure.
        """
        if not self._client:
            return None
        try:
            response = self._client.chat.completions.create(
                model=model or settings.namo_llm_model,
                messages=messages,
                temperature=(
                    temperature if temperature is not None else settings.namo_llm_temperature
                ),  # noqa: E501
                max_tokens=max_tokens or settings.namo_llm_max_tokens,
            )
            content = response.choices[0].message.content if response.choices else None
            return content.strip() if content else None
        except Exception as exc:
            print(f"[LLMAdapter]: request failed: {exc}")
            return None

    def stream(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        """Yield text chunks from a streaming chat completion.

        Yields nothing on failure (never raises).
        """
        if not self._client:
            return
        try:
            response_stream = self._client.chat.completions.create(
                model=model or settings.namo_llm_model,
                messages=messages,
                temperature=(
                    temperature if temperature is not None else settings.namo_llm_temperature
                ),  # noqa: E501
                max_tokens=max_tokens or settings.namo_llm_max_tokens,
                stream=True,
            )
            for chunk in response_stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    yield delta
        except Exception as exc:
            print(f"[LLMAdapter]: stream failed: {exc}")
