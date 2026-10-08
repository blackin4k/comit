from __future__ import annotations

import sys
from typing import Optional
import typer
from rich.console import Console

from comit import __version__
from comit.ai import (
    ComitAIError,
    generate_commit_message,
)
from comit.config import (
    get_config_summary,
    get_model,
    set_user_config_value,
    reset_user_config,
)
from comit.git import (
    GitError,
    is_git_repository,
    get_staged_diff,
    get_recent_commits,
    create_commit,
)
from comit.ui import (
    console,
    show_step_success,
    show_not_git_repository,
    show_no_staged_changes,
    display_suggested_commit,
    prompt_action,
    prompt_edit,
    show_commit_success,
    show_auto_commit_success,
    show_cancelled,
    show_error,
    show_settings_summary,
    prompt_settings_menu,
    prompt_api_key,
    prompt_model,
    prompt_confirm_reset,
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
        console.print(f"Comit version [bold cyan]{__version__}[/bold cyan]")
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


@app.command(name="commit", help="Generate an AI-powered commit message for staged changes.")
def commit_command(
    yes: bool = typer.Option(
        False,
        "-y",
        "--yes",
        help="Automatically accept the generated commit message and create the commit.",
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
        with console.status("[cyan]Analyzing staged changes...[/cyan]", spinner="dots"):
            diff = get_staged_diff()

        if not diff:
            show_no_staged_changes()
            raise typer.Exit(code=1)

        show_step_success("Staged changes analyzed")
    except GitError as e:
        show_error(str(e))
        raise typer.Exit(code=1)

    try:
        with console.status("[cyan]Analyzing commit history...[/cyan]", spinner="dots"):
            recent_commits = get_recent_commits(count=15)
        show_step_success("Commit history analyzed")
    except GitError as e:
        show_error(str(e))
        raise typer.Exit(code=1)

    current_message = ""
    try:
        with console.status("[cyan]Generating commit message...[/cyan]", spinner="dots"):
            current_message = generate_commit_message(diff=diff, recent_commits=recent_commits)
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

        if action == "a":
            try:
                success, output = create_commit(current_message)
                if success:
                    show_commit_success(current_message)
                    return
                else:
                    show_error(f"Git commit failed:\n{output}")
                    raise typer.Exit(code=1)
            except GitError as e:
                show_error(f"Git commit error: {e}")
                raise typer.Exit(code=1)

        elif action == "e":
            current_message = prompt_edit(current_message)

        elif action == "r":
            try:
                with console.status("[cyan]Regenerating commit message...[/cyan]", spinner="dots"):
                    current_message = generate_commit_message(diff=diff, recent_commits=recent_commits)
            except ComitAIError as e:
                show_error(str(e))
            except Exception as e:
                show_error(f"Unexpected error during regeneration: {e}")

        elif action == "c":
            show_cancelled()
            return


def _run_interactive_settings() -> None:
    while True:
        choice = prompt_settings_menu()
        if choice == "1":
            show_settings_summary(get_config_summary())
        elif choice == "2":
            key = prompt_api_key()
            if key:
                set_user_config_value("groq_api_key", key)
                show_step_success("Groq API key saved.")
            else:
                show_error("API key cannot be empty.")
        elif choice == "3":
            current_model = get_model()
            new_model = prompt_model(current_model)
            if new_model:
                set_user_config_value("groq_model", new_model)
                show_step_success(f"Model set to {new_model}.")
        elif choice == "4":
            if prompt_confirm_reset():
                reset_user_config()
                show_step_success("User configuration reset.")
        elif choice == "5":
            break


@settings_app.callback(invoke_without_command=True)
def settings_callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        _run_interactive_settings()


@settings_app.command(name="show", help="Display current configuration.")
def settings_show():
    show_settings_summary(get_config_summary())


@settings_app.command(name="set-model", help="Configure default model.")
def settings_set_model(
    model: str = typer.Argument(..., help="Model name, e.g. qwen/qwen3.8-27b"),
):
    if not model.strip():
        show_error("Model name cannot be empty.")
        raise typer.Exit(code=1)
    set_user_config_value("groq_model", model.strip())
    show_step_success(f"Model set to {model.strip()}.")


@settings_app.command(name="set-key", help="Configure Groq API key.")
def settings_set_key(
    key: Optional[str] = typer.Option(None, "--key", "-k", help="Groq API key"),
):
    if not key:
        key = prompt_api_key()
    if not key or not key.strip():
        show_error("API key cannot be empty.")
        raise typer.Exit(code=1)
    set_user_config_value("groq_api_key", key.strip())
    show_step_success("Groq API key saved.")


@settings_app.command(name="reset", help="Reset user configuration.")
def settings_reset(
    yes: bool = typer.Option(False, "-y", "--yes", help="Confirm reset without prompt"),
):
    if yes or prompt_confirm_reset():
        reset_user_config()
        show_step_success("User configuration reset.")


if __name__ == "__main__":
    app()
