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

def run_real_test():
    temp_dir = Path(tempfile.mkdtemp(prefix="comit_live_"))
    try:
        subprocess.run(["git", "init"], cwd=str(temp_dir), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Dev User"], cwd=str(temp_dir), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "dev@example.com"], cwd=str(temp_dir), check=True, capture_output=True)

        auth_file = temp_dir / "auth.py"
        auth_file.write_text(
            "def login(username: str, password: str) -> bool:\n"
            "    return username == 'admin' and password == 'secret'\n",
            encoding="utf-8"
        )
        subprocess.run(["git", "add", "auth.py"], cwd=str(temp_dir), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "feat: add user authentication"], cwd=str(temp_dir), check=True, capture_output=True)

        auth_file.write_text(
            "def validate_password(password: str) -> bool:\n"
            "    if len(password) < 8:\n"
            "        raise ValueError('Password must be at least 8 characters long')\n"
            "    if not any(c.isdigit() for c in password):\n"
            "        raise ValueError('Password must contain at least one digit')\n"
            "    return True\n\n"
            "def login(username: str, password: str) -> bool:\n"
            "    validate_password(password)\n"
            "    return username == 'admin' and password == 'secret'\n",
            encoding="utf-8"
        )
        subprocess.run(["git", "add", "auth.py"], cwd=str(temp_dir), check=True, capture_output=True)

        env_vals = dotenv_values(COMIT_ROOT / ".env")
        api_key = ""
        for k, v in env_vals.items():
            if "groq" in k.lower() and v:
                api_key = v.strip()
                break

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        if api_key:
            env["GROQ_API_KEY"] = api_key

        res = subprocess.run(
            [str(VENV_PYTHON), "-m", "comit.cli", "commit", "-y"],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )

        assert res.returncode == 0
        assert "Commit created successfully" in res.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    run_real_test()
