import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from dotenv import dotenv_values

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

COMIT_ROOT = Path(__file__).parent.parent.resolve()
VENV_PYTHON = COMIT_ROOT / ".venv" / "Scripts" / "python.exe"

def run_cmd(cmd, cwd=None, input_text=None, env=None):
    merged_env = os.environ.copy()
    merged_env["PYTHONIOENCODING"] = "utf-8"
    if env:
        merged_env.update(env)
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        input=input_text,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        env=merged_env,
    )

def run_qa_pass():
    temp_dir = Path(tempfile.mkdtemp(prefix="comit_qa_"))
    try:
        res = run_cmd([str(VENV_PYTHON), "-m", "comit.cli", "commit"], cwd=temp_dir)
        assert res.returncode == 1
        assert "Not a Git repository" in (res.stdout + res.stderr)

        run_cmd(["git", "init"], cwd=temp_dir)
        run_cmd(["git", "config", "user.name", "Developer"], cwd=temp_dir)
        run_cmd(["git", "config", "user.email", "dev@example.com"], cwd=temp_dir)

        auth_file = temp_dir / "auth.py"
        auth_file.write_text("def login(username, password):\n    return True\n", encoding="utf-8")
        run_cmd(["git", "add", "auth.py"], cwd=temp_dir)
        run_cmd(["git", "commit", "-m", "feat: add user authentication"], cwd=temp_dir)

        session_file = temp_dir / "session.py"
        session_file.write_text("def validate_session(token):\n    return len(token) > 0\n", encoding="utf-8")
        run_cmd(["git", "add", "session.py"], cwd=temp_dir)
        run_cmd(["git", "commit", "-m", "fix: handle expired sessions"], cwd=temp_dir)

        db_file = temp_dir / "database.py"
        db_file.write_text("def get_connection():\n    return 'db_connection'\n", encoding="utf-8")
        run_cmd(["git", "add", "database.py"], cwd=temp_dir)
        run_cmd(["git", "commit", "-m", "refactor: simplify database connection"], cwd=temp_dir)

        res = run_cmd([str(VENV_PYTHON), "-m", "comit.cli", "commit"], cwd=temp_dir)
        assert res.returncode == 1
        assert "No staged changes found" in (res.stdout + res.stderr)

        auth_file.write_text(
            "def login(username, password):\n    return True\n\n"
            "def refresh_token(token):\n    return f'refreshed_{token}'\n",
            encoding="utf-8"
        )
        run_cmd(["git", "add", "auth.py"], cwd=temp_dir)

        mock_cli_script = temp_dir / "qa_mock_runner.py"
        mock_cli_script.write_text("""
import sys
from unittest.mock import patch
from comit.cli import app

generated_messages = ["feat: add JWT refresh token support", "feat: add refresh token generator"]
call_count = 0

def mock_generate(diff, recent_commits):
    global call_count
    msg = generated_messages[call_count % len(generated_messages)]
    call_count += 1
    return msg

with patch("comit.cli.generate_commit_message", side_effect=mock_generate):
    try:
        app()
    except SystemExit as e:
        sys.exit(e.code)
""", encoding="utf-8")

        res = run_cmd([str(VENV_PYTHON), str(mock_cli_script), "commit"], cwd=temp_dir, input_text="c\n")
        assert res.returncode == 0
        assert "Cancelled" in res.stdout

        res = run_cmd(
            [str(VENV_PYTHON), str(mock_cli_script), "commit"],
            cwd=temp_dir,
            input_text="e\nfeat: implement auth token refresh helper\na\n"
        )
        assert res.returncode == 0
        assert "Commit created successfully" in res.stdout

        db_file.write_text(
            "def get_connection():\n    return 'db_connection'\n\n"
            "def close_connection(conn):\n    pass\n",
            encoding="utf-8"
        )
        run_cmd(["git", "add", "database.py"], cwd=temp_dir)

        res = run_cmd(
            [str(VENV_PYTHON), str(mock_cli_script), "commit"],
            cwd=temp_dir,
            input_text="r\na\n"
        )
        assert res.returncode == 0
        assert "Commit created successfully" in res.stdout

        session_file.write_text(
            "def validate_session(token):\n    return len(token) > 0\n\n"
            "def invalidate_session(token):\n    return True\n",
            encoding="utf-8"
        )
        run_cmd(["git", "add", "session.py"], cwd=temp_dir)

        res = run_cmd([str(VENV_PYTHON), str(mock_cli_script), "commit", "-y"], cwd=temp_dir)
        assert res.returncode == 0
        assert "Commit created successfully" in res.stdout

        print("QA pass completed successfully.")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    run_qa_pass()
