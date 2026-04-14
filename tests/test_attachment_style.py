"""Tests for AttachmentStyle in RelationshipEngine."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.relationship_engine import RelationshipEngine


def _engine() -> RelationshipEngine:
    return RelationshipEngine()


# ---------------------------------------------------------------------------
# get_attachment_style
# ---------------------------------------------------------------------------


class TestGetAttachmentStyle:
    def test_stranger_high_trust_is_secure(self) -> None:
        eng = _engine()
        # STAGE_STRANGER, trust = 0.8
        style = eng.get_attachment_style(trust=0.8)
        assert style.name == "Secure"

    def test_stranger_low_trust_is_avoidant(self) -> None:
        eng = _engine()
        style = eng.get_attachment_style(trust=0.2)
        assert style.name == "Avoidant"

    def test_obsession_stage_is_possessive(self) -> None:
        eng = _engine()
        eng.check_progression(sin_points=3000, arousal=90, trust=0.9)
        assert eng.current_stage is eng.STAGE_OBSESSION
        style = eng.get_attachment_style(trust=0.9)
        assert style.name == "Possessive"

    def test_lover_stage_mid_trust_is_anxious(self) -> None:
        eng = _engine()
        eng.check_progression(sin_points=200, arousal=70, trust=0.5)
        assert eng.current_stage is eng.STAGE_LOVER
        style = eng.get_attachment_style(trust=0.5)
        assert style.name == "Anxious"

    def test_lover_stage_high_trust_is_secure(self) -> None:
        eng = _engine()
        eng.check_progression(sin_points=200, arousal=70, trust=0.8)
        style = eng.get_attachment_style(trust=0.8)
        assert style.name == "Secure"

    def test_plaything_stage_mid_trust_is_anxious(self) -> None:
        eng = _engine()
        eng.check_progression(sin_points=600, arousal=40, trust=0.5)
        assert eng.current_stage is eng.STAGE_PLAYTHING
        style = eng.get_attachment_style(trust=0.5)
        assert style.name == "Anxious"

    def test_style_has_prompt_directive(self) -> None:
        eng = _engine()
        for trust in (0.1, 0.4, 0.7, 0.9):
            style = eng.get_attachment_style(trust=trust)
            assert isinstance(style.prompt_directive, str)
            assert len(style.prompt_directive) > 0


# ---------------------------------------------------------------------------
# check_progression accepts trust param
# ---------------------------------------------------------------------------


class TestCheckProgressionTrust:
    def test_accepts_trust_kwarg(self) -> None:
        eng = _engine()
        stage = eng.check_progression(sin_points=100, arousal=20, trust=0.7)
        assert stage is not None

    def test_default_trust_unchanged_behaviour(self) -> None:
        eng1 = _engine()
        eng2 = _engine()
        stage1 = eng1.check_progression(sin_points=600, arousal=30)
        stage2 = eng2.check_progression(sin_points=600, arousal=30, trust=0.5)
        assert stage1.name == stage2.name


# ---------------------------------------------------------------------------
# get_prompt_modifier includes attachment style
# ---------------------------------------------------------------------------


class TestGetPromptModifier:
    def test_modifier_includes_attachment_style_name(self) -> None:
        eng = _engine()
        modifier = eng.get_prompt_modifier(trust=0.8)
        assert "Attachment Style" in modifier
        assert "Secure" in modifier

    def test_modifier_includes_stage_name(self) -> None:
        eng = _engine()
        modifier = eng.get_prompt_modifier()
        assert eng.current_stage.name in modifier

    def test_modifier_includes_stage_directive(self) -> None:
        eng = _engine()
        modifier = eng.get_prompt_modifier()
        assert "Stage Directives" in modifier


# ---------------------------------------------------------------------------
# get_status includes attachment_style key
# ---------------------------------------------------------------------------


class TestGetStatus:
    def test_status_has_attachment_style_key(self) -> None:
        eng = _engine()
        status = eng.get_status()
        assert "attachment_style" in status

    def test_status_attachment_style_is_string(self) -> None:
        eng = _engine()
        status = eng.get_status(trust=0.5)
        assert isinstance(status["attachment_style"], str)

    def test_status_stage_key_present(self) -> None:
        eng = _engine()
        status = eng.get_status()
        assert "stage" in status and "description" in status
