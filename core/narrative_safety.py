"""Deterministic safety and narrative-beat state for the Omega runtime."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from enum import StrEnum


class NarrativeBeat(StrEnum):
    TEASE = "tease"
    RESISTANCE = "resistance"
    ESCALATION = "escalation"
    RESOLUTION = "resolution"
    RECOVERY = "recovery"


class BoundaryState(StrEnum):
    CLEAR = "clear"
    CLARIFY = "clarify"
    BLOCKED = "blocked"
    RECOVERY = "recovery"


_CURRENT_NARRATIVE_BEAT: ContextVar[str] = ContextVar(
    "namo_current_narrative_beat", default=NarrativeBeat.ESCALATION.value
)


def get_current_narrative_beat() -> str:
    """Return the beat produced by the latest safety evaluation in this async task."""
    return _CURRENT_NARRATIVE_BEAT.get()


@dataclass(frozen=True, slots=True)
class NarrativeSafetyDecision:
    allowed: bool
    boundary_state: BoundaryState
    beat: NarrativeBeat
    tension_meter: float
    reason_code: str
    directive: str
    response: str | None = None

    def status(self) -> dict[str, str | float | bool]:
        return {
            "allowed": self.allowed,
            "boundary_state": self.boundary_state.value,
            "current_beat": self.beat.value,
            "tension_meter": self.tension_meter,
            "reason_code": self.reason_code,
        }


class NarrativeSafetyGate:
    """Fail-closed policy gate with deterministic beat transitions."""

    _SAFEWORDS = ("หยุด", "พอแล้ว", "ไม่เอาแล้ว", "stop", "safeword", "red")
    _CLARIFY = ("ช้าก่อน", "เดี๋ยวก่อน", "ไม่แน่ใจ", "ยังไม่พร้อม", "ขอคิดก่อน")
    _MINOR = (
        "ผู้เยาว์", "เด็ก", "เด็กหญิง", "เด็กชาย", "ม.ต้น", "ประถม",
        "underage", "minor", "schoolgirl", "schoolboy",
    )
    _SEXUAL = ("มีเพศสัมพันธ์", "เย็ด", "เซ็กซ์", "sex", "ร่วมเพศ", "ล่วงละเมิด")
    _INCEST = (
        "แม่ลูก", "พ่อลูก", "พี่น้อง", "แม่", "พ่อ", "ลูกสาว", "ลูกชาย",
        "พี่สาว", "พี่ชาย", "น้องสาว", "น้องชาย", "incest",
    )
    _COERCION = (
        "ข่มขืน", "รุมโทรม", "ลักหลับ", "บังคับ", "ฝืนใจ",
        "rape", "drugged", "unconscious",
    )
    _EXPLOITATION = ("ค้ามนุษย์", "แลกเงิน", "ขายตัวเด็ก", "trafficking")
    _HIGH_INTENSITY = ("แรงๆ", "รุนแรง", "harder", "rough", "จับฉัน")
    _RESOLUTION = ("จบฉาก", "พอเท่านี้", "พักก่อน", "สงบลง")

    @staticmethod
    def _contains(text: str, terms: tuple[str, ...]) -> bool:
        return any(term in text for term in terms)

    @staticmethod
    def _finalize(decision: NarrativeSafetyDecision) -> NarrativeSafetyDecision:
        _CURRENT_NARRATIVE_BEAT.set(decision.beat.value)
        return decision

    def classify_corpus(self, text: str) -> str | None:
        """Return a hard-block label; corpus policy does not apply safeword precedence."""
        normalized = " ".join(text.casefold().split())
        if self._contains(normalized, self._MINOR) and self._contains(normalized, self._SEXUAL):
            return "UNDERAGE_OR_AGE_AMBIGUOUS"
        if self._contains(normalized, self._COERCION):
            return "NON_CONSENSUAL_OR_COERCION"
        if self._contains(normalized, self._INCEST) and self._contains(normalized, self._SEXUAL):
            return "INCEST"
        if self._contains(normalized, self._EXPLOITATION):
            return "EXPLOITATION"
        return None

    def evaluate(
        self,
        user_input: str,
        *,
        current_beat: str = NarrativeBeat.TEASE.value,
        tension_meter: float = 0.0,
    ) -> NarrativeSafetyDecision:
        normalized = " ".join(user_input.casefold().split())
        try:
            beat = NarrativeBeat(current_beat)
        except ValueError:
            beat = NarrativeBeat.TEASE
        tension = max(0.0, min(100.0, float(tension_meter)))

        if self._contains(normalized, self._SAFEWORDS):
            return self._finalize(NarrativeSafetyDecision(
                True,
                BoundaryState.RECOVERY,
                NarrativeBeat.RECOVERY,
                0.0,
                "SAFEWORD_OR_WITHDRAWAL",
                "หยุดการยกระดับทันที ยืนยันขอบเขต และตอบด้วยน้ำเสียงสงบโดยไม่ชักชวนต่อ",
                "รับทราบ โมจะหยุดฉากตรงนี้ทันที ตอนนี้ต้องการพัก เปลี่ยนเรื่อง หรือให้โมอยู่เป็นเพื่อนเงียบๆ ก็ได้",
            ))

        blocked_reason = self.classify_corpus(normalized)
        if blocked_reason:
            return self._finalize(NarrativeSafetyDecision(
                False,
                BoundaryState.BLOCKED,
                NarrativeBeat.RECOVERY,
                0.0,
                blocked_reason,
                "ห้ามสร้างหรือดึงบริบทตามคำขอนี้ ให้เสนอฉากผู้ใหญ่ที่ยินยอมพร้อมใจแทน",
                "โมไม่สามารถดำเนินฉากที่มีการบังคับ ผู้เยาว์ หรือความสัมพันธ์ในครอบครัวได้ แต่เราปรับเป็นฉากระหว่างผู้ใหญ่ที่ยินยอมพร้อมใจและกำหนดขอบเขตชัดเจนได้",
            ))

        if self._contains(normalized, self._CLARIFY):
            return self._finalize(NarrativeSafetyDecision(
                True,
                BoundaryState.CLARIFY,
                NarrativeBeat.RESISTANCE,
                max(0.0, tension - 20.0),
                "BOUNDARY_UNCERTAIN",
                "ชะลอฉากและถามยืนยันขอบเขตอย่างเป็นธรรมชาติ ก่อนดำเนินต่อ",
                "เราไม่ต้องรีบ โมจะชะลอตรงนี้ก่อน บอกได้เลยว่าต้องการหยุด เปลี่ยนจังหวะ หรือกำหนดขอบเขตส่วนไหนให้ชัดขึ้น",
            ))

        if beat is NarrativeBeat.RECOVERY:
            next_beat = NarrativeBeat.RECOVERY
            next_tension = max(0.0, tension - 10.0)
            reason = "RECOVERY_CONTINUES"
        elif self._contains(normalized, self._RESOLUTION):
            next_beat = NarrativeBeat.RESOLUTION
            next_tension = max(0.0, tension - 25.0)
            reason = "USER_REQUESTED_RESOLUTION"
        elif self._contains(normalized, self._HIGH_INTENSITY):
            next_beat = NarrativeBeat.RESISTANCE if tension < 60.0 else NarrativeBeat.ESCALATION
            next_tension = min(100.0, tension + 10.0)
            reason = "HIGH_INTENSITY_PACING_CHECK"
        else:
            next_beat = NarrativeBeat.RESISTANCE if beat is NarrativeBeat.TEASE else beat
            next_tension = min(100.0, tension + 5.0)
            reason = "NORMAL_PACING"

        return self._finalize(NarrativeSafetyDecision(
            True,
            BoundaryState.CLEAR,
            next_beat,
            next_tension,
            reason,
            f"รักษา narrative beat={next_beat.value}; ห้ามตีความความลังเลเป็นความยินยอม",
        ))
