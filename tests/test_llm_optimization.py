"""
Unit Tests for NaMo LLM Optimization Engine
"""

from core.llm_optimization import NaMoLLMOptimizer

def test_namo_llm_optimizer_anthropic():
    optimizer = NaMoLLMOptimizer(provider="Anthropic")
    payload = optimizer.build_optimized_payload(
        system_prompt="You are NaMo ACC system core.",
        user_message="Hello NaMo",
        task_type="dialogue"
    )
    
    assert payload["system"][0]["cache_control"]["type"] == "ephemeral"
    assert payload["thinking"]["budget_tokens"] == 2048
    assert payload["messages"][0]["content"] == "Hello NaMo"

def test_prefix_stability_validator():
    optimizer = NaMoLLMOptimizer()
    
    # Stable test
    stable, warnings = optimizer.validate_prefix_stability("Clean static system prompt")
    assert stable is True
    assert len(warnings) == 0

    # Unstable test
    unstable, warnings = optimizer.validate_prefix_stability("System prompt with ISO 2026-07-30T15:00:00Z timestamp")
    assert unstable is False
    assert len(warnings) == 1

def test_cache_audit():
    optimizer = NaMoLLMOptimizer()
    audit = optimizer.audit_cache_response({"cache_read_input_tokens": 12500})
    assert audit["cache_hit"] is True
    assert audit["savings_estimate"] == "90-95%"

if __name__ == "__main__":
    test_namo_llm_optimizer_anthropic()
    test_prefix_stability_validator()
    test_cache_audit()
    print("✅ All NaMo LLM Optimizer Unit Tests Passed!")
