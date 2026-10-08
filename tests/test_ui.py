from unittest.mock import patch, MagicMock
import sys
from comit.ui import select_arrow_menu, prompt_action, prompt_edit, prompt_settings_menu


def test_select_arrow_menu_non_tty(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
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


def test_select_arrow_menu_interactive_app(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    with patch("comit.ui._run_prompt_toolkit_menu", return_value="edit"):
        options = [("accept", "Accept"), ("edit", "Edit"), ("cancel", "Cancel")]
        res = select_arrow_menu(options, default_index=0)
        assert res == "edit"


def test_select_arrow_menu_interactive_shortcut(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    with patch("comit.ui._run_prompt_toolkit_menu", return_value="regenerate"):
        options = [("accept", "Accept"), ("edit", "Edit"), ("regenerate", "Regenerate"), ("cancel", "Cancel")]
        res = select_arrow_menu(options, default_index=0)
        assert res == "regenerate"


def test_select_arrow_menu_interactive_q(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    with patch("comit.ui._run_prompt_toolkit_menu", return_value="exit"):
        options = [("view", "View"), ("exit", "Exit")]
        res = select_arrow_menu(options, default_index=0, allow_quit_key=True)
        assert res == "exit"


def test_prompt_edit_prepopulated(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    with patch("prompt_toolkit.prompt", return_value="feat: modified message") as mock_pt:
        res = prompt_edit("feat: original message")
        assert res == "feat: modified message"
        mock_pt.assert_called_once_with("> ", default="feat: original message")


def test_prompt_confirm_push():
    from comit.ui import prompt_confirm_push, show_push_success, show_push_skipped, show_no_remote, show_no_default_remote, show_push_error
    with patch("rich.prompt.Confirm.ask", return_value=True):
        assert prompt_confirm_push() is True

    with patch("rich.prompt.Confirm.ask", return_value=False):
        assert prompt_confirm_push() is False

    show_push_success("origin", "main")
    show_push_skipped()
    show_no_remote(explicit_push=False)
    show_no_remote(explicit_push=True)
    show_no_default_remote()
    show_push_error("Something failed")

