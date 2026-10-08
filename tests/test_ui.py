from unittest.mock import patch
import sys
from comit.ui import select_arrow_menu, prompt_action, prompt_edit, prompt_settings_menu


def test_select_arrow_menu_non_tty(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    # Piped input "2"
    with patch("rich.prompt.Prompt.ask", return_value="2"):
        options = [("opt1", "Option One"), ("opt2", "Option Two")]
        res = select_arrow_menu(options, default_index=0)
        assert res == "opt2"


def test_select_arrow_menu_non_tty_q(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    with patch("rich.prompt.Prompt.ask", return_value="q"):
        options = [("view", "View"), ("exit", "Exit")]
        res = select_arrow_menu(options, default_index=0, allow_quit_key=True)
        assert res == "exit"


def test_select_arrow_menu_interactive_arrows(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    # Simulate keys: Down arrow, Enter
    key_sequence = ["down", "enter"]
    monkeypatch.setattr("comit.ui._read_key_event", lambda: key_sequence.pop(0))

    options = [("accept", "Accept"), ("edit", "Edit"), ("cancel", "Cancel")]
    res = select_arrow_menu(options, default_index=0)
    assert res == "edit"


def test_select_arrow_menu_interactive_shortcut(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    # Simulate key: 'r' for regenerate
    monkeypatch.setattr("comit.ui._read_key_event", lambda: "r")

    options = [("accept", "Accept"), ("edit", "Edit"), ("regenerate", "Regenerate"), ("cancel", "Cancel")]
    res = select_arrow_menu(options, default_index=0)
    assert res == "regenerate"


def test_select_arrow_menu_interactive_q(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    # Simulate key: 'q'
    monkeypatch.setattr("comit.ui._read_key_event", lambda: "q")

    options = [("view", "View"), ("exit", "Exit")]
    res = select_arrow_menu(options, default_index=0, allow_quit_key=True)
    assert res == "exit"


def test_prompt_edit_prepopulated(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    with patch("prompt_toolkit.prompt", return_value="feat: modified message") as mock_pt:
        res = prompt_edit("feat: original message")
        assert res == "feat: modified message"
        mock_pt.assert_called_once_with("> ", default="feat: original message")
