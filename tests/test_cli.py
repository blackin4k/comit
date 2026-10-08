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
@patch("comit.cli.prompt_action", return_value="c")
def test_cli_commit_interactive_cancel(mock_prompt, mock_gen, mock_recent, mock_diff, mock_is_git):
    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 0
    assert "Cancelled" in result.stdout
