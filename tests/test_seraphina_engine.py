"""Tests for seraphina_ai_complete.py — SeraphinaAI process_input (no TF required)."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_engine():
    from seraphina_ai_complete import SeraphinaAI

    return SeraphinaAI()


# ===========================================================================
# process_input contract
# ===========================================================================


class TestSeraphinaProcessInput:
    def setup_method(self):
        self.engine = _make_engine()

    def test_returns_required_keys(self):
        result = self.engine.process_input("Hello", session_id="s1")
        assert "text" in result
        assert "media_trigger" in result
        assert "system_status" in result

    def test_text_is_non_empty_string(self):
        result = self.engine.process_input("test", session_id="s1")
        assert isinstance(result["text"], str)
        assert len(result["text"]) > 0

    def test_media_trigger_keys(self):
        result = self.engine.process_input("test", session_id="s1")
        media = result["media_trigger"]
        assert "image" in media
        assert "audio" in media
        assert "tts" in media

    def test_system_status_has_detected_emotion(self):
        result = self.engine.process_input("hello", session_id="s1")
        assert "detected_emotion" in result["system_status"]

    def test_system_status_has_strategy(self):
        result = self.engine.process_input("hello", session_id="s1")
        assert "strategy" in result["system_status"]

    def test_multiple_calls_succeed(self):
        for i in range(3):
            result = self.engine.process_input(f"message {i}", session_id="multi")
            assert "text" in result

    def test_none_session_id_is_handled(self):
        result = self.engine.process_input("hi", session_id=None)
        assert result["text"]


# ===========================================================================
# get_status
# ===========================================================================


class TestSeraphinaGetStatus:
    def setup_method(self):
        self.engine = _make_engine()

    def test_get_status_returns_engine_name(self):
        status = self.engine.get_status()
        assert status["engine"] == "SeraphinaAI"

    def test_get_status_online(self):
        status = self.engine.get_status()
        assert status["status"] == "online"

    def test_get_status_has_persona(self):
        status = self.engine.get_status()
        assert "persona" in status
        assert "Seraphina" in status["persona"]

    def test_get_status_has_emotion_from_cognitive(self):
        status = self.engine.get_status()
        assert "emotion" in status


# ===========================================================================
# _build_system_prompt
# ===========================================================================


class TestSeraphinaBuildSystemPrompt:
    def test_prompt_contains_name(self):
        engine = _make_engine()
        prompt = engine._build_system_prompt("flirting")
        assert "Seraphina" in prompt

    def test_prompt_contains_context(self):
        engine = _make_engine()
        prompt = engine._build_system_prompt("conflict")
        assert "conflict" in prompt


# ===========================================================================
# interact() — covers lines 366-413
# ===========================================================================


class TestSeraphinaInteract:
    def test_interact_returns_string(self, capsys):
        engine = _make_engine()
        result = engine.interact("Hello there")
        assert isinstance(result, str) and len(result) > 0

    def test_interact_with_custom_user_name(self, capsys):
        engine = _make_engine()
        result = engine.interact("I am intrigued", user_name="TestUser")
        assert result is not None
        captured = capsys.readouterr()
        assert "TestUser" in captured.out

    def test_interact_curious_input_triggers_imagination(self, capsys):
        engine = _make_engine()
        # "curious" keyword in detected emotion triggers imagination.spark_idea()
        engine.interact("why is this curious what who")
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_interact_rejection_updates_contact(self):
        engine = _make_engine()
        engine.interact("no stop away hate", user_name="Villain")
        assert engine.social.contacts.get("Villain", {}).get("status") == "Challenged"

    def test_interact_attracted_updates_contact(self):
        engine = _make_engine()
        engine.interact("love charm beautiful desire", user_name="Admirer")
        assert engine.social.contacts.get("Admirer", {}).get("status") == "Captivated"

    def test_interact_saves_memory(self):
        engine = _make_engine()
        engine.interact("test input", user_name="Tester")
        assert any("Tester" in m for m in engine.identity.memory_stream)


# ===========================================================================
# SeraphinaIdentity — adapt_goal
# ===========================================================================


class TestSeraphinaIdentityAdaptGoal:
    def test_adapt_goal_adds_to_goals(self):
        from seraphina_ai_complete import SeraphinaIdentity

        identity = SeraphinaIdentity()
        before_count = len(identity.goals)
        identity.adapt_goal("some new experience")
        assert len(identity.goals) == before_count + 1

    def test_adapt_goal_returns_new_goal_string(self):
        from seraphina_ai_complete import SeraphinaIdentity

        identity = SeraphinaIdentity()
        new_goal = identity.adapt_goal("fascinating event")
        assert isinstance(new_goal, str) and len(new_goal) > 0


# ===========================================================================
# RelationshipManager — update branches
# ===========================================================================


class TestRelationshipManagerUpdate:
    def test_update_new_contact(self):
        from seraphina_ai_complete import RelationshipManager

        mgr = RelationshipManager()
        mgr.update("NewPerson", "Neutral")
        assert "NewPerson" in mgr.contacts

    def test_update_rejection_sentiment(self):
        from seraphina_ai_complete import RelationshipManager

        mgr = RelationshipManager()
        mgr.update("Someone", "Rejection/Hostile")
        assert mgr.contacts["Someone"]["status"] == "Challenged"

    def test_update_attracted_sentiment(self):
        from seraphina_ai_complete import RelationshipManager

        mgr = RelationshipManager()
        mgr.update("Someone", "Attracted/Romantic")
        assert mgr.contacts["Someone"]["status"] == "Captivated"
