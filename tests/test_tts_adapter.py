"""Tests for adapters/tts.py — both online (mocked) and offline paths."""
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def _make_adapter(api_key: str | None = None, elevenlabs_available: bool = True):
    """Build a TTSAdapter with controlled environment."""
    with patch("adapters.tts._ELEVENLABS_AVAILABLE", elevenlabs_available), patch(
        "adapters.tts.settings"
    ) as mock_settings:
        mock_settings.elevenlabs_api_key = api_key
        mock_settings.elevenlabs_voice_id = "Rachel"
        mock_settings.elevenlabs_model = "eleven_multilingual_v2"
        mock_settings.tts_output_dir = "/tmp/tts_test_output"

        if elevenlabs_available and api_key:
            mock_client = MagicMock()
            with patch("adapters.tts._ElevenLabsClient", return_value=mock_client):
                from adapters.tts import TTSAdapter

                adapter = TTSAdapter()
                adapter._client = mock_client
                return adapter
        else:
            from adapters.tts import TTSAdapter

            return TTSAdapter()


def test_synthesize_returns_none_when_no_api_key():
    """TTSAdapter.synthesize() returns None when no API key is configured."""
    from adapters.tts import TTSAdapter

    with patch("adapters.tts.settings") as mock_settings, patch(
        "adapters.tts._ELEVENLABS_AVAILABLE", True
    ):
        mock_settings.elevenlabs_api_key = None
        mock_settings.elevenlabs_voice_id = "Rachel"
        mock_settings.elevenlabs_model = "eleven_multilingual_v2"
        mock_settings.tts_output_dir = "/tmp/tts_no_key"
        adapter = TTSAdapter()

    assert adapter._client is None
    assert adapter.synthesize("สวัสดี") is None


def test_synthesize_returns_none_when_package_missing():
    """TTSAdapter.synthesize() returns None when elevenlabs package is absent."""
    from adapters.tts import TTSAdapter

    with patch("adapters.tts._ELEVENLABS_AVAILABLE", False), patch(
        "adapters.tts.settings"
    ) as mock_settings:
        mock_settings.elevenlabs_api_key = "fake-key"
        mock_settings.elevenlabs_voice_id = "Rachel"
        mock_settings.elevenlabs_model = "eleven_multilingual_v2"
        mock_settings.tts_output_dir = "/tmp/tts_no_pkg"
        adapter = TTSAdapter()

    assert adapter._client is None
    assert adapter.synthesize("test") is None


def test_synthesize_saves_file_and_returns_relative_path(tmp_path):
    """TTSAdapter.synthesize() saves audio bytes and returns an Audio_Layers/tts/... path."""
    import importlib
    import adapters.tts as tts_module

    fake_audio = b"\x00\x01\x02\x03"
    mock_client = MagicMock()
    mock_client.generate.return_value = fake_audio

    with patch("adapters.tts._ELEVENLABS_AVAILABLE", True), patch(
        "adapters.tts.settings"
    ) as mock_settings, patch(
        "adapters.tts._ElevenLabsClient", return_value=mock_client
    ):
        mock_settings.elevenlabs_api_key = "fake-key"
        mock_settings.elevenlabs_voice_id = "Rachel"
        mock_settings.elevenlabs_model = "eleven_multilingual_v2"
        mock_settings.tts_output_dir = str(tmp_path)

        importlib.reload(tts_module)
        from adapters.tts import TTSAdapter

        adapter = TTSAdapter()

    adapter._client = mock_client
    adapter._output_dir = tmp_path

    result = adapter.synthesize("สวัสดี")

    assert result is not None
    assert result.startswith("Audio_Layers/tts/")
    assert result.endswith(".mp3")

    # File should actually exist
    filename = result.split("/")[-1]
    assert (tmp_path / filename).read_bytes() == fake_audio


def test_synthesize_returns_none_on_api_error():
    """TTSAdapter.synthesize() returns None (not raises) when the API call fails."""
    from adapters.tts import TTSAdapter

    mock_client = MagicMock()
    mock_client.generate.side_effect = RuntimeError("API down")

    with patch("adapters.tts.settings") as mock_settings:
        mock_settings.elevenlabs_api_key = "fake-key"
        mock_settings.elevenlabs_voice_id = "Rachel"
        mock_settings.elevenlabs_model = "eleven_multilingual_v2"
        mock_settings.tts_output_dir = "/tmp/tts_err"
        from adapters.tts import TTSAdapter as _A

        adapter = _A.__new__(_A)
        adapter._client = mock_client
        adapter._voice_id = "Rachel"
        adapter._model = "eleven_multilingual_v2"
        from pathlib import Path

        adapter._output_dir = Path("/tmp/tts_err")

    assert adapter.synthesize("error test") is None
