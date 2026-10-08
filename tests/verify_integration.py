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

def test_integration():
    temp_dir = Path(tempfile.mkdtemp(prefix="comit_test_"))
    try:
        res = run_cmd([str(VENV_PYTHON), "-m", "comit.cli", "commit"], cwd=temp_dir)
        assert res.returncode == 1
        assert "Not a Git repository" in (res.stdout + res.stderr)

        run_cmd(["git", "init"], cwd=temp_dir)
        run_cmd(["git", "config", "user.name", "Test Committer"], cwd=temp_dir)
        run_cmd(["git", "config", "user.email", "committer@test.com"], cwd=temp_dir)

        res = run_cmd([str(VENV_PYTHON), "-m", "comit.cli", "commit"], cwd=temp_dir)
        assert res.returncode == 1
        assert "No staged changes found" in (res.stdout + res.stderr)

        dummy_file = temp_dir / "calculator.py"
        dummy_file.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
        run_cmd(["git", "add", "calculator.py"], cwd=temp_dir)
        
        custom_env = {"GROQ_API_KEY": ""}
        res = run_cmd([str(VENV_PYTHON), "-m", "comit.cli", "commit", "-y"], cwd=temp_dir, env=custom_env)
        assert res.returncode == 1
        assert "GROQ_API_KEY" in (res.stdout + res.stderr)

        custom_env = {"GROQ_API_KEY": "invalid_test_key_12345"}
        res = run_cmd([str(VENV_PYTHON), "-m", "comit.cli", "commit", "-y"], cwd=temp_dir, env=custom_env)
        assert res.returncode == 1
        assert "authentication failed" in (res.stdout + res.stderr).lower()

        mock_runner = temp_dir / "run_mock_cli.py"
        mock_runner.write_text("""
import sys
from unittest.mock import patch
from comit.cli import app

with patch("comit.cli.generate_commit_message", return_value="feat: add calculator function"):
    try:
        app()
    except SystemExit as e:
        sys.exit(e.code)
""", encoding="utf-8")

        res = run_cmd([str(VENV_PYTHON), str(mock_runner), "commit", "-y"], cwd=temp_dir)
        assert res.returncode == 0
        assert "Commit created successfully" in res.stdout

        dummy_file2 = temp_dir / "auth.py"
        dummy_file2.write_text("def authenticate(): return True\n", encoding="utf-8")
        run_cmd(["git", "add", "auth.py"], cwd=temp_dir)

        res = run_cmd([str(VENV_PYTHON), str(mock_runner), "commit"], cwd=temp_dir, input_text="c\n")
        assert res.returncode == 0
        assert "Cancelled" in res.stdout

        res = run_cmd([str(VENV_PYTHON), str(mock_runner), "commit"], cwd=temp_dir, input_text="e\nfeat: implement token auth\na\n")
        assert res.returncode == 0
        assert "Commit created successfully" in res.stdout

        dummy_file3 = temp_dir / "utils.py"
        dummy_file3.write_text("def format_date(d): return str(d)\n", encoding="utf-8")
        run_cmd(["git", "add", "utils.py"], cwd=temp_dir)

        res = run_cmd([str(VENV_PYTHON), str(mock_runner), "commit"], cwd=temp_dir, input_text="r\na\n")
        assert res.returncode == 0
        assert "Commit created successfully" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_integration()
