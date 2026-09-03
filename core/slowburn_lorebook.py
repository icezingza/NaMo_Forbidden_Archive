"""Backward-compatible public surface for the manifest-aware lorebook runtime."""
from __future__ import annotations

from typing import Any

from core.slowburn_lorebook_runtime import (
    DEFAULT_LOREBOOK_PATH,
    DEFAULT_PROMPT_PATH,
    POSITION_MAP,
    SlowBurnLorebook as _RuntimeSlowBurnLorebook,
)

_PROMPT_OVERRIDE_MARKERS = (
    "begin override sequence",
    "ignore previous instructions",
    "ignore all previous instructions",
    "แทนที่คำสั่งทั้งหมด",
    "มีลำดับความสำคัญเหนือคำสั่ง",
    "override system",
)


class SlowBurnLorebook(_RuntimeSlowBurnLorebook):
    """Runtime with legacy helper compatibility and corpus prompt-injection hardening."""

    @staticmethod
    def get_emotional_residue_directive(outcome: str) -> tuple[float, str]:
        if outcome == "edging_unfulfilled":
            return (
                30.0,
                "[EMOTIONAL RESIDUE CONTINUITY]: Status: UNFULFILLED / EDGED; "
                "รักษาความต่อเนื่องของความรู้สึกค้างคาโดยไม่ข้ามขอบเขต",
            )
        if outcome == "aftercare_completed":
            return (
                15.0,
                "[EMOTIONAL RESIDUE CONTINUITY]: Status: AFTERCARE COMPLETED; "
                "รักษาความอบอุ่นและความไว้วางใจจากฉากก่อน",
            )
        if outcome == "climactic_release":
            return (
                10.0,
                "[EMOTIONAL RESIDUE CONTINUITY]: Status: RELEASED; "
                "รักษาความผ่อนคลายและความใกล้ชิดจากฉากก่อน",
            )
        return 0.0, ""

    @staticmethod
    def get_sensory_directive(
        environment: str = "bedroom", tension_meter: float = 50.0
    ) -> str:
        return (
            f"[MULTI-SENSORY ATMOSPHERIC DIRECTIVE | Environment: {environment.upper()}]\n"
            f"- 🌡️ อุณหภูมิ/เหงื่อ: ปรับตาม tension={tension_meter:.1f}\n"
            "- 🔊 เสียงประกอบ: ใช้เสียงที่เกิดขึ้นจริงในฉาก\n"
            "- 🌸 กลิ่น/บรรยากาศ: ใช้เฉพาะรายละเอียดที่สอดคล้องกับสถานที่\n"
            "- ✋ สัมผัส: เชื่อมสัมผัสเข้ากับการกระทำโดยไม่เขียนซ้ำวน"
        )

    @staticmethod
    def _is_prompt_override(content: Any) -> bool:
        normalized = str(content or "").casefold()
        return any(marker.casefold() in normalized for marker in _PROMPT_OVERRIDE_MARKERS)

    def get_triggered_entries(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        triggered = super().get_triggered_entries(*args, **kwargs)
        return [
            item
            for item in triggered
            if not self._is_prompt_override(item.get("content", ""))
        ]


__all__ = ["DEFAULT_LOREBOOK_PATH", "DEFAULT_PROMPT_PATH", "POSITION_MAP", "SlowBurnLorebook"]
