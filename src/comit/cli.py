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
)

app = typer.Typer(
    name="comit",
    help="Comit: AI-powered Git commit assistant.",
    add_completion=False,
    no_args_is_help=True,
)


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


if __name__ == "__main__":
    app()
