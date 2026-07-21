import sys
from types import SimpleNamespace

from core.token_counter import build_model_token_counter


def test_custom_provider_uses_conservative_fallback_without_importing_tiktoken() -> None:
    counter, method = build_model_token_counter("custom-model", "https://llm.example/v1")

    assert counter is None
    assert method == "conservative_unicode:custom_provider"


def test_missing_tiktoken_uses_conservative_fallback(monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "tiktoken", None)

    counter, method = build_model_token_counter("gpt-4o-mini", None)

    assert counter is None
    assert method == "conservative_unicode:tiktoken_unavailable"


def test_known_official_model_uses_resolved_tiktoken_encoding(monkeypatch) -> None:
    class FakeEncoding:
        name = "fake_encoding"

        @staticmethod
        def encode(text: str, *, disallowed_special: tuple) -> list[str]:
            assert disallowed_special == ()
            return list(text)

    fake_tiktoken = SimpleNamespace(encoding_for_model=lambda _model: FakeEncoding())
    monkeypatch.setitem(sys.modules, "tiktoken", fake_tiktoken)

    counter, method = build_model_token_counter("gpt-test", "https://api.openai.com/v1")

    assert counter is not None
    assert counter("ภาษาไทย") == len("ภาษาไทย")
    assert method == "tiktoken:fake_encoding"


def test_unknown_official_model_uses_conservative_fallback(monkeypatch) -> None:
    def unknown_model(_model: str):
        raise KeyError("unknown")

    monkeypatch.setitem(sys.modules, "tiktoken", SimpleNamespace(encoding_for_model=unknown_model))

    counter, method = build_model_token_counter("unknown", None)

    assert counter is None
    assert method == "conservative_unicode:unknown_model"
