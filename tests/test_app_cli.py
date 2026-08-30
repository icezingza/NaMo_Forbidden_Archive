import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def _make_dark_system():
    """Return a mocked DarkNaMoSystem."""
    mock_system = MagicMock()
    mock_system.process_input.return_value = {
        "text": "Hello",
        "media_trigger": {"image": None, "audio": None, "tts": None},
        "system_status": {"intensity": 1},
    }
    return mock_system


def test_main_loop_normal_interaction(capsys):
    """main_loop processes user input and prints the response text."""
    mock_system = _make_dark_system()

    with (
        patch("app.DarkNaMoSystem", return_value=mock_system),
        patch("builtins.input", side_effect=["สวัสดี", "exit"]),
    ):
        from app import main_loop

        main_loop()

    mock_system.process_input.assert_called_once()
    captured = capsys.readouterr()
    assert "NaMo FORBIDDEN CORE" in captured.out


def test_main_loop_exit_command(capsys, caplog):
    """main_loop exits cleanly when user types 'exit'."""
    mock_system = _make_dark_system()

    with (
        patch("app.DarkNaMoSystem", return_value=mock_system),
        patch("builtins.input", side_effect=["exit"]),
    ):
        from app import main_loop

        main_loop()

    mock_system.process_input.assert_not_called()
    captured = capsys.readouterr()
    full_output = captured.out + captured.err + caplog.text
    assert "Void" in full_output or "Deactivating" in full_output


def test_main_loop_quit_command(capsys):
    """main_loop exits cleanly when user types 'quit'."""
    mock_system = _make_dark_system()

    with (
        patch("app.DarkNaMoSystem", return_value=mock_system),
        patch("builtins.input", side_effect=["quit"]),
    ):
        from app import main_loop

        main_loop()

    mock_system.process_input.assert_not_called()


def test_main_loop_keyboard_interrupt(capsys, caplog):
    """main_loop handles KeyboardInterrupt gracefully."""
    mock_system = _make_dark_system()

    with (
        patch("app.DarkNaMoSystem", return_value=mock_system),
        patch("builtins.input", side_effect=KeyboardInterrupt),
    ):
        from app import main_loop

        main_loop()  # Should not raise

    captured = capsys.readouterr()
    full_output = captured.out + captured.err + caplog.text
    assert "Interrupted" in full_output or "Shutting" in full_output


def test_main_loop_exception_during_input(capsys, caplog):
    """main_loop catches exceptions during process_input and continues the loop."""
    mock_system = _make_dark_system()
    mock_system.process_input.side_effect = [RuntimeError("oops"), None]

    with (
        patch("app.DarkNaMoSystem", return_value=mock_system),
        patch("builtins.input", side_effect=["bad input", "exit"]),
    ):
        from app import main_loop

        main_loop()  # Should not raise

    captured = capsys.readouterr()
    full_output = captured.out + captured.err + caplog.text
    assert "UNHANDLED EXCEPTION" in full_output or "oops" in full_output


def test_main_loop_init_failure(capsys, caplog):
    """main_loop returns early and prints an error when DarkNaMoSystem init fails."""
    with (
        patch("app.DarkNaMoSystem", side_effect=RuntimeError("init fail")),
        patch("builtins.input") as mock_input,
    ):
        from app import main_loop

        with pytest.raises(SystemExit) as excinfo:
            main_loop()
        assert excinfo.value.code == 1

    # input should never have been called since we returned early
    mock_input.assert_not_called()
    captured = capsys.readouterr()
    full_output = captured.out + captured.err + caplog.text
    assert "CRITICAL ERROR" in full_output or "init fail" in full_output
