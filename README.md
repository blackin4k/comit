# Comit

> AI-powered Git commit messages that understand your project's commit style.

Comit is a lightweight developer CLI for Git. It analyzes your staged changes and recent commit history, learns your repository's commit conventions, and generates concise, accurate commit messages using your choice of AI provider.

## Features

- **Multi-Provider Support** — Use Groq, Google Gemini, OpenAI, or local models with Ollama.
- **Context-aware** — Analyzes your staged diff and recent commit history to match your repository's style.
- **Developer in control** — Review, edit, regenerate, or cancel a suggested commit message before committing.
- **Push Integration** — Optional safe remote pushing after creating a commit.
- **Fast-track mode** — Use `-y` to automatically commit the generated message without confirmation.
- **Settings management** — Configure your provider, model, API keys, and endpoints interactively or via CLI commands.
- **Safe and non-destructive** — Only analyzes staged changes with `git diff --cached`. Comit never stages files or modifies unstaged changes.

## Supported Providers

| Provider | Default Model | Authentication | Setup / Env Variable |
| :--- | :--- | :--- | :--- |
| **Groq** *(Default)* | `qwen/qwen3.8-27b` | API Key | `GROQ_API_KEY` |
| **Google Gemini** | `gemini-2.5-flash` | API Key | `GEMINI_API_KEY` |
| **OpenAI** | `gpt-4o-mini` | API Key | `OPENAI_API_KEY` |
| **Ollama** | `llama3.2` | None (Local) | `OLLAMA_HOST` (default: `http://localhost:11434`) |

## Installation

### Requirements

- Python 3.11+
- Git

### Install Comit

Install Comit using pip:

```bash
pip install .
```

For editable local development:

```bash
pip install -e .
```

To install with additional provider SDKs:

```bash
# Google Gemini SDK
pip install -e ".[gemini]"

# OpenAI SDK
pip install -e ".[openai]"

# Ollama SDK
pip install -e ".[ollama]"

# All providers and testing tools
pip install -e ".[all,test]"
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

### 2. Configure Your Provider & API Key

Open the interactive settings menu:

```powershell
git ai settings
```

Or configure via CLI:

```powershell
# Select provider (groq, gemini, openai, ollama)
git ai settings set-provider groq

# Set API key for the active provider
git ai settings set-key

# Or specify the provider directly
git ai settings set-key --provider gemini
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

Options:
1. View configuration
2. Select AI provider
3. Configure API key / host
4. Configure model
5. Reset configuration
6. Exit

### Settings Commands

- **View configuration:**
  ```powershell
  git ai settings show
  ```

- **Set AI provider:**
  ```powershell
  git ai settings set-provider gemini
  ```

- **Set API key (masked prompt):**
  ```powershell
  git ai settings set-key
  git ai settings set-key --provider openai
  ```

- **Set model:**
  ```powershell
  git ai settings set-model qwen/qwen3.8-27b
  git ai settings set-model gpt-4o --provider openai
  ```

- **Set Ollama host URL:**
  ```powershell
  git ai settings set-host http://localhost:11434
  ```

- **Reset user configuration:**
  ```powershell
  git ai settings reset
  ```

### Configuration Precedence

Comit resolves settings in the following order:

1. **Environment variables**:
   - Provider: `COMIT_PROVIDER`
   - Model: `COMIT_MODEL`, `GROQ_MODEL`, `GEMINI_MODEL`, `OPENAI_MODEL`, `OLLAMA_MODEL`
   - API Keys / Endpoints: `GROQ_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`, `OLLAMA_HOST`
2. **User configuration** (`config.json` stored in `%APPDATA%\comit` on Windows or `~/.config/comit` on Linux/macOS)
3. **Application defaults** (Provider: `groq`, Model: `qwen/qwen3.8-27b`)

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

- **Accept (`a` or `1`)** — Creates the commit using the generated message. After the local commit succeeds, you are asked whether to push to the remote (`[y/N]`, default No).
- **Edit (`e` or `2`)** — Opens an interactive inline editor with the generated message pre-populated for modification.
- **Regenerate (`r` or `3`)** — Requests an alternative commit message from the AI provider while avoiding previous attempts.
- **Cancel (`c`, `q`, or `4`)** — Exits cleanly without creating a commit or modifying staged changes.

---

### Pushing Commits

Pushing is strictly opt-in and safe.

#### 1. Interactive commit with push confirmation

```bash
git ai commit
```

After accepting the commit, Comit asks:

```text
✓ Commit created successfully

  feat: add JWT refresh token support

Push this commit to the remote? [y/N]
```

Choosing `N` leaves the commit local:

```text
Commit created locally. Nothing was pushed.
```

#### 2. Automatic push after commit

```bash
git ai commit --push
```

Reviews the commit message interactively, and pushes automatically to `origin/<branch>` upon acceptance without a secondary prompt.

#### 3. Fast mode without push

```bash
git ai commit -y
```

Automatically accepts the generated commit message. Does **not** push to the remote.

#### 4. Fast mode with automatic push

```bash
git ai commit -y --push
```

Automatically accepts the generated message, creates the commit, and pushes to `origin/<branch>`.

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
- Push to a remote without explicit confirmation or `--push`
- Force push (`git push --force` is never executed)
- Write API keys or credentials into repository files

If no changes are staged, Comit exits without calling the AI provider.
If no Git remote is configured, Comit reports that no remote exists and leaves your commit local.

---

## Testing

Run the test suite with pytest:

```bash
pytest
```

---

## License

MIT License.