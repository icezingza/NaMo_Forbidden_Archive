import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

TokenCounter = Callable[[str], int]


@dataclass(frozen=True, slots=True)
class AllocatorConfig:
    context_window: int = 8192
    response_reserve: int = 1500
    system_ratio: float = 0.25
    memory_ratio: float = 0.25
    history_ratio: float = 0.50
    message_overhead_tokens: int = 4

    def __post_init__(self) -> None:
        if isinstance(self.context_window, bool) or not isinstance(self.context_window, int):
            raise TypeError("context_window must be an integer")
        if isinstance(self.response_reserve, bool) or not isinstance(self.response_reserve, int):
            raise TypeError("response_reserve must be an integer")
        if self.context_window <= 0:
            raise ValueError("context_window must be positive")
        if self.response_reserve < 0 or self.response_reserve >= self.context_window:
            raise ValueError("response_reserve must be non-negative and below context_window")
        if (
            isinstance(self.message_overhead_tokens, bool)
            or not isinstance(self.message_overhead_tokens, int)
        ):
            raise TypeError("message_overhead_tokens must be an integer")
        if self.message_overhead_tokens < 0:
            raise ValueError("message_overhead_tokens must be non-negative")

        ratios = (self.system_ratio, self.memory_ratio, self.history_ratio)
        if any(isinstance(ratio, bool) or not isinstance(ratio, (int, float)) for ratio in ratios):
            raise TypeError("allocation ratios must be numeric")
        if any(not math.isfinite(ratio) or not 0.0 <= ratio <= 1.0 for ratio in ratios):
            raise ValueError("allocation ratios must be finite values between 0.0 and 1.0")
        if not math.isclose(sum(ratios), 1.0, rel_tol=0.0, abs_tol=1e-9):
            raise ValueError(f"allocation ratios must sum to 1.0, got {sum(ratios)}")


@dataclass(frozen=True, slots=True)
class ContextMessage:
    role: str
    content: str

    def __post_init__(self) -> None:
        if not isinstance(self.role, str) or not self.role.strip():
            raise ValueError("message role must be a non-empty string")
        if not isinstance(self.content, str):
            raise TypeError("message content must be a string")

    def as_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


class ContextAllocator:
    """Allocate prompt context without mutating caller-owned messages."""

    __slots__ = ("_config", "_estimation_method", "_token_counter")

    def __init__(
        self,
        config: AllocatorConfig | None = None,
        *,
        token_counter: TokenCounter | None = None,
        estimation_method: str | None = None,
    ) -> None:
        self._config = config or AllocatorConfig()
        self._token_counter = token_counter or self._estimate_conservative_unicode
        if estimation_method is not None and not estimation_method.strip():
            raise ValueError("estimation_method must be a non-empty string")
        self._estimation_method = estimation_method or (
            "model_tokenizer" if token_counter is not None else "conservative_unicode"
        )

    @property
    def config(self) -> AllocatorConfig:
        return self._config

    @staticmethod
    def _estimate_conservative_unicode(text: str) -> int:
        """Conservatively estimate ASCII at 4 chars/token and non-ASCII at 1 char/token."""
        if not text:
            return 0
        ascii_characters = sum(character.isascii() for character in text)
        non_ascii_characters = len(text) - ascii_characters
        return math.ceil(ascii_characters / 4) + non_ascii_characters

    def _count_tokens(self, text: str) -> int:
        count = self._token_counter(text)
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError("token_counter must return a non-negative integer")
        return count

    def _truncate_to_tokens(self, text: str, budget: int, *, keep_tail: bool = False) -> str:
        if budget <= 0 or not text:
            return ""
        if self._count_tokens(text) <= budget:
            return text

        low = 0
        high = len(text)
        while low < high:
            length = (low + high + 1) // 2
            candidate = text[-length:] if keep_tail else text[:length]
            if self._count_tokens(candidate) <= budget:
                low = length
            else:
                high = length - 1
        return text[-low:] if keep_tail and low else text[:low]

    @staticmethod
    def _normalize_messages(
        messages: Sequence[ContextMessage | Mapping[str, str]] | None,
    ) -> tuple[ContextMessage, ...]:
        normalized: list[ContextMessage] = []
        for message in messages or ():
            if isinstance(message, ContextMessage):
                normalized.append(message)
                continue
            if not isinstance(message, Mapping):
                raise TypeError("each message must be a ContextMessage or mapping")
            if "role" not in message or "content" not in message:
                raise ValueError("each message mapping requires role and content")
            normalized.append(ContextMessage(role=message["role"], content=message["content"]))
        return tuple(normalized)

    def allocate(
        self,
        system_text: str,
        memory_text: str | None,
        history_messages: Sequence[ContextMessage | Mapping[str, str]] | None,
        *,
        critical_system_text: str | None = None,
    ) -> dict[str, Any]:
        if not isinstance(system_text, str):
            raise TypeError("system_text must be a string")
        if memory_text is not None and not isinstance(memory_text, str):
            raise TypeError("memory_text must be a string or None")
        if critical_system_text is not None and not isinstance(critical_system_text, str):
            raise TypeError("critical_system_text must be a string or None")

        memory_text = memory_text or ""
        critical_system_text = critical_system_text or ""
        messages = self._normalize_messages(history_messages)
        prompt_budget = self.config.context_window - self.config.response_reserve

        fixed_overhead = self.config.message_overhead_tokens * sum(
            (bool(critical_system_text or system_text), bool(memory_text))
        )
        content_budget = max(0, prompt_budget - fixed_overhead)
        nominal_system_budget = int(content_budget * self.config.system_ratio)
        nominal_memory_budget = int(content_budget * self.config.memory_ratio)

        final_critical_system = self._truncate_to_tokens(
            critical_system_text,
            content_budget,
        )
        critical_system_tokens = self._count_tokens(final_critical_system)
        separator = "\n\n" if final_critical_system and system_text else ""
        critical_with_separator_tokens = self._count_tokens(final_critical_system + separator)
        dynamic_system_budget = max(0, nominal_system_budget - critical_with_separator_tokens)
        final_dynamic_system = self._truncate_to_tokens(system_text, dynamic_system_budget)
        final_system = final_critical_system
        if final_dynamic_system:
            final_system += ("\n\n" if final_system else "") + final_dynamic_system
        system_tokens = self._count_tokens(final_system)
        remaining_content_budget = max(0, content_budget - system_tokens)

        memory_budget = min(nominal_memory_budget, remaining_content_budget)
        final_memory = self._truncate_to_tokens(memory_text, memory_budget)
        memory_tokens = self._count_tokens(final_memory)
        history_budget = max(0, remaining_content_budget - memory_tokens)

        allocated_reversed: list[ContextMessage] = []
        history_tokens = 0
        history_truncated = 0
        for message in reversed(messages):
            message_tokens = self._count_tokens(message.content)
            required = message_tokens + self.config.message_overhead_tokens
            if history_tokens + required <= history_budget:
                allocated_reversed.append(message)
                history_tokens += required
                continue

            if not allocated_reversed:
                remaining = max(
                    0,
                    history_budget - history_tokens - self.config.message_overhead_tokens,
                )
                content = self._truncate_to_tokens(message.content, remaining, keep_tail=True)
                if content or not message.content:
                    allocated_reversed.append(ContextMessage(message.role, content))
                    history_tokens += self._count_tokens(content)
                    history_tokens += self.config.message_overhead_tokens
                    history_truncated = int(content != message.content)
            break

        allocated_messages = tuple(reversed(allocated_reversed))
        represented_messages = len(allocated_messages)
        dropped_messages = len(messages) - represented_messages

        system_overhead = self.config.message_overhead_tokens if final_system else 0
        memory_overhead = self.config.message_overhead_tokens if final_memory else 0
        total_prompt_tokens = (
            system_tokens
            + memory_tokens
            + history_tokens
            + system_overhead
            + memory_overhead
        )

        return {
            "system": final_system,
            "memory": final_memory,
            "history": [message.as_dict() for message in allocated_messages],
            "allocated_budget": self.config.context_window,
            "usage": {
                "system_tokens": system_tokens,
                "critical_system_tokens": critical_system_tokens,
                "dynamic_system_tokens": max(0, system_tokens - critical_system_tokens),
                "memory_tokens": memory_tokens,
                "history_tokens_with_overhead": history_tokens,
                "protocol_overhead_tokens": system_overhead + memory_overhead,
                "response_reserved": self.config.response_reserve,
                "total_prompt_tokens": total_prompt_tokens,
                "prompt_budget": prompt_budget,
                "context_window_limit": self.config.context_window,
                "estimation_method": self._estimation_method,
            },
            "truncated": {
                "system": final_system
                != "\n\n".join(
                    section for section in (critical_system_text, system_text) if section
                ),
                "critical_system": final_critical_system != critical_system_text,
                "dynamic_system": final_dynamic_system != system_text,
                "memory": final_memory != memory_text,
                "history_messages_truncated": history_truncated,
                "history_messages_dropped": max(0, dropped_messages),
            },
        }
