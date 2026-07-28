from dataclasses import FrozenInstanceError

import pytest

from core.context_allocator import AllocatorConfig, ContextAllocator, ContextMessage


def character_counter(text: str) -> int:
    return len(text)


def test_config_and_messages_are_frozen() -> None:
    config = AllocatorConfig()
    message = ContextMessage("user", "hello")

    with pytest.raises(FrozenInstanceError):
        config.context_window = 10  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        message.content = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    "config",
    [
        AllocatorConfig(system_ratio=0.0, memory_ratio=0.0, history_ratio=1.0),
        AllocatorConfig(system_ratio=1.0, memory_ratio=0.0, history_ratio=0.0),
    ],
)
def test_boundary_ratios_are_valid(config: AllocatorConfig) -> None:
    assert ContextAllocator(config).config == config


@pytest.mark.parametrize(
    "kwargs",
    [
        {"context_window": 0},
        {"context_window": 10, "response_reserve": 10},
        {"system_ratio": -1.0, "memory_ratio": 1.0, "history_ratio": 1.0},
        {"system_ratio": 0.2, "memory_ratio": 0.2, "history_ratio": 0.2},
    ],
)
def test_invalid_config_is_rejected(kwargs: dict[str, int | float]) -> None:
    with pytest.raises((TypeError, ValueError)):
        AllocatorConfig(**kwargs)  # type: ignore[arg-type]


def test_none_memory_and_history_are_supported() -> None:
    allocator = ContextAllocator(
        AllocatorConfig(context_window=20, response_reserve=4),
        token_counter=character_counter,
        estimation_method="test_characters",
    )

    result = allocator.allocate("", None, None)

    assert result["memory"] == ""
    assert result["history"] == []
    assert result["usage"]["estimation_method"] == "test_characters"


def test_default_estimator_is_conservative_for_thai() -> None:
    allocator = ContextAllocator()

    assert allocator._count_tokens("ภาษาไทย") == len("ภาษาไทย")
    assert allocator._count_tokens("abcd") == 1


def test_allocate_does_not_share_mutable_message_references() -> None:
    source = {"role": "user", "content": "mutable"}
    allocator = ContextAllocator(
        AllocatorConfig(context_window=100, response_reserve=10),
        token_counter=character_counter,
    )

    result = allocator.allocate("", "", [source])
    result["history"][0]["content"] = "changed"

    assert source["content"] == "mutable"


def test_unused_system_and_memory_budget_is_redistributed_to_history() -> None:
    allocator = ContextAllocator(
        AllocatorConfig(
            context_window=40,
            response_reserve=0,
            system_ratio=0.25,
            memory_ratio=0.25,
            history_ratio=0.5,
            message_overhead_tokens=0,
        ),
        token_counter=character_counter,
    )

    result = allocator.allocate("", "", [{"role": "user", "content": "x" * 35}])

    assert result["history"][0]["content"] == "x" * 35
    assert result["usage"]["total_prompt_tokens"] <= result["usage"]["prompt_budget"]


def test_oversized_latest_message_keeps_tail_and_reports_all_older_drops() -> None:
    allocator = ContextAllocator(
        AllocatorConfig(
            context_window=20,
            response_reserve=0,
            system_ratio=0.0,
            memory_ratio=0.0,
            history_ratio=1.0,
            message_overhead_tokens=2,
        ),
        token_counter=character_counter,
    )
    messages = [
        {"role": "user", "content": "old-one"},
        {"role": "assistant", "content": "old-two"},
        {"role": "user", "content": "prefix-keep-this-tail"},
    ]

    result = allocator.allocate("", "", messages)

    assert result["history"] == [{"role": "user", "content": "fix-keep-this-tail"}]
    assert result["truncated"]["history_messages_truncated"] == 1
    assert result["truncated"]["history_messages_dropped"] == 2
    assert result["usage"]["total_prompt_tokens"] <= result["usage"]["prompt_budget"]


def test_invalid_token_counter_is_rejected() -> None:
    allocator = ContextAllocator(token_counter=lambda _text: -1)

    with pytest.raises(ValueError, match="non-negative integer"):
        allocator.allocate("system", "", [])


def test_critical_system_borrows_budget_before_dynamic_memory_and_history() -> None:
    allocator = ContextAllocator(
        AllocatorConfig(
            context_window=20,
            response_reserve=0,
            system_ratio=0.25,
            memory_ratio=0.25,
            history_ratio=0.5,
            message_overhead_tokens=0,
        ),
        token_counter=character_counter,
    )

    result = allocator.allocate(
        "dynamic-context",
        "memory-data",
        [{"role": "user", "content": "latest-user"}],
        critical_system_text="criticalrule",
    )

    assert result["system"] == "criticalrule"
    assert result["truncated"]["critical_system"] is False
    assert result["truncated"]["dynamic_system"] is True
    assert result["usage"]["critical_system_tokens"] == len("criticalrule")
    assert result["usage"]["total_prompt_tokens"] <= result["usage"]["prompt_budget"]


def test_oversized_critical_system_is_reported() -> None:
    allocator = ContextAllocator(
        AllocatorConfig(
            context_window=10,
            response_reserve=0,
            system_ratio=0.25,
            memory_ratio=0.25,
            history_ratio=0.5,
            message_overhead_tokens=0,
        ),
        token_counter=character_counter,
    )

    result = allocator.allocate("", None, None, critical_system_text="x" * 20)

    assert result["system"] == "x" * 10
    assert result["truncated"]["critical_system"] is True
    assert result["usage"]["total_prompt_tokens"] == 10
