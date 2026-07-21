from collections.abc import Callable
from urllib.parse import urlparse

TokenCounter = Callable[[str], int]


def _is_official_openai_endpoint(base_url: str | None) -> bool:
    if not base_url:
        return True
    hostname = urlparse(base_url).hostname
    return hostname == "api.openai.com"


def build_model_token_counter(
    model: str,
    base_url: str | None,
) -> tuple[TokenCounter | None, str]:
    """Return a local plain-text counter only for a recognized official OpenAI model."""
    if not _is_official_openai_endpoint(base_url):
        return None, "conservative_unicode:custom_provider"

    try:
        import tiktoken
    except ImportError:
        return None, "conservative_unicode:tiktoken_unavailable"

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        return None, "conservative_unicode:unknown_model"

    def count_tokens(text: str) -> int:
        return len(encoding.encode(text, disallowed_special=()))

    return count_tokens, f"tiktoken:{encoding.name}"

