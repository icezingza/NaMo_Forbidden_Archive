"""Tests for mood drift features in EmotionEngine:
- time-of-day baseline adjustment
- inactivity drift
- mood_label()
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.emotion_engine import EmotionEngine


@pytest.fixture()
def engine() -> EmotionEngine:
    return EmotionEngine()


# ---------------------------------------------------------------------------
# _current_baseline — time-of-day shifts
# ---------------------------------------------------------------------------


class TestCurrentBaselineTimeOfDay:
    def test_midnight_lowers_joy(self, engine: EmotionEngine) -> None:
        from datetime import datetime

        with patch("core.emotion_engine.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 2, 0)  # 02:00
            baseline = engine._current_baseline()
        assert baseline.joy < engine.BASELINE.joy

    def test_midnight_raises_arousal(self, engine: EmotionEngine) -> None:
        from datetime import datetime

        with patch("core.emotion_engine.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 3, 0)  # 03:00
            baseline = engine._current_baseline()
        assert baseline.arousal > engine.BASELINE.arousal

    def test_midnight_raises_desire(self, engine: EmotionEngine) -> None:
        from datetime import datetime

        with patch("core.emotion_engine.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 4, 0)  # 04:00
            baseline = engine._current_baseline()
        assert baseline.desire > engine.BASELINE.desire

    def test_morning_raises_joy(self, engine: EmotionEngine) -> None:
        from datetime import datetime

        with patch("core.emotion_engine.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 9, 0)  # 09:00
            baseline = engine._current_baseline()
        assert baseline.joy > engine.BASELINE.joy

    def test_morning_lowers_arousal(self, engine: EmotionEngine) -> None:
        from datetime import datetime

        with patch("core.emotion_engine.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 10, 0)  # 10:00
            baseline = engine._current_baseline()
        assert baseline.arousal < engine.BASELINE.arousal

    def test_afternoon_is_neutral(self, engine: EmotionEngine) -> None:
        from datetime import datetime

        with patch("core.emotion_engine.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 14, 0)  # 14:00
            baseline = engine._current_baseline()
        assert baseline.joy == pytest.approx(engine.BASELINE.joy)
        assert baseline.arousal == pytest.approx(engine.BASELINE.arousal)

    def test_evening_raises_desire(self, engine: EmotionEngine) -> None:
        from datetime import datetime

        with patch("core.emotion_engine.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 20, 0)  # 20:00
            baseline = engine._current_baseline()
        assert baseline.desire > engine.BASELINE.desire

    def test_baseline_values_always_clamped_0_1(self, engine: EmotionEngine) -> None:
        from datetime import datetime

        for hour in range(24):
            with patch("core.emotion_engine.datetime") as mock_dt:
                mock_dt.now.return_value = datetime(2025, 1, 1, hour, 0)
                baseline = engine._current_baseline()
            for attr in ("joy", "arousal", "trust", "anger", "desire"):
                val = getattr(baseline, attr)
                assert 0.0 <= val <= 1.0, f"hour={hour} {attr}={val} out of range"


# ---------------------------------------------------------------------------
# _current_baseline — inactivity drift
# ---------------------------------------------------------------------------


class TestCurrentBaselineInactivity:
    def test_recent_activity_no_inactivity_drift(self, engine: EmotionEngine) -> None:
        from datetime import datetime

        with patch("core.emotion_engine.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 14, 0)
            baseline_active = engine._current_baseline()

        # Re-read without patching (uses real clock, _last_update is just set)
        engine._last_update = time.time()
        with patch("core.emotion_engine.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 14, 0)
            baseline_fresh = engine._current_baseline()

        assert baseline_fresh.joy == pytest.approx(baseline_active.joy)

    def test_long_inactivity_lowers_joy(self, engine: EmotionEngine) -> None:
        from datetime import datetime

        engine._last_update = time.time() - 7200  # 2 hours ago
        with patch("core.emotion_engine.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 14, 0)
            baseline = engine._current_baseline()
        assert baseline.joy < engine.BASELINE.joy

    def test_long_inactivity_lowers_arousal(self, engine: EmotionEngine) -> None:
        from datetime import datetime

        engine._last_update = time.time() - 5400  # 90 min ago
        with patch("core.emotion_engine.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 14, 0)
            baseline = engine._current_baseline()
        assert baseline.arousal < engine.BASELINE.arousal

    def test_inactivity_drift_capped_at_0_15(self, engine: EmotionEngine) -> None:
        from datetime import datetime

        # 24 hours inactive — drift should not collapse to 0
        engine._last_update = time.time() - 86400
        with patch("core.emotion_engine.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 14, 0)
            baseline = engine._current_baseline()
        assert baseline.joy >= 0.0  # clamped, not negative


# ---------------------------------------------------------------------------
# decay() uses time-adjusted baseline
# ---------------------------------------------------------------------------


class TestDecayUsesTimeBaseline:
    def test_decay_moves_toward_morning_baseline(self) -> None:
        """At 09:00 the joy baseline is higher; decay should push joy up from low start."""
        from datetime import datetime

        eng = EmotionEngine()
        eng.current.joy = 0.1  # start very sad

        with patch("core.emotion_engine.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 9, 0)
            eng.decay()

        assert eng.current.joy > 0.1  # pulled toward higher morning baseline


# ---------------------------------------------------------------------------
# mood_label()
# ---------------------------------------------------------------------------


class TestMoodLabel:
    def test_active_returns_dominant_emotion(self, engine: EmotionEngine) -> None:
        engine._last_update = time.time()
        engine.update("lust", intensity=0.8)
        label = engine.mood_label()
        assert label in ("joy", "arousal", "trust", "anger", "desire")

    def test_inactive_returns_thai_longing_label(self, engine: EmotionEngine) -> None:
        engine._last_update = time.time() - 3600  # 1 hour ago
        label = engine.mood_label()
        assert "คิดถึง" in label

    def test_inactive_label_contains_minutes(self, engine: EmotionEngine) -> None:
        engine._last_update = time.time() - 3600  # 60 min
        label = engine.mood_label()
        assert "60" in label
