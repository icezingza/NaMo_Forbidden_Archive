from __future__ import annotations

from core.engines.namonexus_fusion import NamoNexusEngine
from core.relationship_engine import RelationshipEngine


def test_relationship_engine_persists_stage(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    engine = RelationshipEngine(persistence_key="session-a")
    engine.check_progression(sin_points=1200, arousal=70, trust=0.6)
    assert engine.current_stage is engine.STAGE_LOVER

    reloaded = RelationshipEngine(persistence_key="session-a")
    assert reloaded.current_stage is reloaded.STAGE_LOVER
    assert reloaded.stage_history


def test_relationship_engine_demotes_after_low_signal_streak(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    engine = RelationshipEngine(persistence_key="session-b")
    engine.check_progression(sin_points=3000, arousal=90, trust=0.9)
    assert engine.current_stage is engine.STAGE_OBSESSION

    engine.check_progression(sin_points=0, arousal=0, trust=0.2)
    assert engine.current_stage is engine.STAGE_OBSESSION

    engine.check_progression(sin_points=0, arousal=0, trust=0.2)
    assert engine.current_stage is engine.STAGE_LOVER


def test_fusion_engine_clamps_outputs_and_persists_state(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    engine = NamoNexusEngine(persistence_key="fusion-a")
    engine.fused_score = 1.0
    engine.update(score=2.5, confidence=-3.0, modality="face")

    assert 0.0 <= engine.fused_score <= 1.0
    assert 0.0 <= engine.confidence <= 1.0

    reloaded = NamoNexusEngine(persistence_key="fusion-a")
    assert reloaded.fused_score == engine.fused_score
    assert reloaded.confidence == engine.confidence
    assert isinstance(reloaded.history, list)


def test_fusion_engine_recovers_from_drift_after_cooldown(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    engine = NamoNexusEngine(persistence_key="fusion-b")
    engine.fused_score = 1.0

    monkeypatch.setattr("core.engines.namonexus_fusion.time.time", lambda: 100.0)
    engine.update(score=0.0, confidence=1.0, modality="face")
    assert engine.has_drift_alarm is True

    monkeypatch.setattr("core.engines.namonexus_fusion.time.time", lambda: 106.0)
    engine.update(score=0.0, confidence=0.5, modality="text")
    assert engine.has_drift_alarm is False
