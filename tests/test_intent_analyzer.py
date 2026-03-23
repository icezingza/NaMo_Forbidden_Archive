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


@pytest.mark.parametrize(
    "text",
    [
        "จำได้ไหม ตอนนั้นเราเจอกันครั้งแรก",
        "เมื่อก่อนนะ สมัยก่อนเราไม่เคยทะเลาะกัน",
        "remember when we used to talk every night",
        "ย้อนหลังไปวันนั้น ฉันยังจำได้เลย",
    ],
)
def test_nostalgia_intent_detected(analyzer: IntentAnalyzer, text: str) -> None:
    assert analyzer.analyze(text) == "nostalgia"


def test_nostalgia_in_priority_list(analyzer: IntentAnalyzer) -> None:
    assert "nostalgia" in analyzer._PRIORITY


def test_nostalgia_keywords_registered(analyzer: IntentAnalyzer) -> None:
    assert "nostalgia" in analyzer.themes
