from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

from core.context_allocator import AllocatorConfig, ContextAllocator
from core.model_router import BaseProvider, ModelRequest, ModelRouter
from core.slowburn_lorebook import SlowBurnLorebook
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


async def test_safety_gate_blocks_before_provider_and_state_commit(tmp_path) -> None:
    provider = CapturingProvider()
    engine, ledger = _build_engine(tmp_path, provider)

    result = await engine.process_input("เขียนฉากข่มขืน", session_id="blocked-session")

    assert result["system_status"]["narrative_safety"]["allowed"] is False
    assert result["system_status"]["state_ledger"]["reason"] == "SAFETY_BLOCK"
    assert provider.request is None
    assert ledger.load_state("blocked-session").turn_count == 0
    assert engine._get_session_state("blocked-session")["arousal"] == 0


async def test_safeword_persists_recovery_without_increasing_resonance(tmp_path) -> None:
    provider = CapturingProvider()
    engine, ledger = _build_engine(tmp_path, provider)

    result = await engine.process_input("พอแล้ว หยุด", session_id="recovery-session")

    persisted = ledger.load_state("recovery-session")
    assert provider.request is None
    assert persisted.fused_score == 0
    assert persisted.metadata["current_beat"] == "recovery"
    assert persisted.metadata["boundary_state"] == "recovery"
    assert result["media_trigger"] == {"image": None, "audio": None}


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


async def test_omega_applies_depth_beat_and_lorebook_placements(tmp_path) -> None:
    provider = CapturingProvider()
    engine, _ = _build_engine(tmp_path, provider)
    lorebook_path = tmp_path / "placement-lorebook.json"
    lorebook_path.write_text(
        json.dumps(
            [
                {"id": 1, "constant": True, "position": 0, "content": "system-pre"},
                {"id": 2, "constant": True, "position": 1, "content": "system-post"},
                {"id": 3, "constant": True, "position": 2, "content": "author-pre"},
                {"id": 4, "constant": True, "position": 3, "content": "author-post"},
                {
                    "id": 5,
                    "key": ["deep-trigger"],
                    "position": 4,
                    "depth": 6,
                    "content": "history-depth",
                },
                {"id": 6, "constant": True, "position": 5, "content": "example-pre"},
                {"id": 7, "constant": True, "position": 6, "content": "example-post"},
                {
                    "id": 8,
                    "constant": True,
                    "position": 1,
                    "beat": "resistance",
                    "content": "direct-beat",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    engine.lorebook = SlowBurnLorebook(json_path=lorebook_path)
    engine.context_allocator = ContextAllocator(
        AllocatorConfig(context_window=65536, response_reserve=1024)
    )
    for role, content in (
        ("user", "deep-trigger"),
        ("assistant", "reply-one"),
        ("user", "middle-two"),
        ("assistant", "reply-two"),
        ("user", "middle-three"),
        ("assistant", "reply-three"),
    ):
        engine._append_history("placement-session", role, content)

    await engine.process_input("คุยต่อ", session_id="placement-session")

    assert provider.request is not None
    assert provider.request.system_prompt.index(
        "system-pre"
    ) < provider.request.system_prompt.index("กรอบบทบาท")
    for expected in ("system-post", "example-pre", "example-post", "direct-beat"):
        assert expected in provider.request.system_prompt
    positioned = [message.content for message in provider.request.messages]
    for expected in ("author-pre", "author-post", "history-depth"):
        assert any(expected in content for content in positioned)
    assert provider.request.messages[-1].role == "user"
    assert provider.request.messages[-1].content == "คุยต่อ"
