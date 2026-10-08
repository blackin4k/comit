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
VENV_SCRIPTS = COMIT_ROOT / ".venv" / "Scripts"

def test_git_ai_subcommand():
    temp_dir = Path(tempfile.mkdtemp(prefix="git_ai_subcmd_"))
    try:
        subprocess.run(["git", "init"], cwd=str(temp_dir), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Tester"], cwd=str(temp_dir), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "tester@test.com"], cwd=str(temp_dir), check=True, capture_output=True)

        env_vals = dotenv_values(COMIT_ROOT / ".env")
        api_key = ""
        for k, v in env_vals.items():
            if "groq" in k.lower() and v:
                api_key = v.strip()
                break

        env = os.environ.copy()
        env["PATH"] = f"{VENV_SCRIPTS};{env.get('PATH', '')}"
        env["PYTHONIOENCODING"] = "utf-8"
        if api_key:
            env["GROQ_API_KEY"] = api_key

        test_file = temp_dir / "sample.py"
        test_file.write_text("print('sample')\n", encoding="utf-8")
        subprocess.run(["git", "add", "sample.py"], cwd=str(temp_dir), check=True, capture_output=True)

        res = subprocess.run(
            ["git", "ai", "commit", "-y"],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        assert res.returncode == 0
        assert "Commit created successfully" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_git_ai_subcommand()
