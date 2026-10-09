from __future__ import annotations

import os
import sys
from typing import Optional, Dict, Any, List, Tuple
from rich.console import Console
from rich.prompt import Prompt, Confirm

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
    console.print(message)


def show_step_error(message: str) -> None:
    error_console.print(f"Error: {message}")


def show_not_git_repository() -> None:
    error_console.print("Not a Git repository.")


def show_no_staged_changes() -> None:
    error_console.print("No staged changes found.\n")
    error_console.print("Stage your changes first:")
    error_console.print("  git add <files>\n")


def display_suggested_commit(message: str, title: str = "Generated") -> None:
    console.print(f"{title}:\n\n  {message}\n")


def _run_prompt_toolkit_menu(
    options: List[Tuple[str, str]],
    prompt_text: str = "",
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
        tokens = []
        if prompt_text:
            tokens.append(("bold", f"{prompt_text}\n\n"))
        for i, (_, label) in enumerate(options):
            if i == selected[0]:
                tokens.append(("ansicyan bold", f"> {label}\n"))
            else:
                tokens.append(("", f"  {label}\n"))
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
    prompt_text: str = "",
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
                return result
        except Exception:
            pass

    if prompt_text:
        console.print(f"{prompt_text}\n")
    for idx, (opt_id, opt_label) in enumerate(options, start=1):
        console.print(f"  {opt_id} - {opt_label}")
    choices = [opt_id for opt_id, _ in options]
    if allow_quit_key:
        choices.extend(["q", "quit"])
    try:
        choice = Prompt.ask(
            "\nSelect an option",
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
    return select_arrow_menu(options, prompt_text="", default_index=0)


def prompt_edit(current_message: str) -> Optional[str]:
    console.print("\nEdit commit message (press Enter to save, Esc or Ctrl+C to cancel):")
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
                    console.print("Edit cancelled. Keeping previous message.")
                    return None

                cleaned = edited.strip()
                if not cleaned:
                    error_console.print("Commit message cannot be empty. Please enter a valid message or press Esc to cancel.")
                    continue
                return cleaned
            else:
                from rich.prompt import Prompt
                edited = Prompt.ask("> ", default=current_message, console=console)
                if edited is None:
                    return None
                cleaned = edited.strip()
                if not cleaned:
                    error_console.print("Commit message cannot be empty.")
                    return None
                return cleaned
        except (KeyboardInterrupt, EOFError):
            console.print("Edit cancelled. Keeping previous message.")
            return None
        except Exception:
            return None


def prompt_confirm_continue_commit() -> bool:
    try:
        return Confirm.ask(
            "Continue to commit?",
            default=False,
            console=console,
        )
    except Exception:
        return False


def show_commit_success(message: str) -> None:
    console.print("\nCommit created successfully.\n")
    console.print(f"  {message}\n")


def show_auto_commit_success(message: str) -> None:
    console.print(f"\nGenerated:\n\n  {message}\n\nCommit created successfully.\n")


def show_cancelled() -> None:
    console.print("\nCancelled. No commit was created.\n")


def show_error(message: str) -> None:
    error_console.print(f"Error: {message}")


def show_settings_summary(summary: Dict[str, Any]) -> None:
    console.print("\nComit Configuration\n")
    console.print(f"  AI Provider:        {summary['provider']} ({summary.get('provider_source', 'default')})")
    console.print(f"  Model:              {summary['model']} ({summary['model_source']})")
    if summary['provider'] == "ollama":
        console.print(f"  Ollama Host:        {summary['ollama_host']}")
    else:
        provider_title = summary['provider'].capitalize()
        console.print(f"  {provider_title} API Key:    {summary['api_key_masked']} ({summary['api_key_source']})")
    console.print(f"  Config File:        {summary['config_file']}")
    console.print(f"  Config File Status: {'Present' if summary['config_exists'] else 'Not created (using defaults)'}\n")


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
        f"Enter {provider_title} API Key",
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
        f"Enter {provider_title} Model",
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
        "Enter Ollama Host",
        default=current_host,
        console=console,
    ).strip()
    return host if host else current_host


def prompt_confirm_reset() -> bool:
    return Confirm.ask(
        "Are you sure you want to reset all user configuration?",
        default=False,
        console=console,
    )


def prompt_confirm_push() -> bool:
    try:
        return Confirm.ask(
            "\nPush this commit to the remote?",
            default=False,
            console=console,
        )
    except Exception:
        return False


def show_push_success(remote: str, branch: str) -> None:
    console.print(f"Pushed to {remote}/{branch}.\n")


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
    error_console.print("\nPush failed:\n")
    error_console.print(f"  {error_message}\n")
    console.print("Your commit was created locally and was not lost.\n")


def display_review_result(result: Any) -> None:
    from comit.review.models import ReviewSeverity

    if not result.has_findings:
        console.print("No issues detected.\n")
        return

    console.print("Review findings:\n")

    for finding in result.findings:
        if finding.severity == ReviewSeverity.HIGH:
            sev_tag = "HIGH"
        elif finding.severity == ReviewSeverity.WARNING:
            sev_tag = "WARNING"
        else:
            sev_tag = "INFO"

        console.print(f"{sev_tag}")
        console.print(f"{finding.message}")
        console.print(f"{finding.file_path}")
        if finding.details:
            console.print(f"  {finding.details}")
        console.print()


def display_validation_result(result: Any) -> None:
    if not result.has_warnings and not result.has_errors:
        return

    console.print("Validation warning:\n")
    for finding in result.findings:
        if finding.severity.value in ("WARNING", "ERROR"):
            console.print(f"  {finding.message}")
            if finding.details:
                console.print(f"    {finding.details}")
    console.print()
