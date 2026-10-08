# Comit

> AI-powered Git commit messages that understand your project's commit style.

Comit is a lightweight developer CLI assistant for Git. It examines currently staged changes alongside recent commit history, infers your repository's conventions (such as Conventional Commits), and uses high-speed LLM inference (powered by Groq) to generate concise, accurate commit messages.

---

## Features

- Context-Aware: Analyzes both your staged diff and previous commit subjects to match repository style.
- Developer in Control: Review, edit, regenerate, or cancel suggestions before committing.
- Fast-Track Mode (-y): Automatically commit generated messages without prompts.
- Safe and Non-Destructive: Only examines staged changes (git diff --cached). Never modifies unstaged files or automatically stages changes.
- Minimal Dependencies: Built with Python 3.11+, Typer, Rich, and Groq SDK.

---

## Architecture

```text
Staged Git Diff (git diff --cached)
               ↓
Recent Commit History (git log -15)
               ↓
    Groq LLM (Prompt & Context)
               ↓
       Suggested Commit
               ↓
   Interactive User Action
   [a] Accept  [e] Edit  [r] Regenerate  [c] Cancel
               ↓
     Git Commit (git commit -m)
```

---

## Installation

### Prerequisites
- Python 3.11 or higher
- Git installed and accessible in your PATH

### Setup

1. Install locally from source:
   ```bash
   pip install -e .
   ```

   To install test dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

2. PATH Configuration (Windows):
   Ensure your Python Scripts directory (e.g. `C:\Users\<User>\AppData\Local\Programs\Python\Python313\Scripts` or active environment Scripts directory) is on your PATH so Git discovers the `git-ai` executable.

---

## Configuration

Comit uses Groq for fast model inference.

Create a `.env` file in your repository or root directory (or export the variable in your shell):

```env
GROQ_API_KEY=your_groq_api_key_here
```

Security Note: Never commit or expose your `.env` file. It is automatically ignored in `.gitignore`.

You can optionally customize the model via `GROQ_MODEL` (defaults to `qwen/qwen3.8-27b`):

```env
GROQ_MODEL=qwen/qwen3.8-27b
```

---

## Verifying Installation

Verify that the CLI extension is installed and discovered by Git:

```powershell
git-ai --version
```

and:

```powershell
git ai --version
```

Output:
```text
Comit version 0.1.0
```

---

## Usage

Comit integrates directly with Git as a subcommand:

### Standard Interactive Workflow

1. Stage your changes:
   ```bash
   git add <files>
   ```

2. Run Comit:
   ```bash
   git ai commit
   ```
   (or `comit commit`)

3. Review the suggested commit message:
   ```text
   $ git ai commit

   ✓ Staged changes analyzed
   ✓ Commit history analyzed
   
   ┌─ Suggested commit ───────────────────────────────────────────┐
   │                                                              │
   │   feat: add JWT refresh token support                        │
   │                                                              │
   └──────────────────────────────────────────────────────────────┘

   What would you like to do?

     [a] Accept
     [e] Edit
     [r] Regenerate
     [c] Cancel

   Select an option [a]: 
   ```

4. Actions:
   - `[a]` Accept: Runs `git commit -m "<message>"` and displays success.
   - `[e]` Edit: Lets you adjust the message in your terminal before confirming.
   - `[r]` Regenerate: Re-queries the AI model for an alternative message.
   - `[c]` Cancel: Aborts without making any commit or touching your staged files.

---

### Non-Interactive Fast Mode (-y)

For quick commits when you trust the AI generation:

```bash
git ai commit -y
```

Output:
```text
✓ Staged changes analyzed
✓ Commit history analyzed

✓ Generated:

  feat: add playlist sharing

✓ Commit created successfully
```

---

## Running Tests

Run the test suite using pytest:

```bash
pytest
```

---

## License

MIT License.
