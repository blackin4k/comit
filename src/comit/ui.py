from __future__ import annotations

import os
import sys
from typing import Optional, Dict, Any, List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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


def _run_prompt_toolkit_menu(
    options: List[Tuple[str, str]],
    prompt_text: str = "What would you like to do?",
    default_index: int = 0,
    allow_quit_key: bool = True,
) -> Optional[str]:
    from prompt_toolkit.application import Application
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import Layout, HSplit, Window
    from prompt_toolkit.layout.controls import FormattedTextControl
    from prompt_toolkit.styles import Style

    kb = KeyBindings()
    selected = [default_index]
    num_options = len(options)

    @kb.add("up")
    @kb.add("k")
    def _(event):
        selected[0] = (selected[0] - 1) % num_options

    @kb.add("down")
    @kb.add("j")
    def _(event):
        selected[0] = (selected[0] + 1) % num_options

    @kb.add("enter")
    def _(event):
        event.app.exit(result=options[selected[0]][0])

    if allow_quit_key:
        @kb.add("q")
        @kb.add("Q")
        def _(event):
            res = "cancel" if "cancel" in [o[0] for o in options] else "exit"
            event.app.exit(result=res)

    for opt_id, _ in options:
        first_char = opt_id[0].lower()
        @kb.add(first_char)
        def _(event, val=opt_id):
            event.app.exit(result=val)

    for idx, (opt_id, _) in enumerate(options, start=1):
        @kb.add(str(idx))
        def _(event, val=opt_id):
            event.app.exit(result=val)

    @kb.add("c-c")
    def _(event):
        res = "cancel" if "cancel" in [o[0] for o in options] else "exit"
        event.app.exit(result=res)

    def get_formatted_text():
        tokens = [("bold", f"{prompt_text}\n\n")]
        for i, (_, label) in enumerate(options):
            if i == selected[0]:
                tokens.append(("ansicyan bold", f"  ❯ {label}\n"))
            else:
                tokens.append(("", f"    {label}\n"))
        return tokens

    style = Style.from_dict({
        "prompt": "bold",
        "cursor": "ansicyan bold",
        "selected": "ansicyan bold",
        "unselected": "",
    })

    app = Application(
        layout=Layout(HSplit([Window(content=FormattedTextControl(get_formatted_text))])),
        key_bindings=kb,
        style=style,
        full_screen=False,
        erase_when_done=True,
    )

    return app.run()


def select_arrow_menu(
    options: List[Tuple[str, str]],
    prompt_text: str = "What would you like to do?",
    default_index: int = 0,
    allow_quit_key: bool = True,
) -> str:
    if sys.stdin.isatty() and sys.stdout.isatty():
        try:
            result = _run_prompt_toolkit_menu(
                options=options,
                prompt_text=prompt_text,
                default_index=default_index,
                allow_quit_key=allow_quit_key,
            )
            if result:
                label = dict(options).get(result, result.title())
                console.print(f"[dim]Selected: {label}[/dim]\n")
                return result
        except Exception:
            pass

    console.print(f"[bold]{prompt_text}[/bold]\n")
    for idx, (opt_id, opt_label) in enumerate(options, start=1):
        console.print(f"  [bold cyan]{opt_id}[/bold cyan] - {opt_label}")
    choices = [opt_id for opt_id, _ in options]
    if allow_quit_key:
        choices.extend(["q", "quit"])
    try:
        choice = Prompt.ask(
            "\n[bold]Select an option[/bold]",
            default=options[default_index][0],
            console=console,
        ).strip().lower()
    except Exception:
        return options[default_index][0]

    if allow_quit_key and choice in ("q", "quit"):
        return "cancel" if "cancel" in [o[0] for o in options] else "exit"
    for idx, (opt_id, opt_label) in enumerate(options, start=1):
        if choice in (opt_id.lower(), opt_label.lower(), str(idx), opt_id[:1].lower()):
            return opt_id
    return options[default_index][0]


def prompt_action() -> str:
    options = [
        ("accept", "Accept"),
        ("edit", "Edit"),
        ("regenerate", "Regenerate"),
        ("cancel", "Cancel"),
    ]
    return select_arrow_menu(options, prompt_text="What would you like to do?", default_index=0)


def prompt_edit(current_message: str) -> Optional[str]:
    console.print("\n[bold cyan]Edit commit message[/bold cyan] (press Enter to save, Esc or Ctrl+C to cancel):")
    while True:
        try:
            if sys.stdin.isatty() and sys.stdout.isatty():
                from prompt_toolkit import prompt as pt_prompt
                from prompt_toolkit.key_binding import KeyBindings

                kb = KeyBindings()
                cancelled = [False]

                @kb.add("escape")
                def _(event):
                    cancelled[0] = True
                    event.app.exit(result=None)

                edited = pt_prompt("> ", default=current_message, key_bindings=kb)
                if cancelled[0] or edited is None:
                    console.print("[dim]Edit cancelled. Keeping previous message.[/dim]")
                    return None

                cleaned = edited.strip()
                if not cleaned:
                    error_console.print("[bold red]✗[/bold red] Commit message cannot be empty. Please enter a valid message or press Esc to cancel.")
                    continue
                return cleaned
            else:
                from rich.prompt import Prompt
                edited = Prompt.ask("[bold]> [/bold]", default=current_message, console=console)
                if edited is None:
                    return None
                cleaned = edited.strip()
                if not cleaned:
                    error_console.print("[bold red]✗[/bold red] Commit message cannot be empty.")
                    return None
                return cleaned
        except (KeyboardInterrupt, EOFError):
            console.print("[dim]Edit cancelled. Keeping previous message.[/dim]")
            return None
        except Exception:
            return None


def prompt_confirm_continue_commit() -> bool:
    try:
        return Confirm.ask(
            "[bold]Continue to commit?[/bold]",
            default=False,
            console=console,
        )
    except Exception:
        return False



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
    console.print(f"  [bold]AI Provider:[/bold]        {summary['provider']} [dim]({summary.get('provider_source', 'default')})[/dim]")
    console.print(f"  [bold]Model:[/bold]              {summary['model']} [dim]({summary['model_source']})[/dim]")
    if summary['provider'] == "ollama":
        console.print(f"  [bold]Ollama Host:[/bold]        {summary['ollama_host']}")
    else:
        provider_title = summary['provider'].capitalize()
        console.print(f"  [bold]{provider_title} API Key:[/bold]    {summary['api_key_masked']} [dim]({summary['api_key_source']})[/dim]")
    console.print(f"  [bold]Config File:[/bold]        {summary['config_file']}")
    console.print(f"  [bold]Config File Status:[/bold] {'Present' if summary['config_exists'] else 'Not created (using defaults)'}\n")


def prompt_settings_menu(provider: str = "groq") -> str:
    options = [
        ("view", "View configuration"),
        ("set_provider", "Select AI provider"),
        ("set_key", f"Configure {provider.capitalize()} API key" if provider != "ollama" else "Configure Ollama host"),
        ("set_model", "Configure model"),
        ("reset", "Reset configuration"),
        ("exit", "Exit"),
    ]
    return select_arrow_menu(options, prompt_text="Settings Menu", default_index=0, allow_quit_key=True)


def prompt_provider_selection(current_provider: str = "groq") -> str:
    options = [
        ("groq", "Groq (Fast inference, default)"),
        ("gemini", "Google Gemini"),
        ("openai", "OpenAI"),
        ("ollama", "Ollama (Local models)"),
    ]
    idx = 0
    for i, (p_id, _) in enumerate(options):
        if p_id == current_provider:
            idx = i
            break
    return select_arrow_menu(options, prompt_text="Select AI Provider", default_index=idx, allow_quit_key=True)


def prompt_api_key(provider: str = "groq") -> str:
    provider_title = provider.capitalize()
    key = Prompt.ask(
        f"[bold]Enter {provider_title} API Key[/bold]",
        password=True,
        console=console,
    ).strip()
    return key


def prompt_model(current_model: str, provider: str = "groq") -> str:
    provider_title = provider.capitalize()
    if sys.stdin.isatty() and sys.stdout.isatty():
        try:
            from prompt_toolkit import prompt as pt_prompt
            model = pt_prompt(f"Enter {provider_title} Model: ", default=current_model).strip()
            return model if model else current_model
        except Exception:
            pass
    model = Prompt.ask(
        f"[bold]Enter {provider_title} Model[/bold]",
        default=current_model,
        console=console,
    ).strip()
    return model if model else current_model


def prompt_ollama_host(current_host: str = "http://localhost:11434") -> str:
    if sys.stdin.isatty() and sys.stdout.isatty():
        try:
            from prompt_toolkit import prompt as pt_prompt
            host = pt_prompt("Enter Ollama Host: ", default=current_host).strip()
            return host if host else current_host
        except Exception:
            pass
    host = Prompt.ask(
        "[bold]Enter Ollama Host[/bold]",
        default=current_host,
        console=console,
    ).strip()
    return host if host else current_host


def prompt_confirm_reset() -> bool:
    return Confirm.ask(
        "[bold yellow]Are you sure you want to reset all user configuration?[/bold yellow]",
        default=False,
        console=console,
    )


def prompt_confirm_push() -> bool:
    try:
        return Confirm.ask(
            "\n[bold]Push this commit to the remote?[/bold]",
            default=False,
            console=console,
        )
    except Exception:
        return False


def show_push_success(remote: str, branch: str) -> None:
    console.print(f"[bold green]✓[/bold green] Pushed to {remote}/{branch}\n")


def show_push_skipped() -> None:
    console.print("Commit created locally. Nothing was pushed.\n")


def show_no_remote(explicit_push: bool = False) -> None:
    if explicit_push:
        console.print("No Git remote is configured. Commit created locally; nothing was pushed.\n")
    else:
        console.print("No Git remote is configured. Commit created locally.\n")


def show_no_default_remote() -> None:
    console.print("No default push remote ('origin') found. Commit created locally; nothing was pushed.\n")


def show_push_error(error_message: str) -> None:
    error_console.print("\n[bold red]✗[/bold red] Push failed\n")
    error_console.print(f"  {error_message}\n")
    console.print("Your commit was created locally and was not lost.\n")


def display_review_result(result: Any) -> None:
    from comit.review.models import ReviewSeverity

    console.print()
    console.print("[bold]Comit Change Review[/bold]")
    console.print()

    files_count = result.files_checked
    files_label = f"{files_count} file{'s' if files_count != 1 else ''} changed"
    console.print(f"  {files_label}")
    console.print(f"  {result.diff_stat.insertions} additions")
    console.print(f"  {result.diff_stat.deletions} deletions")
    console.print()

    if not result.has_findings:
        console.print("[bold green]No issues detected.[/bold green]\n")
        return

    console.print("[bold]Findings:[/bold]\n")

    for finding in result.findings:
        if finding.severity == ReviewSeverity.HIGH:
            sev_tag = "[bold red]HIGH[/bold red]"
        elif finding.severity == ReviewSeverity.WARNING:
            sev_tag = "[bold yellow]WARNING[/bold yellow]"
        else:
            sev_tag = "[bold cyan]INFO[/bold cyan]"

        console.print(f"{sev_tag}")
        console.print(f"{finding.message}")
        console.print(f"[cyan]{finding.file_path}[/cyan]")
        if finding.details:
            console.print(f"  [dim]{finding.details}[/dim]")
        console.print()

    console.print("[bold]Review complete.[/bold]\n")
