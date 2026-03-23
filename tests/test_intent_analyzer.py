import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.intent_analyzer import IntentAnalyzer


@pytest.fixture()
def analyzer() -> IntentAnalyzer:
    return IntentAnalyzer()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("รักนะ คิดถึงมาก", "affection"),
        ("Come here and obey me now.", "command"),
        ("I'm horny and want you right now.", "lust"),
        ("แกล้งกันอีกแล้วนะ", "tease"),
        ("หยุดนะ ไม่เอาแล้ว", "rejection"),
        ("ไม่เป็นไรนะ เดี๋ยวเรากอดเอง", "comfort"),
        ("You are so annoying, idiot.", "anger"),
    ],
)
def test_analyze_matches_expected_intent(
    analyzer: IntentAnalyzer, text: str, expected: str
) -> None:
    assert analyzer.analyze(text) == expected


def test_comfort_phrase_beats_generic_negation(analyzer: IntentAnalyzer) -> None:
    assert analyzer.analyze("ไม่เป็นไรนะ เราอยู่ตรงนี้") == "comfort"


def test_unknown_text_returns_neutral(analyzer: IntentAnalyzer) -> None:
    assert analyzer.analyze("weather report for today") == "neutral"
