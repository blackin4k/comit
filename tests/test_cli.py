from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
import pytest

from comit.cli import app

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "Comit version" in result.stdout


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Comit" in result.stdout
    assert "commit" in result.stdout
    assert "settings" in result.stdout


@patch("comit.cli.is_git_repository", return_value=False)
def test_cli_commit_not_git_repo(mock_is_git):
    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 1
    assert "Not a Git repository" in result.stderr or "Not a Git repository" in result.stdout


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="")
def test_cli_commit_no_staged_changes(mock_diff, mock_is_git):
    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 1
    assert "No staged changes found" in result.stderr or "No staged changes found" in result.stdout


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/app.py b/app.py\n+x = 1")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message", return_value="feat: add x variable")
@patch("comit.cli.create_commit", return_value=(True, "[main 123456] feat: add x variable"))
def test_cli_commit_yes_flag(mock_create, mock_gen, mock_recent, mock_diff, mock_is_git):
    result = runner.invoke(app, ["commit", "-y"])
    assert result.exit_code == 0
    assert "feat: add x variable" in result.stdout
    assert "Commit created successfully" in result.stdout
    mock_create.assert_called_once_with("feat: add x variable")


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/app.py b/app.py\n+x = 1")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message", return_value="feat: add x variable")
@patch("comit.cli.prompt_action", return_value="cancel")
def test_cli_commit_interactive_cancel(mock_prompt, mock_gen, mock_recent, mock_diff, mock_is_git):
    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 0
    assert "Cancelled" in result.stdout


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/app.py b/app.py\n+x = 1")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message", return_value="feat: initial generated message")
@patch("comit.cli.prompt_action", side_effect=["edit", "accept"])
@patch("comit.cli.prompt_edit", return_value="feat: manually edited message")
@patch("comit.cli.create_commit", return_value=(True, "[main 123456] feat: manually edited message"))
def test_cli_commit_edit_flow(mock_create, mock_edit, mock_prompt, mock_gen, mock_recent, mock_diff, mock_is_git):
    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 0
    mock_edit.assert_called_once_with("feat: initial generated message")
    mock_create.assert_called_once_with("feat: manually edited message")
    assert "Commit created successfully" in result.stdout


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/app.py b/app.py\n+x = 1")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message", side_effect=["feat: message 1", "feat: alternative message 2"])
@patch("comit.cli.prompt_action", side_effect=["regenerate", "accept"])
@patch("comit.cli.create_commit", return_value=(True, "[main 123456] feat: alternative message 2"))
def test_cli_commit_regenerate_flow(mock_create, mock_prompt, mock_gen, mock_recent, mock_diff, mock_is_git):
    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 0
    assert mock_gen.call_count == 2
    mock_create.assert_called_once_with("feat: alternative message 2")
    assert "Commit created successfully" in result.stdout


def test_cli_settings_show(tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    result = runner.invoke(app, ["settings", "show"])
    assert result.exit_code == 0
    assert "Comit Configuration" in result.stdout
    assert "AI Provider:" in result.stdout


def test_cli_settings_set_model(tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    result = runner.invoke(app, ["settings", "set-model", "test-llama-model"])
    assert result.exit_code == 0
    assert "Model set to test-llama-model" in result.stdout

    from comit.config import get_model
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    monkeypatch.delenv("groq_model", raising=False)
    assert get_model() == "test-llama-model"


def test_cli_settings_set_key(tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    result = runner.invoke(app, ["settings", "set-key", "--key", "gsk_custom_1234567890"])
    assert result.exit_code == 0
    assert "Groq API key saved" in result.stdout

    from comit.config import get_api_key
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("groq_api_key", raising=False)
    monkeypatch.delenv("Groq_Api_Key", raising=False)
    monkeypatch.delenv("GROQ_KEY", raising=False)
    assert get_api_key() == "gsk_custom_1234567890"


def test_cli_settings_reset(tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    from comit.config import set_user_config_value, load_user_config
    set_user_config_value("groq_model", "custom")

    result = runner.invoke(app, ["settings", "reset", "--yes"])
    assert result.exit_code == 0
    assert "User configuration reset" in result.stdout
    assert load_user_config() == {}


def test_cli_settings_interactive_exit(tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    result = runner.invoke(app, ["settings"], input="5\n")
    assert result.exit_code == 0
    assert "Settings Menu" in result.stdout


def test_cli_settings_interactive_q_exit(tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    result = runner.invoke(app, ["settings"], input="q\n")
    assert result.exit_code == 0
    assert "Settings Menu" in result.stdout


def test_cli_settings_set_key_double_quoted(tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    result = runner.invoke(app, ["settings", "set-key", "--key", '"gsk_quoted_1234567890"'])
    assert result.exit_code == 0
    assert "Groq API key saved" in result.stdout

    from comit.config import get_api_key, load_user_config
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("groq_api_key", raising=False)
    monkeypatch.delenv("Groq_Api_Key", raising=False)
    monkeypatch.delenv("GROQ_KEY", raising=False)
    assert load_user_config()["groq_api_key"] == "gsk_quoted_1234567890"
    assert get_api_key() == "gsk_quoted_1234567890"


def test_cli_settings_set_key_single_quoted(tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    result = runner.invoke(app, ["settings", "set-key", "--key", "  'gsk_single_1234567890'  "])
    assert result.exit_code == 0
    assert "Groq API key saved" in result.stdout

    from comit.config import get_api_key, load_user_config
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("groq_api_key", raising=False)
    monkeypatch.delenv("Groq_Api_Key", raising=False)
    monkeypatch.delenv("GROQ_KEY", raising=False)
    assert load_user_config()["groq_api_key"] == "gsk_single_1234567890"
    assert get_api_key() == "gsk_single_1234567890"


@patch("comit.cli.prompt_settings_menu", side_effect=["set_key", "exit"])
@patch("comit.cli.prompt_api_key", return_value='  "gsk_interactive_1234567890"  ')
def test_cli_settings_interactive_set_key_normalization(mock_prompt_key, mock_prompt_menu, tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    result = runner.invoke(app, ["settings"])
    assert result.exit_code == 0
    assert "Groq API key saved" in result.stdout

    from comit.config import get_api_key, load_user_config
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("groq_api_key", raising=False)
    monkeypatch.delenv("Groq_Api_Key", raising=False)
    monkeypatch.delenv("GROQ_KEY", raising=False)
    assert load_user_config()["groq_api_key"] == "gsk_interactive_1234567890"
    assert get_api_key() == "gsk_interactive_1234567890"

