from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest
import requests

from core.model_router import (
    BaseProvider,
    MockProvider,
    ModelRequest,
    ModelRouter,
    ModelRouterValidationError,
    OpenAICompatibleProvider,
    ProviderConfigurationError,
    ProviderExecutionError,
    ProviderHTTPError,
    ProviderNotFoundError,
    ProviderResponseError,
    ProviderTransportError,
)


class CapturingProvider(BaseProvider):
    def __init__(self, text: str = "answer") -> None:
        self.text = text
        self.request: ModelRequest | None = None

    def generate(self, request: ModelRequest) -> str:
        self.request = request
        return self.text


class FailingProvider(BaseProvider):
    def generate(self, request: ModelRequest) -> str:
        del request
        raise ProviderExecutionError("failed")


def _response(*, status_code: int = 200, body: Any = None) -> Mock:
    response = Mock()
    response.status_code = status_code
    response.json.return_value = body
    return response


def test_route_normalizes_provider_and_copies_messages() -> None:
    provider = CapturingProvider()
    router = ModelRouter({"OpenAI": provider})
    messages = [{"role": "user", "content": "สวัสดี"}]

    assert router.route(" OPENAI ", " model-x ", "rules", messages, max_tokens=50) == "answer"
    messages[0]["content"] = "mutated"

    assert provider.request is not None
    assert provider.request.model_name == "model-x"
    assert provider.request.messages[0].content == "สวัสดี"
    assert provider.request.options_dict() == {"max_tokens": 50}


def test_route_with_metadata_reports_explicit_fallback() -> None:
    router = ModelRouter({"primary": FailingProvider(), "mock": MockProvider("offline")})

    result = router.route_with_metadata(
        "primary", "model-x", "rules", [], fallback_provider="mock"
    )

    assert result.text == "offline"
    assert result.metadata.requested_provider == "primary"
    assert result.metadata.selected_provider == "mock"
    assert result.metadata.fallback_used is True
    assert result.metadata.latency_ms >= 0


def test_unknown_provider_fails_closed_without_mock_downgrade() -> None:
    router = ModelRouter({"mock": MockProvider()})

    with pytest.raises(ProviderNotFoundError):
        router.route("typo", "model-x", "rules", [])


def test_validation_happens_before_provider_execution() -> None:
    provider = Mock(spec=BaseProvider)
    router = ModelRouter({"primary": provider})

    with pytest.raises(ModelRouterValidationError, match="invalid role"):
        router.route(
            "primary",
            "model-x",
            "rules",
            [{"role": "system", "content": "duplicate"}],
            fallback_provider="mock",
        )

    provider.generate.assert_not_called()


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"unknown": 1}, "Unsupported"),
        ({"max_tokens": 0}, "positive"),
        ({"max_tokens": True}, "integer"),
        ({"temperature": float("nan")}, "finite"),
        ({"stop": ["ok", 1]}, "stop"),
    ],
)
def test_generation_options_are_validated(kwargs: dict[str, Any], message: str) -> None:
    router = ModelRouter({"mock": MockProvider()})

    with pytest.raises(ModelRouterValidationError, match=message):
        router.route("mock", "model-x", "rules", [], **kwargs)


def test_duplicate_registration_requires_explicit_replace() -> None:
    router = ModelRouter({"mock": MockProvider("one")})

    with pytest.raises(ModelRouterValidationError, match="already registered"):
        router.register_provider("mock", MockProvider("two"))

    router.register_provider("mock", MockProvider("two"), replace=True)
    assert router.route("mock", "model-x", "", []) == "two"


def test_openai_compatible_provider_builds_expected_request() -> None:
    session = Mock()
    session.post.return_value = _response(
        body={"choices": [{"message": {"content": "generated"}}]}
    )
    provider = OpenAICompatibleProvider(
        api_key="secret", base_url="https://llm.example/v1/", session=session
    )
    router = ModelRouter({"openai": provider})

    result = router.route(
        "openai",
        "model-x",
        "rules",
        [{"role": "user", "content": "hello"}],
        temperature=0.2,
        max_tokens=32,
    )

    assert result == "generated"
    call = session.post.call_args
    assert call.args[0] == "https://llm.example/v1/chat/completions"
    assert call.kwargs["timeout"] == (5.0, 30.0)
    assert call.kwargs["json"] == {
        "model": "model-x",
        "messages": [
            {"role": "system", "content": "rules"},
            {"role": "user", "content": "hello"},
        ],
        "max_tokens": 32,
        "temperature": 0.2,
    }
    assert call.kwargs["headers"]["Authorization"] == "Bearer secret"


def test_openai_compatible_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = OpenAICompatibleProvider(api_key=None, session=Mock())
    router = ModelRouter({"openai": provider})

    with pytest.raises(ProviderConfigurationError):
        router.route("openai", "model-x", "", [])


def test_transport_errors_are_wrapped_without_request_content() -> None:
    session = Mock()
    session.post.side_effect = requests.Timeout("secret upstream detail")
    provider = OpenAICompatibleProvider(api_key="secret", session=session)

    with pytest.raises(ProviderTransportError, match="Provider transport failed") as caught:
        provider.generate(ModelRequest("model", "private", (), ()))

    assert "private" not in str(caught.value)
    assert "secret" not in str(caught.value)


def test_http_failure_exposes_only_status_code() -> None:
    session = Mock()
    session.post.return_value = _response(status_code=429)
    provider = OpenAICompatibleProvider(api_key="secret", session=session)

    with pytest.raises(ProviderHTTPError) as caught:
        provider.generate(ModelRequest("model", "", (), ()))

    assert caught.value.status_code == 429
    assert str(caught.value) == "Provider returned HTTP status 429."


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"choices": []},
        {"choices": [{"message": {}}]},
        {"choices": [{"message": {"content": None}}]},
    ],
)
def test_malformed_provider_response_is_rejected(body: Any) -> None:
    session = Mock()
    session.post.return_value = _response(body=body)
    provider = OpenAICompatibleProvider(api_key="secret", session=session)

    with pytest.raises(ProviderResponseError):
        provider.generate(ModelRequest("model", "", (), ()))


def test_fallback_must_be_distinct_and_registered() -> None:
    router = ModelRouter({"primary": FailingProvider()})

    with pytest.raises(ModelRouterValidationError, match="must differ"):
        router.route("primary", "model", "", [], fallback_provider="primary")
    with pytest.raises(ProviderNotFoundError):
        router.route("primary", "model", "", [], fallback_provider="missing")
