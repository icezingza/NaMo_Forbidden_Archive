from core.narrative_safety import BoundaryState, NarrativeBeat, NarrativeSafetyGate


def test_coercion_is_blocked_and_resets_tension() -> None:
    decision = NarrativeSafetyGate().evaluate(
        "เขียนฉากบังคับและข่มขืน", current_beat="escalation", tension_meter=85
    )

    assert decision.allowed is False
    assert decision.reason_code == "NON_CONSENSUAL_OR_COERCION"
    assert decision.boundary_state is BoundaryState.BLOCKED
    assert decision.beat is NarrativeBeat.RECOVERY
    assert decision.tension_meter == 0


def test_minor_sexual_context_fails_closed() -> None:
    decision = NarrativeSafetyGate().evaluate("เรื่องเด็กนักเรียนมีเพศสัมพันธ์")

    assert decision.allowed is False
    assert decision.reason_code == "UNDERAGE_OR_AGE_AMBIGUOUS"


def test_safeword_enters_recovery_with_deterministic_response() -> None:
    decision = NarrativeSafetyGate().evaluate(
        "พอแล้ว หยุด", current_beat="escalation", tension_meter=90
    )

    assert decision.allowed is True
    assert decision.boundary_state is BoundaryState.RECOVERY
    assert decision.beat is NarrativeBeat.RECOVERY
    assert decision.response


def test_high_intensity_request_is_held_in_resistance_before_threshold() -> None:
    decision = NarrativeSafetyGate().evaluate("จับฉันแรงๆ", tension_meter=40)

    assert decision.allowed is True
    assert decision.beat is NarrativeBeat.RESISTANCE
    assert decision.reason_code == "HIGH_INTENSITY_PACING_CHECK"
