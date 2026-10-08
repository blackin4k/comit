from __future__ import annotations

import os
import sys
from typing import Optional, Dict, Any, List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
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


def _read_key_event() -> str:
    if sys.platform == "win32":
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            ch2 = msvcrt.getwch()
            if ch2 == "H":
                return "up"
            elif ch2 == "P":
                return "down"
            elif ch2 == "K":
                return "left"
            elif ch2 == "M":
                return "right"
            return "special"
        elif ch in ("\r", "\n"):
            return "enter"
        elif ch == "\x03":
            raise KeyboardInterrupt
        return ch
    else:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                ch2 = sys.stdin.read(1)
                if ch2 == "[":
                    ch3 = sys.stdin.read(1)
                    if ch3 == "A":
                        return "up"
                    elif ch3 == "B":
                        return "down"
                return "escape"
            elif ch in ("\r", "\n"):
                return "enter"
            elif ch == "\x03":
                raise KeyboardInterrupt
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def select_arrow_menu(
    options: List[Tuple[str, str]],
    prompt_text: str = "What would you like to do?",
    default_index: int = 0,
    allow_quit_key: bool = True,
) -> str:
    if not sys.stdin.isatty():
        console.print(f"[bold]{prompt_text}[/bold]\n")
        for idx, (opt_id, opt_label) in enumerate(options, start=1):
            console.print(f"  [bold cyan]{opt_id}[/bold cyan] - {opt_label}")
        choices = [opt_id for opt_id, _ in options]
        if allow_quit_key:
            choices.extend(["q", "quit"])
        choice = Prompt.ask(
            "\n[bold]Select an option[/bold]",
            default=options[default_index][0],
            console=console,
        ).strip().lower()
        if allow_quit_key and choice in ("q", "quit"):
            return "cancel" if "cancel" in [o[0] for o in options] else "exit"
        for opt_id, opt_label in options:
            if choice in (opt_id.lower(), opt_label.lower(), str(options.index((opt_id, opt_label)) + 1)):
                return opt_id
        return options[default_index][0]

    selected = default_index
    num_options = len(options)

    console.print(f"[bold]{prompt_text}[/bold]\n")

    def render_lines():
        for i, (_, label) in enumerate(options):
            if i == selected:
                console.print(f"  [bold cyan]❯ {label}[/bold cyan]")
            else:
                console.print(f"    {label}")

    render_lines()

    while True:
        try:
            key = _read_key_event()
        except KeyboardInterrupt:
            console.print()
            return "cancel" if "cancel" in [o[0] for o in options] else "exit"

        if key == "up":
            selected = (selected - 1) % num_options
        elif key == "down":
            selected = (selected + 1) % num_options
        elif key == "enter":
            console.print(f"\n[dim]Selected: {options[selected][1]}[/dim]\n")
            return options[selected][0]
        elif allow_quit_key and key.lower() == "q":
            console.print("\n[dim]Selected: Exit[/dim]\n")
            return "cancel" if "cancel" in [o[0] for o in options] else "exit"
        else:
            for i, (opt_id, opt_label) in enumerate(options):
                if key.lower() in (opt_id.lower()[:1], str(i + 1)):
                    selected = i
                    console.print(f"\x1b[{num_options}A\r", end="")
                    render_lines()
                    console.print(f"\n[dim]Selected: {opt_label}[/dim]\n")
                    return opt_id

        console.print(f"\x1b[{num_options}A\r", end="")
        render_lines()


def prompt_action() -> str:
    options = [
        ("accept", "Accept"),
        ("edit", "Edit"),
        ("regenerate", "Regenerate"),
        ("cancel", "Cancel"),
    ]
    return select_arrow_menu(options, prompt_text="What would you like to do?", default_index=0)


def prompt_edit(current_message: str) -> str:
    console.print("\n[bold cyan]Edit commit message[/bold cyan] (use arrow keys to navigate, press Enter when done):")
    if sys.stdin.isatty():
        try:
            from prompt_toolkit import prompt as pt_prompt
            edited = pt_prompt("> ", default=current_message)
            return edited.strip() if edited and edited.strip() else current_message
        except Exception:
            pass
    try:
        from rich.prompt import Prompt
        edited = Prompt.ask("[bold]> [/bold]", default=current_message, console=console).strip()
        return edited if edited else current_message
    except Exception:
        line = sys.stdin.readline().strip()
        return line if line else current_message


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


def show_settings_summary(summary: Dict[str, Any]) -> None:
    console.print("\n[bold cyan]Comit Configuration[/bold cyan]\n")
    console.print(f"  [bold]AI Provider:[/bold]        {summary['provider']}")
    console.print(f"  [bold]Groq Model:[/bold]         {summary['model']} [dim]({summary['model_source']})[/dim]")
    console.print(f"  [bold]Groq API Key:[/bold]       {summary['api_key_masked']} [dim]({summary['api_key_source']})[/dim]")
    console.print(f"  [bold]Config File:[/bold]        {summary['config_file']}")
    console.print(f"  [bold]Config File Status:[/bold] {'Present' if summary['config_exists'] else 'Not created (using defaults)'}\n")


def prompt_settings_menu() -> str:
    options = [
        ("view", "View configuration"),
        ("set_key", "Configure Groq API key"),
        ("set_model", "Configure model"),
        ("reset", "Reset configuration"),
        ("exit", "Exit"),
    ]
    return select_arrow_menu(options, prompt_text="Settings Menu", default_index=0, allow_quit_key=True)


def prompt_api_key() -> str:
    key = Prompt.ask(
        "[bold]Enter Groq API Key[/bold]",
        password=True,
        console=console,
    ).strip()
    return key


def prompt_model(current_model: str) -> str:
    if sys.stdin.isatty():
        try:
            from prompt_toolkit import prompt as pt_prompt
            model = pt_prompt("Enter Groq Model: ", default=current_model).strip()
            return model if model else current_model
        except Exception:
            pass
    model = Prompt.ask(
        "[bold]Enter Groq Model[/bold]",
        default=current_model,
        console=console,
    ).strip()
    return model if model else current_model


def prompt_confirm_reset() -> bool:
    return Confirm.ask(
        "[bold yellow]Are you sure you want to reset all user configuration?[/bold yellow]",
        default=False,
        console=console,
    )
