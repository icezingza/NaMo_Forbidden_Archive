from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from core.model_router import BaseProvider, ModelRequest, ModelRouter
from core.state_ledger import StateLedger


class CapturingProvider(BaseProvider):
    def __init__(self, response: str = "unified response") -> None:
        self.response = response
        self.request: ModelRequest | None = None

    def generate(self, request: ModelRequest) -> str:
        self.request = request
        return self.response


def _build_engine(tmp_path, provider: BaseProvider):
    ledger = StateLedger(tmp_path / "namo_state.json")
    router = ModelRouter({"primary": provider})
    with (
        patch("core.namo_omega_engine.TTSAdapter") as tts_cls,
        patch("core.namo_omega_engine.NaMoOmegaEngine._resolve_llm_enabled", return_value=False),
    ):
        tts_cls.return_value = MagicMock(
            _client=None,
            synthesize=AsyncMock(return_value=None),
        )
        from core.namo_omega_engine import NaMoOmegaEngine

        engine = NaMoOmegaEngine(state_ledger=ledger, model_router=router)
    engine.rag_memory = None
    return engine, ledger


async def test_unified_pipeline_allocates_routes_and_commits(tmp_path) -> None:
    provider = CapturingProvider()
    engine, ledger = _build_engine(tmp_path, provider)

    result = await engine.process_input("รักนะ คิดถึงมาก", session_id="unified-session")

    assert result["text"] == "unified response"
    assert provider.request is not None
    assert "[Resonance Ledger]" in provider.request.system_prompt
    assert provider.request.messages[-1].role == "user"
    assert provider.request.messages[-1].content == "รักนะ คิดถึงมาก"

    status = result["system_status"]
    assert status["context_allocation"]["usage"]["total_prompt_tokens"] > 0
    assert status["model_route"]["selected_provider"] == "primary"
    assert status["model_route"]["fallback_used"] is False
    assert status["state_ledger"]["committed"] is True
    assert status["state_ledger"]["turn_count"] == 1

    persisted = ledger.load_state("unified-session")
    assert persisted.turn_count == 1
    assert persisted.fused_score > 0
    assert len(ledger.get_history("unified-session")) == 1


async def test_unified_pipeline_preserves_session_isolation(tmp_path) -> None:
    engine, ledger = _build_engine(tmp_path, CapturingProvider())

    await engine.process_input("รักนะ", session_id="session-a")
    await engine.process_input("สวัสดี", session_id="session-b")

    assert ledger.load_state("session-a").turn_count == 1
    assert ledger.load_state("session-b").turn_count == 1
    assert len(ledger.get_history("session-a")) == 1
    assert len(ledger.get_history("session-b")) == 1


def test_resonance_signal_is_bounded_and_signal_driven(tmp_path) -> None:
    engine, _ = _build_engine(tmp_path, CapturingProvider())

    high, confidence = engine._calculate_resonance_signal(
        {"emotion": {"trust": 1.0, "desire": 1.0, "arousal": 1.0}}
    )
    low, _ = engine._calculate_resonance_signal(
        {"emotion": {"trust": 0.0, "desire": 0.0, "arousal": 0.0}}
    )
    neutral, neutral_confidence = engine._calculate_resonance_signal(None)
    non_finite, _ = engine._calculate_resonance_signal(
        {"emotion": {"trust": float("nan"), "desire": float("inf"), "arousal": None}}
    )

    assert high == 1.0
    assert low == 0.0
    assert high > neutral > low
    assert confidence == 0.75
    assert neutral_confidence == 0.25
    assert non_finite == neutral
