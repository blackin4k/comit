from __future__ import annotations

import sys
from typing import Optional, List
import typer
from rich.console import Console

from comit import __version__
from comit.ai import (
    ComitAIError,
    generate_commit_message,
)
from comit.config import (
    get_config_summary,
    get_provider,
    get_model,
    get_ollama_host,
    set_user_config_value,
    reset_user_config,
    normalize_api_key,
    SUPPORTED_PROVIDERS,
)
from comit.commit.context import CommitContext
from comit.git import (
    GitError,
    is_git_repository,
    get_staged_diff,
    get_recent_commits,
    get_repository_name,
    get_current_branch,
    get_staged_changed_files,
    get_diff_stat,
    get_commit_context,
    create_commit,
    get_remotes,
    get_default_remote,
    push_commit,
)
from comit.review import review_changes
from comit.ui import (
    console,
    show_step_success,
    show_not_git_repository,
    show_no_staged_changes,
    display_suggested_commit,
    display_review_result,
    prompt_action,
    prompt_edit,
    prompt_confirm_continue_commit,
    show_commit_success,
    show_auto_commit_success,
    show_cancelled,
    show_error,
    show_settings_summary,
    prompt_settings_menu,
    prompt_provider_selection,
    prompt_api_key,
    prompt_model,
    prompt_ollama_host,
    prompt_confirm_reset,
    prompt_confirm_push,
    show_push_success,
    show_push_skipped,
    show_no_remote,
    show_no_default_remote,
    show_push_error,
)

app = typer.Typer(
    name="comit",
    help="Comit: AI-powered Git commit assistant.",
    add_completion=False,
    no_args_is_help=True,
)

settings_app = typer.Typer(
    name="settings",
    help="View and configure Comit settings.",
    invoke_without_command=True,
    no_args_is_help=False,
)
app.add_typer(settings_app, name="settings")


def version_callback(value: bool):
    if value:
        console.print(f"Comit version {__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
):
    pass


def _perform_push(explicit_push: bool) -> None:
    try:
        remotes = get_remotes()
    except GitError as e:
        show_push_error(str(e))
        return

    if not remotes:
        show_no_remote(explicit_push=explicit_push)
        return

    remote = get_default_remote()
    if not remote:
        show_no_default_remote()
        return

    try:
        branch = get_current_branch()
    except GitError as e:
        show_push_error(str(e))
        return

    if not branch:
        show_push_error("Could not determine current branch (detached HEAD).")
        return

    if not explicit_push:
        try:
            should_push = prompt_confirm_push()
        except Exception:
            should_push = False
        if not should_push:
            show_push_skipped()
            return

    try:
        success, output = push_commit(remote, branch)
        if success:
            show_push_success(remote, branch)
        else:
            show_push_error(output)
    except GitError as e:
        show_push_error(str(e))
    except Exception as e:
        show_push_error(f"Unexpected error during push: {e}")


@app.command(name="commit", help="Generate an AI-powered commit message for staged changes.")
def commit_command(
    yes: bool = typer.Option(
        False,
        "-y",
        "--yes",
        help="Automatically accept the generated commit message without confirmation.",
    ),
    push: bool = typer.Option(
        False,
        "--push",
        help="Push the resulting commit to the remote after creation.",
    ),
):
    try:
        if not is_git_repository():
            show_not_git_repository()
            raise typer.Exit(code=1)
    except GitError as e:
        show_error(str(e))
        raise typer.Exit(code=1)

    try:
        diff = get_staged_diff()
        if not diff:
            show_no_staged_changes()
            raise typer.Exit(code=1)
    except GitError as e:
        show_error(str(e))
        raise typer.Exit(code=1)

    try:
        recent_commits = get_recent_commits(count=15)
        repo_name = get_repository_name()
        branch = get_current_branch() or "HEAD"
        changed_files = get_staged_changed_files()
        diff_stat = get_diff_stat()
    except GitError as e:
        show_error(str(e))
        raise typer.Exit(code=1)

    context = CommitContext(
        repository_name=repo_name,
        current_branch=branch,
        changed_files=changed_files,
        recent_commits=recent_commits,
        diff_stat=diff_stat,
        staged_diff=diff,
    )

    review_result = review_changes(context)
    if review_result.has_findings:
        display_review_result(review_result)
        should_continue = prompt_confirm_continue_commit()
        if not should_continue:
            show_cancelled()
            return
    else:
        console.print("No issues detected.\n")

    current_message = ""
    seen_messages: List[str] = []

    try:
        current_message = generate_commit_message(context=context)
        seen_messages.append(current_message)
    except ComitAIError as e:
        show_error(str(e))
        raise typer.Exit(code=1)
    except Exception as e:
        show_error(f"Unexpected error during generation: {e}")
        raise typer.Exit(code=1)

    if yes:
        try:
            success, output = create_commit(current_message)
            if success:
                show_auto_commit_success(current_message)
                if push:
                    _perform_push(explicit_push=True)
            else:
                show_error(f"Git commit failed:\n{output}")
                raise typer.Exit(code=1)
        except GitError as e:
            show_error(f"Git commit error: {e}")
            raise typer.Exit(code=1)
        return

    while True:
        display_suggested_commit(current_message)
        action = prompt_action()

        if action in ("accept", "a"):
            try:
                success, output = create_commit(current_message)
                if success:
                    show_commit_success(current_message)
                    _perform_push(explicit_push=push)
                    return
                else:
                    show_error(f"Git commit failed:\n{output}")
                    raise typer.Exit(code=1)
            except GitError as e:
                show_error(f"Git commit error: {e}")
                raise typer.Exit(code=1)

        elif action in ("edit", "e"):
            edited = prompt_edit(current_message)
            if edited:
                current_message = edited

        elif action in ("regenerate", "r"):
            try:
                current_message = generate_commit_message(
                    context=context,
                    avoid_messages=seen_messages,
                )
                seen_messages.append(current_message)
            except ComitAIError as e:
                show_error(str(e))
            except Exception as e:
                show_error(f"Unexpected error during regeneration: {e}")

        elif action in ("cancel", "c", "exit"):
            show_cancelled()
            return


@app.command(name="review", help="Analyze staged changes for potential security and safety issues.")
def review_command():
    try:
        if not is_git_repository():
            show_not_git_repository()
            raise typer.Exit(code=1)
    except GitError as e:
        show_error(str(e))
        raise typer.Exit(code=1)

    try:
        context = get_commit_context()
        if not context.changed_files and not context.staged_diff:
            show_no_staged_changes()
            raise typer.Exit(code=1)
    except GitError as e:
        show_error(str(e))
        raise typer.Exit(code=1)

    result = review_changes(context)
    display_review_result(result)


def _run_interactive_settings() -> None:
    while True:
        current_p = get_provider()
        choice = prompt_settings_menu(provider=current_p)
        if choice == "view":
            show_settings_summary(get_config_summary())
        elif choice == "set_provider":
            new_provider = prompt_provider_selection(current_provider=current_p)
            if new_provider in SUPPORTED_PROVIDERS:
                set_user_config_value("provider", new_provider)
                show_step_success(f"AI provider set to {new_provider}.")
        elif choice == "set_key":
            if current_p == "ollama":
                current_host = get_ollama_host()
                new_host = prompt_ollama_host(current_host)
                if new_host:
                    set_user_config_value("ollama_host", new_host)
                    show_step_success(f"Ollama host set to {new_host}.")
            else:
                key = prompt_api_key(provider=current_p)
                norm_key = normalize_api_key(key)
                if norm_key:
                    set_user_config_value(f"{current_p}_api_key", norm_key)
                    if current_p == "groq":
                        set_user_config_value("groq_api_key", norm_key)
                    show_step_success(f"{current_p.capitalize()} API key saved.")
                else:
                    show_error("API key cannot be empty.")
        elif choice == "set_model":
            current_model = get_model(provider=current_p)
            new_model = prompt_model(current_model, provider=current_p)
            if new_model:
                set_user_config_value(f"{current_p}_model", new_model)
                if current_p == "groq":
                    set_user_config_value("groq_model", new_model)
                show_step_success(f"{current_p.capitalize()} model set to {new_model}.")
        elif choice == "reset":
            if prompt_confirm_reset():
                reset_user_config()
                show_step_success("User configuration reset.")
        elif choice in ("exit", "cancel", "q"):
            break


@settings_app.callback(invoke_without_command=True)
def settings_callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        _run_interactive_settings()


@settings_app.command(name="show", help="Display current configuration.")
def settings_show():
    show_settings_summary(get_config_summary())


@settings_app.command(name="set-provider", help="Configure default AI provider.")
def settings_set_provider(
    provider: str = typer.Argument(..., help="Provider name (groq, gemini, openai, ollama)"),
):
    p = provider.strip().lower()
    if p not in SUPPORTED_PROVIDERS:
        show_error(f"Unsupported provider '{p}'. Supported providers: {', '.join(SUPPORTED_PROVIDERS)}")
        raise typer.Exit(code=1)
    set_user_config_value("provider", p)
    show_step_success(f"AI provider set to {p}.")


@settings_app.command(name="set-model", help="Configure default model for a provider.")
def settings_set_model(
    model: str = typer.Argument(..., help="Model name"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Target provider (defaults to active provider)"),
):
    if not model.strip():
        show_error("Model name cannot be empty.")
        raise typer.Exit(code=1)
    p = (provider or get_provider()).strip().lower()
    if p not in SUPPORTED_PROVIDERS:
        show_error(f"Unsupported provider '{p}'. Supported providers: {', '.join(SUPPORTED_PROVIDERS)}")
        raise typer.Exit(code=1)
    set_user_config_value(f"{p}_model", model.strip())
    if p == "groq":
        set_user_config_value("groq_model", model.strip())
    show_step_success(f"{p.capitalize()} model set to {model.strip()}.")


@settings_app.command(name="set-key", help="Configure API key for a provider.")
def settings_set_key(
    key: Optional[str] = typer.Option(None, "--key", "-k", help="API key"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Target provider (defaults to active provider)"),
):
    p = (provider or get_provider()).strip().lower()
    if p == "ollama":
        show_error("Ollama runs locally and does not use an API key. Use 'set-host' to configure the host.")
        raise typer.Exit(code=1)
    if p not in SUPPORTED_PROVIDERS:
        show_error(f"Unsupported provider '{p}'. Supported providers: {', '.join(SUPPORTED_PROVIDERS)}")
        raise typer.Exit(code=1)
    if not key:
        key = prompt_api_key(provider=p)
    norm_key = normalize_api_key(key)
    if not norm_key:
        show_error("API key cannot be empty.")
        raise typer.Exit(code=1)
    set_user_config_value(f"{p}_api_key", norm_key)
    if p == "groq":
        set_user_config_value("groq_api_key", norm_key)
    show_step_success(f"{p.capitalize()} API key saved.")


@settings_app.command(name="set-host", help="Configure host URL for Ollama.")
def settings_set_host(
    host: str = typer.Argument(..., help="Ollama host URL, e.g. http://localhost:11434"),
):
    if not host.strip():
        show_error("Host cannot be empty.")
        raise typer.Exit(code=1)
    set_user_config_value("ollama_host", host.strip())
    show_step_success(f"Ollama host set to {host.strip()}.")


@settings_app.command(name="reset", help="Reset user configuration.")
def settings_reset(
    yes: bool = typer.Option(False, "-y", "--yes", help="Confirm reset without prompt"),
):
    if yes or prompt_confirm_reset():
        reset_user_config()
        show_step_success("User configuration reset.")


if __name__ == "__main__":
    app()
