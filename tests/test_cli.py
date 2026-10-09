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
    assert "model set to test-llama-model" in result.stdout.lower()

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
    result = runner.invoke(app, ["settings"], input="6\n")
    assert result.exit_code == 0
    assert "Settings Menu" in result.stdout


def test_cli_settings_interactive_q_exit(tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    result = runner.invoke(app, ["settings"], input="q\n")
    assert result.exit_code == 0
    assert "Settings Menu" in result.stdout


def test_cli_settings_set_provider(tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    result = runner.invoke(app, ["settings", "set-provider", "gemini"])
    assert result.exit_code == 0
    assert "AI provider set to gemini" in result.stdout

    from comit.config import get_provider
    monkeypatch.delenv("COMIT_PROVIDER", raising=False)
    assert get_provider() == "gemini"


def test_cli_settings_set_provider_unsupported(tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    result = runner.invoke(app, ["settings", "set-provider", "unknown_provider"])
    assert result.exit_code == 1
    assert "Unsupported provider" in result.stderr or "Unsupported provider" in result.stdout


def test_cli_settings_set_host(tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    result = runner.invoke(app, ["settings", "set-host", "http://127.0.0.1:11434"])
    assert result.exit_code == 0
    assert "Ollama host set to http://127.0.0.1:11434" in result.stdout

    from comit.config import get_ollama_host
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    assert get_ollama_host() == "http://127.0.0.1:11434"


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
    assert get_api_key(provider="groq") == "gsk_quoted_1234567890"


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
    assert get_api_key(provider="groq") == "gsk_single_1234567890"


def test_cli_settings_set_key_gemini(tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    result = runner.invoke(app, ["settings", "set-key", "--provider", "gemini", "--key", "AIzaSy_custom_key"])
    assert result.exit_code == 0
    assert "Gemini API key saved" in result.stdout

    from comit.config import get_api_key, load_user_config
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert load_user_config()["gemini_api_key"] == "AIzaSy_custom_key"
    assert get_api_key(provider="gemini") == "AIzaSy_custom_key"


def test_cli_settings_set_key_ollama_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    result = runner.invoke(app, ["settings", "set-key", "--provider", "ollama", "--key", "any_key"])
    assert result.exit_code == 1
    assert "Ollama runs locally" in result.stderr or "Ollama runs locally" in result.stdout


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
    assert get_api_key(provider="groq") == "gsk_interactive_1234567890"


@patch("comit.cli.prompt_settings_menu", side_effect=["set_provider", "exit"])
@patch("comit.cli.prompt_provider_selection", return_value="openai")
def test_cli_settings_interactive_set_provider(mock_select_p, mock_menu, tmp_path, monkeypatch):
    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)
    result = runner.invoke(app, ["settings"])
    assert result.exit_code == 0
    assert "AI provider set to openai" in result.stdout

    from comit.config import get_provider
    monkeypatch.delenv("COMIT_PROVIDER", raising=False)
    assert get_provider() == "openai"



@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/app.py b/app.py\n+x = 1")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message", return_value="feat: add x")
@patch("comit.cli.create_commit", return_value=(True, "[main 123456] feat: add x"))
@patch("comit.cli.get_remotes", return_value=["origin"])
@patch("comit.cli.get_default_remote", return_value="origin")
@patch("comit.cli.get_current_branch", return_value="main")
@patch("comit.cli.prompt_action", return_value="accept")
@patch("comit.cli.prompt_confirm_push", return_value=True)
@patch("comit.cli.push_commit", return_value=(True, "Pushed to origin/main"))
def test_cli_commit_interactive_push_yes(mock_push, mock_confirm, mock_prompt, mock_branch, mock_remote, mock_remotes, mock_create, mock_gen, mock_recent, mock_diff, mock_is_git):
    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 0
    assert "Commit created successfully" in result.stdout
    assert "Pushed to origin/main" in result.stdout
    mock_push.assert_called_once_with("origin", "main")


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/app.py b/app.py\n+x = 1")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message", return_value="feat: add x")
@patch("comit.cli.create_commit", return_value=(True, "[main 123456] feat: add x"))
@patch("comit.cli.get_remotes", return_value=["origin"])
@patch("comit.cli.get_default_remote", return_value="origin")
@patch("comit.cli.get_current_branch", return_value="main")
@patch("comit.cli.prompt_action", return_value="accept")
@patch("comit.cli.prompt_confirm_push", return_value=False)
@patch("comit.cli.push_commit")
def test_cli_commit_interactive_push_no(mock_push, mock_confirm, mock_prompt, mock_branch, mock_remote, mock_remotes, mock_create, mock_gen, mock_recent, mock_diff, mock_is_git):
    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 0
    assert "Commit created successfully" in result.stdout
    assert "Nothing was pushed" in result.stdout
    mock_push.assert_not_called()


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/app.py b/app.py\n+x = 1")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message", return_value="feat: add x")
@patch("comit.cli.create_commit", return_value=(True, "[main 123456] feat: add x"))
@patch("comit.cli.get_remotes", return_value=["origin"])
@patch("comit.cli.get_default_remote", return_value="origin")
@patch("comit.cli.get_current_branch", return_value="main")
@patch("comit.cli.prompt_action", return_value="accept")
@patch("comit.cli.prompt_confirm_push")
@patch("comit.cli.push_commit", return_value=(True, "Pushed to origin/main"))
def test_cli_commit_explicit_push_flag(mock_push, mock_confirm, mock_prompt, mock_branch, mock_remote, mock_remotes, mock_create, mock_gen, mock_recent, mock_diff, mock_is_git):
    result = runner.invoke(app, ["commit", "--push"])
    assert result.exit_code == 0
    assert "Commit created successfully" in result.stdout
    assert "Pushed to origin/main" in result.stdout
    mock_confirm.assert_not_called()
    mock_push.assert_called_once_with("origin", "main")


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/app.py b/app.py\n+x = 1")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message", return_value="feat: add x")
@patch("comit.cli.create_commit", return_value=(True, "[main 123456] feat: add x"))
@patch("comit.cli.get_remotes", return_value=["origin"])
@patch("comit.cli.get_default_remote", return_value="origin")
@patch("comit.cli.get_current_branch", return_value="main")
@patch("comit.cli.push_commit", return_value=(True, "Pushed to origin/main"))
def test_cli_commit_yes_with_push(mock_push, mock_branch, mock_remote, mock_remotes, mock_create, mock_gen, mock_recent, mock_diff, mock_is_git):
    result = runner.invoke(app, ["commit", "-y", "--push"])
    assert result.exit_code == 0
    assert "Commit created successfully" in result.stdout
    assert "Pushed to origin/main" in result.stdout
    mock_push.assert_called_once_with("origin", "main")


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/app.py b/app.py\n+x = 1")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message", return_value="feat: add x")
@patch("comit.cli.create_commit", return_value=(True, "[main 123456] feat: add x"))
@patch("comit.cli.get_remotes", return_value=[])
@patch("comit.cli.prompt_action", return_value="accept")
def test_cli_commit_push_no_remotes(mock_prompt, mock_remotes, mock_create, mock_gen, mock_recent, mock_diff, mock_is_git):
    result = runner.invoke(app, ["commit", "--push"])
    assert result.exit_code == 0
    assert "No Git remote is configured" in result.stdout


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/app.py b/app.py\n+x = 1")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message", return_value="feat: add x")
@patch("comit.cli.create_commit", return_value=(True, "[main 123456] feat: add x"))
@patch("comit.cli.get_remotes", return_value=["backup", "upstream"])
@patch("comit.cli.get_default_remote", return_value=None)
@patch("comit.cli.prompt_action", return_value="accept")
def test_cli_commit_push_multiple_remotes_no_origin(mock_prompt, mock_remote, mock_remotes, mock_create, mock_gen, mock_recent, mock_diff, mock_is_git):
    result = runner.invoke(app, ["commit", "--push"])
    assert result.exit_code == 0
    assert "No default push remote ('origin') found" in result.stdout


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/app.py b/app.py\n+x = 1")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message", return_value="feat: add x")
@patch("comit.cli.create_commit", return_value=(True, "[main 123456] feat: add x"))
@patch("comit.cli.get_remotes", return_value=["origin"])
@patch("comit.cli.get_default_remote", return_value="origin")
@patch("comit.cli.get_current_branch", return_value="main")
@patch("comit.cli.prompt_action", return_value="accept")
@patch("comit.cli.push_commit", return_value=(False, "The remote rejected the push because the branch is behind the remote."))
def test_cli_commit_push_failure_rejection(mock_push, mock_prompt, mock_branch, mock_remote, mock_remotes, mock_create, mock_gen, mock_recent, mock_diff, mock_is_git):
    result = runner.invoke(app, ["commit", "--push"])
    assert result.exit_code == 0
    assert "Push failed" in result.stderr or "Push failed" in result.stdout
    assert "behind the remote" in result.stderr or "behind the remote" in result.stdout
    assert "Your commit was created locally and was not lost" in result.stdout


@patch("comit.cli.is_git_repository", return_value=False)
def test_cli_review_not_git_repo(mock_is_git):
    result = runner.invoke(app, ["review"])
    assert result.exit_code == 1
    assert "Not a Git repository" in result.stderr or "Not a Git repository" in result.stdout


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_commit_context")
def test_cli_review_no_staged_changes(mock_get_ctx, mock_is_git):
    from comit.commit.context import CommitContext
    mock_get_ctx.return_value = CommitContext(repository_name="test", current_branch="main", changed_files=[], staged_diff="")
    result = runner.invoke(app, ["review"])
    assert result.exit_code == 1
    assert "No staged changes found" in result.stderr or "No staged changes found" in result.stdout


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_commit_context")
def test_cli_review_clean_staged_changes(mock_get_ctx, mock_is_git):
    from comit.commit.context import CommitContext, ChangedFile, DiffStat
    mock_get_ctx.return_value = CommitContext(
        repository_name="test",
        current_branch="main",
        changed_files=[ChangedFile(path="src/main.py", status="M")],
        diff_stat=DiffStat(files_changed=1, insertions=5, deletions=1),
        staged_diff="diff --git a/src/main.py b/src/main.py\n+def run(): pass",
    )
    result = runner.invoke(app, ["review"])
    assert result.exit_code == 0
    assert "No issues detected" in result.stdout


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_commit_context")
def test_cli_review_with_findings(mock_get_ctx, mock_is_git):
    from comit.commit.context import CommitContext, ChangedFile, DiffStat
    mock_get_ctx.return_value = CommitContext(
        repository_name="test",
        current_branch="main",
        changed_files=[
            ChangedFile(path=".env", status="A"),
            ChangedFile(path="keys.py", status="A"),
        ],
        diff_stat=DiffStat(files_changed=2, insertions=10, deletions=0),
        staged_diff="diff --git a/keys.py b/keys.py\n+openai_key = 'sk-proj-12345678901234567890abcdef'",
    )
    result = runner.invoke(app, ["review"])
    assert result.exit_code == 0
    assert "Review findings" in result.stdout
    assert "HIGH" in result.stdout
    assert "WARNING" in result.stdout
    assert ".env" in result.stdout


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/app.py b/app.py\n+x = 1")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message", return_value="feat: add x")
@patch("comit.cli.create_commit", return_value=(True, "[main 123456] feat: add x"))
@patch("comit.cli.prompt_action", return_value="accept")
def test_cli_commit_with_clean_review(mock_prompt, mock_create, mock_gen, mock_recent, mock_diff, mock_is_git):
    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 0
    assert "No issues detected" in result.stdout
    assert "Commit created successfully" in result.stdout
    mock_gen.assert_called_once()
    mock_create.assert_called_once_with("feat: add x")


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/.env b/.env\n+SECRET=xyz")
@patch("comit.cli.get_staged_changed_files")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message")
@patch("comit.cli.create_commit")
@patch("comit.cli.prompt_confirm_continue_commit", return_value=False)
def test_cli_commit_with_review_findings_declined(mock_confirm, mock_create, mock_gen, mock_recent, mock_files, mock_diff, mock_is_git):
    from comit.commit.context import ChangedFile
    mock_files.return_value = [ChangedFile(path=".env", status="A")]

    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 0
    assert "Review findings" in result.stdout
    assert "WARNING" in result.stdout
    assert "Cancelled" in result.stdout
    mock_confirm.assert_called_once()
    mock_gen.assert_not_called()
    mock_create.assert_not_called()


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/.env b/.env\n+SECRET=xyz")
@patch("comit.cli.get_staged_changed_files")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message", return_value="feat: add env file")
@patch("comit.cli.create_commit", return_value=(True, "[main 123456] feat: add env file"))
@patch("comit.cli.prompt_confirm_continue_commit", return_value=True)
@patch("comit.cli.prompt_action", return_value="accept")
def test_cli_commit_with_review_findings_accepted(mock_prompt, mock_confirm, mock_create, mock_gen, mock_recent, mock_files, mock_diff, mock_is_git):
    from comit.commit.context import ChangedFile
    mock_files.return_value = [ChangedFile(path=".env", status="A")]

    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 0
    assert "Review findings" in result.stdout
    assert "WARNING" in result.stdout
    assert "Commit created successfully" in result.stdout
    mock_confirm.assert_called_once()
    mock_gen.assert_called_once()
    mock_create.assert_called_once_with("feat: add env file")


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/.env b/.env\n+SECRET=xyz")
@patch("comit.cli.get_staged_changed_files")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message")
@patch("comit.cli.create_commit")
@patch("comit.cli.prompt_confirm_continue_commit", return_value=False)
def test_cli_commit_yes_with_review_findings_declined(mock_confirm, mock_create, mock_gen, mock_recent, mock_files, mock_diff, mock_is_git):
    from comit.commit.context import ChangedFile
    mock_files.return_value = [ChangedFile(path=".env", status="A")]

    result = runner.invoke(app, ["commit", "-y"])
    assert result.exit_code == 0
    assert "Review findings" in result.stdout
    assert "WARNING" in result.stdout
    assert "Cancelled" in result.stdout
    mock_confirm.assert_called_once()
    mock_gen.assert_not_called()
    mock_create.assert_not_called()


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/.env b/.env\n+SECRET=xyz")
@patch("comit.cli.get_staged_changed_files")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message", return_value="feat: add env file")
@patch("comit.cli.create_commit", return_value=(True, "[main 123456] feat: add env file"))
@patch("comit.cli.prompt_confirm_continue_commit", return_value=True)
def test_cli_commit_yes_with_review_findings_accepted(mock_confirm, mock_create, mock_gen, mock_recent, mock_files, mock_diff, mock_is_git):
    from comit.commit.context import ChangedFile
    mock_files.return_value = [ChangedFile(path=".env", status="A")]

    result = runner.invoke(app, ["commit", "-y"])
    assert result.exit_code == 0
    assert "Review findings" in result.stdout
    assert "Commit created successfully" in result.stdout
    mock_confirm.assert_called_once()
    mock_gen.assert_called_once()
    mock_create.assert_called_once_with("feat: add env file")


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/.env b/.env\n+SECRET=xyz")
@patch("comit.cli.get_staged_changed_files")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message")
@patch("comit.cli.create_commit")
@patch("comit.cli.push_commit")
@patch("comit.cli.prompt_confirm_continue_commit", return_value=False)
def test_cli_commit_push_with_review_findings_declined(mock_confirm, mock_push, mock_create, mock_gen, mock_recent, mock_files, mock_diff, mock_is_git):
    from comit.commit.context import ChangedFile
    mock_files.return_value = [ChangedFile(path=".env", status="A")]

    result = runner.invoke(app, ["commit", "--push"])
    assert result.exit_code == 0
    assert "Cancelled" in result.stdout
    mock_gen.assert_not_called()
    mock_create.assert_not_called()
    mock_push.assert_not_called()


@patch("comit.cli.is_git_repository", return_value=True)
@patch("comit.cli.get_staged_diff", return_value="diff --git a/app.py b/app.py\n+x = 1")
@patch("comit.cli.get_recent_commits", return_value=["feat: initial"])
@patch("comit.cli.generate_commit_message", return_value="feat: initial generated message")
@patch("comit.cli.prompt_action", side_effect=["edit", "accept"])
@patch("comit.cli.prompt_edit", return_value=None)
@patch("comit.cli.create_commit", return_value=(True, "[main 123456] feat: initial generated message"))
def test_cli_commit_edit_cancel_flow(mock_create, mock_edit, mock_prompt, mock_gen, mock_recent, mock_diff, mock_is_git):
    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 0
    mock_edit.assert_called_once_with("feat: initial generated message")
    mock_create.assert_called_once_with("feat: initial generated message")
    assert "Commit created successfully" in result.stdout


