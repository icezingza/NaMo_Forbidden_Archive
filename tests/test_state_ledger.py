import json
from dataclasses import FrozenInstanceError

import pytest

from core.state_ledger import (
    SessionState,
    StateConflictError,
    StateLedger,
    StateLedgerCorruptionError,
)


def test_missing_session_returns_frozen_fresh_state_without_writing(tmp_path) -> None:
    path = tmp_path / "state" / "namo_state.json"
    ledger = StateLedger(path)

    state = ledger.load_state("session-a")

    assert state.session_id == "session-a"
    assert state.turn_count == 0
    assert not path.exists()
    with pytest.raises(FrozenInstanceError):
        state.turn_count = 1  # type: ignore[misc]


def test_commit_persists_state_and_transition_history(tmp_path) -> None:
    path = tmp_path / "namo_state.json"
    ledger = StateLedger(path)
    initial = ledger.load_state("session-a")

    updated = ledger.commit_transition(initial, 0.55, {"event": "bond"})

    assert updated.fused_score == 0.55
    assert updated.relationship_stage == "deep_attachment"
    assert updated.turn_count == 1
    assert updated.last_updated.endswith("Z")
    assert ledger.load_state("session-a") == updated
    history = ledger.get_history("session-a")
    assert len(history) == 1
    assert history[0]["previous_stage"] == "awakening"
    assert history[0]["new_stage"] == "deep_attachment"
    assert history[0]["metadata"] == {"event": "bond"}


def test_negative_delta_demotes_stage_and_clamps_score(tmp_path) -> None:
    ledger = StateLedger(tmp_path / "ledger.json")
    state = ledger.commit_transition(ledger.load_state("session-a"), 1.5)
    assert state.relationship_stage == "maximum_resonance"

    state = ledger.commit_transition(state, -2.0)

    assert state.fused_score == 0.0
    assert state.relationship_stage == "awakening"


def test_commit_preserves_other_sessions(tmp_path) -> None:
    path = tmp_path / "ledger.json"
    ledger = StateLedger(path)
    state_a = ledger.commit_transition(ledger.load_state("a"), 0.2)
    state_b = ledger.commit_transition(ledger.load_state("b"), 0.8)

    state_a = ledger.commit_transition(state_a, 0.1)

    assert ledger.load_state("a") == state_a
    assert ledger.load_state("b") == state_b
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert set(payload["sessions"]) == {"a", "b"}


def test_stale_snapshot_is_rejected_without_lost_update(tmp_path) -> None:
    ledger_a = StateLedger(tmp_path / "ledger.json")
    ledger_b = StateLedger(tmp_path / "ledger.json")
    stale_a = ledger_a.load_state("shared")
    stale_b = ledger_b.load_state("shared")
    committed = ledger_a.commit_transition(stale_a, 0.4)

    with pytest.raises(StateConflictError, match="stale state"):
        ledger_b.commit_transition(stale_b, 0.2)

    assert ledger_b.load_state("shared") == committed
    assert len(ledger_b.get_history("shared")) == 1


def test_corrupt_json_is_not_silently_overwritten(tmp_path) -> None:
    path = tmp_path / "ledger.json"
    path.write_text("{broken", encoding="utf-8")
    ledger = StateLedger(path)

    with pytest.raises(StateLedgerCorruptionError):
        ledger.load_state("session-a")
    with pytest.raises(StateLedgerCorruptionError):
        ledger.commit_transition(SessionState("session-a"), 0.1)

    assert path.read_text(encoding="utf-8") == "{broken"


def test_malformed_transition_history_blocks_commit(tmp_path) -> None:
    path = tmp_path / "ledger.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sessions": {
                    "session-a": {
                        "state": {"session_id": "session-a", "turn_count": 0},
                        "transitions": ["invalid"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    ledger = StateLedger(path)

    with pytest.raises(StateLedgerCorruptionError, match="list of objects"):
        ledger.commit_transition(ledger.load_state("session-a"), 0.1)


def test_candidate_single_session_format_is_migrated_on_commit(tmp_path) -> None:
    path = tmp_path / "ledger.json"
    path.write_text(
        json.dumps(
            {
                "session_id": "legacy",
                "relationship_stage": "synchronized",
                "fused_score": 0.3,
                "attachment_style": "secure",
                "confidence": 0.8,
                "turn_count": 2,
                "metadata": {"source": "candidate"},
            }
        ),
        encoding="utf-8",
    )
    ledger = StateLedger(path)

    migrated = ledger.load_state("legacy")
    committed = ledger.commit_transition(migrated, 0.1)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert committed.turn_count == 3
    assert payload["sessions"]["legacy"]["state"]["fused_score"] == 0.4


def test_transition_history_is_bounded(tmp_path) -> None:
    ledger = StateLedger(tmp_path / "ledger.json", history_limit=2)
    state = ledger.load_state("session-a")
    for _ in range(3):
        state = ledger.commit_transition(state, 0.1)

    history = ledger.get_history("session-a")

    assert len(history) == 2
    assert [item["turn"] for item in history] == [2, 3]


def test_metadata_is_defensively_copied_and_must_be_json_serializable(tmp_path) -> None:
    ledger = StateLedger(tmp_path / "ledger.json")
    metadata = {"nested": {"value": 1}}
    state = ledger.commit_transition(ledger.load_state("session-a"), 0.1, metadata)
    metadata["nested"]["value"] = 999
    state.metadata["nested"]["value"] = 500

    loaded = ledger.load_state("session-a")

    assert loaded.metadata["nested"]["value"] == 1
    with pytest.raises(ValueError, match="JSON-serializable"):
        ledger.commit_transition(loaded, 0.1, {"bad": object()})


@pytest.mark.parametrize("session_id", ["", "   ", "x" * 257])
def test_invalid_session_ids_are_rejected(tmp_path, session_id: str) -> None:
    ledger = StateLedger(tmp_path / "ledger.json")

    with pytest.raises(ValueError):
        ledger.load_state(session_id)


@pytest.mark.parametrize("delta", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_deltas_are_rejected(tmp_path, delta: float) -> None:
    ledger = StateLedger(tmp_path / "ledger.json")

    with pytest.raises(ValueError, match="finite"):
        ledger.commit_transition(ledger.load_state("session-a"), delta)


def test_default_path_does_not_overwrite_legacy_root_state(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    legacy_path = tmp_path / "namo_state.json"
    legacy_content = {"mood": "Neutral", "corruption": 0}
    legacy_path.write_text(json.dumps(legacy_content), encoding="utf-8")
    ledger = StateLedger()

    ledger.commit_transition(ledger.load_state("session-a"), 0.2)

    assert json.loads(legacy_path.read_text(encoding="utf-8")) == legacy_content
    assert (tmp_path / "state" / "namo_state.json").exists()
