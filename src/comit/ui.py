from __future__ import annotations

from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

console = Console()
error_console = Console(stderr=True)


def show_step_success(message: str) -> None:
    console.print(f"[bold green]✓[/bold green] {message}")


def show_step_error(message: str) -> None:
    error_console.print(f"[bold red]✗[/bold red] {message}")


def show_not_git_repository() -> None:
    error_console.print("[bold red]✗[/bold red] Not a Git repository.")


def show_no_staged_changes() -> None:
    error_console.print("[bold red]✗[/bold red] No staged changes found.\n")
    error_console.print("Stage your changes first:")
    error_console.print("  [bold cyan]git add <files>[/bold cyan]\n")


def display_suggested_commit(message: str, title: str = "Suggested commit") -> None:
    console.print()
    content = Text(f"  {message}", style="bold white")
    panel = Panel(
        content,
        title=f"[bold cyan]{title}[/bold cyan]",
        title_align="left",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)
    console.print()


def prompt_action() -> str:
    console.print("[bold]What would you like to do?[/bold]\n")
    console.print("  [bold cyan]\\[a][/bold cyan] Accept")
    console.print("  [bold cyan]\\[e][/bold cyan] Edit")
    console.print("  [bold cyan]\\[r][/bold cyan] Regenerate")
    console.print("  [bold cyan]\\[c][/bold cyan] Cancel\n")

    while True:
        choice = Prompt.ask(
            "[bold]Select an option[/bold]",
            choices=["a", "e", "r", "c", "accept", "edit", "regenerate", "cancel"],
            default="a",
            show_choices=False,
            console=console,
        ).strip().lower()

        if choice in ("a", "accept"):
            return "a"
        if choice in ("e", "edit"):
            return "e"
        if choice in ("r", "regenerate"):
            return "r"
        if choice in ("c", "cancel"):
            return "c"


def prompt_edit(current_message: str) -> str:
    console.print("\n[bold cyan]Edit commit message[/bold cyan] (press Enter to keep or submit changes):")
    edited = Prompt.ask(
        "[bold]> [/bold]",
        default=current_message,
        console=console,
    ).strip()
    return edited if edited else current_message


def show_commit_success(message: str) -> None:
    console.print("\n[bold green]✓[/bold green] Commit created successfully\n")
    console.print(f"  [bold]{message}[/bold]\n")


def show_auto_commit_success(message: str) -> None:
    console.print(f"\n[bold green]✓[/bold green] Generated:\n\n  [bold]{message}[/bold]\n")
    console.print("[bold green]✓[/bold green] Commit created successfully\n")


def show_cancelled() -> None:
    console.print("\n[yellow]Cancelled. No commit was created.[/yellow]\n")


def show_error(message: str) -> None:
    error_console.print(f"[bold red]✗[/bold red] {message}")
