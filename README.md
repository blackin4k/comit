# Comit

> AI-powered Git commit messages that understand your project's commit style.

Comit is a lightweight developer CLI for Git. It analyzes your staged changes and recent commit history, learns your repository's commit conventions, and uses fast LLM inference through Groq to generate concise, accurate commit messages.

## Features

- **Context-aware** — Analyzes your staged diff and recent commit history to match your repository's style.
- **Developer in control** — Review, edit, regenerate, or cancel a suggested commit message before committing.
- **Fast-track mode** — Use `-y` to automatically commit the generated message without confirmation.
- **Settings management** — Configure your API key and model interactively or via CLI commands without editing files.
- **Safe and non-destructive** — Only analyzes staged changes with `git diff --cached`. Comit never stages files or modifies unstaged changes.
- **Lightweight** — Built with Python, Typer, Rich, and the Groq SDK.

## How It Works

```text
Staged Git Diff
      |
      v
Recent Commit History
      |
      v
   Groq LLM
      |
      v
Suggested Commit
      |
      v
User Review
[a] Accept  [e] Edit  [r] Regenerate  [c] Cancel
      |
      v
   Git Commit
```

## Installation

### Requirements

- Python 3.11+
- Git
- A Groq API key

### Install Comit

Install Comit using pip:

```bash
pip install .
```

For editable local development:

```bash
pip install -e .
```

To install development and testing dependencies:

```bash
pip install -e ".[test]"
```

### Windows PATH Note

When installing Python packages with CLI scripts, pip places executables (like `git-ai.exe`) into your Python Scripts directory.

Make sure your Python Scripts directory is on your system or user `PATH` so Git discovers the `git ai` extension from any terminal session.

Common Python Scripts locations on Windows:
- System Python: `C:\Users\<Username>\AppData\Local\Programs\Python\Python313\Scripts`
- Virtual Environment: `<venv_path>\Scripts`

## Quick Start

### 1. Verify Installation

```powershell
git ai --version
```

Output:
```text
Comit version 0.1.0
```

### 2. Configure Your API Key

Run the interactive settings manager:

```powershell
git ai settings
```

Or set the key directly from the command line:

```powershell
git ai settings set-key
```

### 3. Generate Commit Messages

Stage your files:

```bash
git add <files>
```

Run Comit:

```bash
git ai commit
```

---

## Configuration & Settings

Comit provides an interactive configuration interface as well as non-interactive subcommands.

### Interactive Settings Menu

```powershell
git ai settings
```

Menu options:
1. View configuration
2. Configure Groq API key
3. Configure model
4. Reset configuration
5. Exit

### Settings Commands

- **View configuration:**
  ```powershell
  git ai settings show
  ```

- **Set Groq API key (hidden prompt):**
  ```powershell
  git ai settings set-key
  ```

- **Set Groq model:**
  ```powershell
  git ai settings set-model qwen/qwen3.8-27b
  ```

- **Reset user configuration:**
  ```powershell
  git ai settings reset
  ```

### Configuration Precedence

Comit resolves settings in the following order:

1. **Environment variables** (e.g. `GROQ_API_KEY`, `GROQ_MODEL`, or `.env` files in your workspace)
2. **User configuration** (`config.json` stored in your OS user directory: `%APPDATA%\comit` on Windows or `~/.config/comit` on Linux/macOS)
3. **Application defaults** (Model: `qwen/qwen3.8-27b`, Provider: `groq`)

---

## Usage

### Interactive Mode

First, stage your changes:

```bash
git add <files>
```

Then run:

```bash
git ai commit
```

Comit analyzes your staged changes and recent commit history before generating a suggestion:

```text
Staged changes analyzed
Commit history analyzed

Suggested commit:

  feat: add JWT refresh token support

What would you like to do?

  ❯ Accept
    Edit
    Regenerate
    Cancel
```

Navigate with **Up/Down arrow keys** or **k/j**, and press **Enter** to select.

### Actions

- **Accept (`a` or `1`)** — Creates the commit using the generated message.
- **Edit (`e` or `2`)** — Opens an interactive inline editor with the generated message pre-populated for modification.
- **Regenerate (`r` or `3`)** — Requests an alternative commit message from Groq while avoiding previous attempts.
- **Cancel (`c`, `q`, or `4`)** — Exits cleanly without creating a commit or modifying staged changes.

---

### Fast Mode (-y)

Use `-y` to automatically accept and commit the generated message without confirmation:

```bash
git ai commit -y
```

Example output:

```text
Staged changes analyzed
Commit history analyzed

Generated:

  feat: add playlist sharing

Commit created successfully
```

---

## Safety Guarantees

Comit only reads staged changes:

```bash
git diff --cached
```

Comit does NOT:
- Automatically run `git add`
- Modify unstaged files
- Modify working tree files
- Create a commit without approval (unless `-y` is explicitly passed)
- Write API keys or credentials into repository files

If no changes are staged, Comit exits without calling the AI provider.

---

## Testing

Run the test suite with pytest:

```bash
pytest
```

---

## License

MIT License.