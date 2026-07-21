"""Validated, observable routing for synchronous text-generation providers."""

from __future__ import annotations

import logging
import math
import os
import re
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import requests

logger = logging.getLogger("NamoModelRouter")

_PROVIDER_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_MESSAGE_ROLES = frozenset({"user", "assistant", "tool"})
_GENERATION_OPTIONS = frozenset(
    {
        "temperature",
        "max_tokens",
        "top_p",
        "stop",
        "seed",
        "presence_penalty",
        "frequency_penalty",
    }
)


class ModelRouterError(RuntimeError):
    """Base error for model routing."""


class ModelRouterValidationError(ModelRouterError, ValueError):
    """The caller supplied an invalid routing request."""


class ProviderNotFoundError(ModelRouterError, LookupError):
    """The requested provider is not registered."""


class ProviderExecutionError(ModelRouterError):
    """A registered provider could not complete generation."""


class ProviderConfigurationError(ProviderExecutionError):
    """A provider is missing required runtime configuration."""


class ProviderTransportError(ProviderExecutionError):
    """A provider network request failed."""


class ProviderHTTPError(ProviderExecutionError):
    """A provider returned a non-success HTTP status."""

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"Provider returned HTTP status {status_code}.")


class ProviderResponseError(ProviderExecutionError):
    """A provider returned a malformed response body."""


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True, slots=True)
class ModelRequest:
    model_name: str
    system_prompt: str
    messages: tuple[ChatMessage, ...]
    options: tuple[tuple[str, Any], ...]

    def options_dict(self) -> dict[str, Any]:
        return dict(self.options)


@dataclass(frozen=True, slots=True)
class RouteMetadata:
    requested_provider: str
    selected_provider: str
    model_name: str
    latency_ms: float
    fallback_used: bool


@dataclass(frozen=True, slots=True)
class ModelResponse:
    text: str
    metadata: RouteMetadata


class BaseProvider(ABC):
    """Contract implemented by synchronous text-generation providers."""

    @abstractmethod
    def generate(self, request: ModelRequest) -> str:
        """Generate one complete text response."""


class OpenAICompatibleProvider(BaseProvider):
    """Synchronous Chat Completions transport for compatible HTTP servers."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        session: requests.Session | None = None,
        timeout: tuple[float, float] = (5.0, 30.0),
    ) -> None:
        resolved_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip(
            "/"
        )
        if not resolved_url.startswith(("http://", "https://")):
            raise ModelRouterValidationError("base_url must use http or https.")
        if (
            not isinstance(timeout, tuple)
            or len(timeout) != 2
            or any(
                isinstance(value, bool) or not isinstance(value, (int, float))
                for value in timeout
            )
            or any(not math.isfinite(value) or value <= 0 for value in timeout)
        ):
            raise ModelRouterValidationError("timeout must contain positive connect/read seconds.")

        self._api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self._base_url = resolved_url
        self._session = session or requests.Session()
        self._timeout = timeout

    def generate(self, request: ModelRequest) -> str:
        if not self._api_key:
            raise ProviderConfigurationError("OpenAI-compatible provider API key is missing.")

        payload_messages = [{"role": "system", "content": request.system_prompt}]
        payload_messages.extend(
            {"role": message.role, "content": message.content} for message in request.messages
        )
        payload: dict[str, Any] = {
            "model": request.model_name,
            "messages": payload_messages,
            **request.options_dict(),
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = self._session.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            raise ProviderTransportError("Provider transport failed.") from exc

        if not 200 <= response.status_code < 300:
            raise ProviderHTTPError(response.status_code)

        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
        except (ValueError, TypeError, KeyError, IndexError) as exc:
            raise ProviderResponseError("Provider response schema is invalid.") from exc
        if not isinstance(content, str):
            raise ProviderResponseError("Provider response content must be a string.")
        return content


class MockProvider(BaseProvider):
    """Explicit deterministic provider for tests and offline development."""

    def __init__(self, response_text: str = "[MOCK_VOID_RESONANCE]") -> None:
        if not isinstance(response_text, str):
            raise ModelRouterValidationError("Mock response_text must be a string.")
        self._response_text = response_text

    def generate(self, request: ModelRequest) -> str:
        del request
        return self._response_text


class ModelRouter:
    """Thread-safe provider registry with explicit, observable fallback routing."""

    def __init__(self, providers: Mapping[str, BaseProvider] | None = None) -> None:
        self._lock = threading.RLock()
        self._providers: dict[str, BaseProvider] = {}
        if providers:
            for name, provider in providers.items():
                self.register_provider(name, provider)

    def register_provider(
        self, name: str, provider: BaseProvider, *, replace: bool = False
    ) -> None:
        normalized = _normalize_provider_name(name)
        if not isinstance(provider, BaseProvider):
            raise ModelRouterValidationError("provider must implement BaseProvider.")
        with self._lock:
            if normalized in self._providers and not replace:
                raise ModelRouterValidationError(f"Provider '{normalized}' is already registered.")
            self._providers[normalized] = provider
        logger.info("Registered model provider '%s'.", normalized)

    def route(
        self,
        provider_name: str,
        model_name: str,
        system_prompt: str,
        messages: Sequence[Mapping[str, str] | ChatMessage],
        *,
        fallback_provider: str | None = None,
        **options: Any,
    ) -> str:
        return self.route_with_metadata(
            provider_name,
            model_name,
            system_prompt,
            messages,
            fallback_provider=fallback_provider,
            **options,
        ).text

    def route_with_metadata(
        self,
        provider_name: str,
        model_name: str,
        system_prompt: str,
        messages: Sequence[Mapping[str, str] | ChatMessage],
        *,
        fallback_provider: str | None = None,
        **options: Any,
    ) -> ModelResponse:
        requested = _normalize_provider_name(provider_name)
        request = _build_request(model_name, system_prompt, messages, options)
        provider = self._get_provider(requested)

        selected = requested
        fallback_used = False
        started = time.perf_counter()
        try:
            text = provider.generate(request)
        except ProviderExecutionError as exc:
            if fallback_provider is None:
                raise
            selected = _normalize_provider_name(fallback_provider)
            fallback = self._get_provider(selected)
            if selected == requested:
                raise ModelRouterValidationError(
                    "Fallback provider must differ from primary provider."
                ) from exc
            fallback_used = True
            logger.warning(
                "Provider '%s' failed with %s; routing to explicit fallback '%s'.",
                requested,
                type(exc).__name__,
                selected,
            )
            text = fallback.generate(request)

        if not isinstance(text, str):
            raise ProviderResponseError("Provider output must be a string.")
        latency_ms = (time.perf_counter() - started) * 1000
        return ModelResponse(
            text=text,
            metadata=RouteMetadata(
                requested_provider=requested,
                selected_provider=selected,
                model_name=request.model_name,
                latency_ms=latency_ms,
                fallback_used=fallback_used,
            ),
        )

    def _get_provider(self, name: str) -> BaseProvider:
        with self._lock:
            provider = self._providers.get(name)
        if provider is None:
            raise ProviderNotFoundError(f"Provider '{name}' is not registered.")
        return provider


def _normalize_provider_name(name: str) -> str:
    if not isinstance(name, str):
        raise ModelRouterValidationError("Provider name must be a string.")
    normalized = name.strip().lower()
    if not _PROVIDER_NAME.fullmatch(normalized):
        raise ModelRouterValidationError("Provider name is empty or invalid.")
    return normalized


def _build_request(
    model_name: str,
    system_prompt: str,
    messages: Sequence[Mapping[str, str] | ChatMessage],
    options: Mapping[str, Any],
) -> ModelRequest:
    if not isinstance(model_name, str) or not model_name.strip():
        raise ModelRouterValidationError("model_name must be a non-empty string.")
    if not isinstance(system_prompt, str):
        raise ModelRouterValidationError("system_prompt must be a string.")
    if isinstance(messages, (str, bytes)) or not isinstance(messages, Sequence):
        raise ModelRouterValidationError("messages must be a sequence.")

    normalized_messages: list[ChatMessage] = []
    for index, message in enumerate(messages):
        if isinstance(message, ChatMessage):
            role, content = message.role, message.content
        elif isinstance(message, Mapping):
            role, content = message.get("role"), message.get("content")
        else:
            raise ModelRouterValidationError(f"Message {index} must be a mapping or ChatMessage.")
        if role not in _MESSAGE_ROLES:
            raise ModelRouterValidationError(f"Message {index} has an invalid role.")
        if not isinstance(content, str):
            raise ModelRouterValidationError(f"Message {index} content must be a string.")
        normalized_messages.append(ChatMessage(role=role, content=content))

    unknown = set(options) - _GENERATION_OPTIONS
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ModelRouterValidationError(f"Unsupported generation options: {names}.")
    _validate_options(options)
    return ModelRequest(
        model_name=model_name.strip(),
        system_prompt=system_prompt,
        messages=tuple(normalized_messages),
        options=tuple((key, options[key]) for key in sorted(options)),
    )


def _validate_options(options: Mapping[str, Any]) -> None:
    for name in ("temperature", "top_p", "presence_penalty", "frequency_penalty"):
        value = options.get(name)
        if value is not None and (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ModelRouterValidationError(f"{name} must be a finite number.")
    for name in ("max_tokens", "seed"):
        value = options.get(name)
        if value is not None and (isinstance(value, bool) or not isinstance(value, int)):
            raise ModelRouterValidationError(f"{name} must be an integer.")
    if "max_tokens" in options and options["max_tokens"] <= 0:
        raise ModelRouterValidationError("max_tokens must be positive.")
    stop = options.get("stop")
    if stop is not None and not (
        isinstance(stop, str)
        or (
            isinstance(stop, Sequence)
            and not isinstance(stop, (str, bytes))
            and all(isinstance(item, str) for item in stop)
        )
    ):
        raise ModelRouterValidationError("stop must be a string or a sequence of strings.")
