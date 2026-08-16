"""
NaMo Forbidden Archive — LLM Cost & Token Optimization Module
Integrates Prompt Caching, Thinking Budgeting, Cache Miss Prevention, and Token Usage Audit
directly into the NaMo Model Router pipeline.
"""

import logging
from typing import Any

logger = logging.getLogger("NamoLLMOptimizer")


class NaMoLLMOptimizer:
    """
    LLM Optimizer for NaMo Advanced Conversational Core (ACC).
    Provides prompt caching, reasoning budget selection, and cache miss prevention checks.
    """

    DYNAMIC_PATTERNS = [
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",  # UUID
        r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\b",  # ISO Timestamp
    ]

    def __init__(self, provider: str = "Anthropic"):
        self.provider = provider.title()

    def build_optimized_payload(
        self,
        system_prompt: str,
        user_message: str,
        task_type: str = "qa",
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Structures System Prompt + Tools as an ephemeral cache prefix
        and calculates the optimal Thinking Budget.
        """
        # Step 1: Check Prefix Stability (Cache Miss Prevention)
        is_stable, warnings = self.validate_prefix_stability(system_prompt)
        if not is_stable:
            logger.warning(f"⚠️ [Cache Miss Warning]: {', '.join(warnings)}")

        # Step 2: Get Thinking Budget
        budget_config = self.get_thinking_budget(task_type)

        # Step 3: Format Cache Prefix according to Provider
        if self.provider == "Anthropic":
            formatted_payload = {
                "model": budget_config["model"],
                "max_tokens": budget_config["max_tokens"],
                "thinking": {"type": "enabled", "budget_tokens": budget_config["budget_tokens"]},
                "system": [
                    {"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}
                ],
                "tools": tools or [],
                "messages": [{"role": "user", "content": user_message}],
            }
        else:
            # OpenAI / Generic format
            formatted_payload = {
                "model": "gpt-4o",
                "max_tokens": budget_config["max_tokens"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "prompt_cache_key": f"namo_cache_{hash(system_prompt) & 0xffffffff}",
            }

        return formatted_payload

    def validate_prefix_stability(self, system_prompt: str) -> tuple[bool, list[str]]:
        import re

        warnings = []
        is_stable = True

        for pattern in self.DYNAMIC_PATTERNS:
            matches = re.findall(pattern, system_prompt)
            if matches:
                is_stable = False
                warnings.append(
                    f"Dynamic value detected: '{matches[0]}'. Move out of system prompt."
                )

        return is_stable, warnings

    def get_thinking_budget(self, task_type: str) -> dict[str, Any]:
        presets = {
            "qa": {
                "model": "claude-3-7-sonnet-20250219",
                "max_tokens": 2048,
                "budget_tokens": 1024,
            },
            "dialogue": {
                "model": "claude-3-7-sonnet-20250219",
                "max_tokens": 4096,
                "budget_tokens": 2048,
            },
            "emotion_fusion": {
                "model": "claude-3-7-sonnet-20250219",
                "max_tokens": 4096,
                "budget_tokens": 2048,
            },
            "deep_reasoning": {
                "model": "claude-3-7-sonnet-20250219",
                "max_tokens": 8192,
                "budget_tokens": 4096,
            },
        }
        return presets.get(task_type.lower(), presets["qa"])

    def audit_cache_response(self, usage: dict[str, int]) -> dict[str, Any]:
        cache_read = usage.get("cache_read_input_tokens", 0) or usage.get("cached_tokens", 0)
        cache_created = usage.get("cache_creation_input_tokens", 0)

        hit = cache_read > 0
        return {
            "cache_hit": hit,
            "status": "CACHE HIT (SAVINGS ACTIVE)" if hit else "CACHE MISS",
            "cache_read_input_tokens": cache_read,
            "cache_creation_input_tokens": cache_created,
            "savings_estimate": "90-95%" if hit else "0%",
        }
