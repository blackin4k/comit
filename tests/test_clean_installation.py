import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

COMIT_ROOT = Path(__file__).parent.parent.resolve()


def test_clean_installation():
    temp_dir = Path(tempfile.mkdtemp(prefix="comit_clean_env_"))
    try:
        clean_venv = temp_dir / "test_venv"
        clean_repo = temp_dir / "external_project"

        # 1. Create a clean virtual environment
        subprocess.run([sys.executable, "-m", "venv", str(clean_venv)], check=True)

        if sys.platform == "win32":
            venv_bin = clean_venv / "Scripts"
            pip_exe = venv_bin / "pip.exe"
            python_exe = venv_bin / "python.exe"
        else:
            venv_bin = clean_venv / "bin"
            pip_exe = venv_bin / "pip"
            python_exe = venv_bin / "python"

        assert pip_exe.exists(), f"pip executable not found at {pip_exe}"
        assert python_exe.exists(), f"python executable not found at {python_exe}"

        # 2. Clean non-editable installation of comit
        res = subprocess.run(
            [str(pip_exe), "install", str(COMIT_ROOT)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert res.returncode == 0, f"pip install failed:\n{res.stdout}\n{res.stderr}"

        # Configure PATH to include clean venv binaries
        env = os.environ.copy()
        env["PATH"] = f"{venv_bin}{os.pathsep}{env.get('PATH', '')}"
        env["PYTHONIOENCODING"] = "utf-8"
        # Ensure external env does not leak API keys by default for the missing-key test
        env.pop("GROQ_API_KEY", None)
        env.pop("OPENAI_API_KEY", None)
        env.pop("GEMINI_API_KEY", None)

        # 3. Test git-ai and comit --version
        git_ai_bin = shutil.which("git-ai", path=env["PATH"])
        comit_bin = shutil.which("comit", path=env["PATH"])
        assert git_ai_bin is not None, "git-ai executable not found in PATH"
        assert comit_bin is not None, "comit executable not found in PATH"

        res = subprocess.run(
            [git_ai_bin, "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        assert res.returncode == 0
        assert "Comit version 0.2.0" in res.stdout

        res_comit = subprocess.run(
            [comit_bin, "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        assert res_comit.returncode == 0
        assert "Comit version 0.2.0" in res_comit.stdout

        # 4. Create an external Git repository
        clean_repo.mkdir()
        subprocess.run(["git", "init"], cwd=str(clean_repo), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "External Dev"], cwd=str(clean_repo), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "external@dev.com"], cwd=str(clean_repo), check=True, capture_output=True)

        # 5. Test git ai --version from external repo
        res = subprocess.run(
            ["git", "ai", "--version"],
            cwd=str(clean_repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        assert res.returncode == 0
        assert "Comit version 0.2.0" in res.stdout

        # 6. Test git ai settings show from external repo (works offline)
        res = subprocess.run(
            ["git", "ai", "settings", "show"],
            cwd=str(clean_repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        assert res.returncode == 0
        assert "AI Provider:" in res.stdout
        assert "Comit Configuration" in res.stdout

        # 7. Test git ai review in external repo with staged change
        main_py = clean_repo / "main.py"
        main_py.write_text("def main():\n    print('hello world')\n", encoding="utf-8")
        subprocess.run(["git", "add", "main.py"], cwd=str(clean_repo), check=True, capture_output=True)

        res_review = subprocess.run(
            ["git", "ai", "review"],
            cwd=str(clean_repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        assert res_review.returncode == 0
        assert "No issues detected." in res_review.stdout

        # 8. Test clean error handling when API key is missing
        res_no_key = subprocess.run(
            ["git", "ai", "commit", "-y"],
            cwd=str(clean_repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        assert res_no_key.returncode == 1
        combined_err = res_no_key.stdout + res_no_key.stderr
        assert "Error:" in combined_err
        assert "GROQ_API_KEY" in combined_err or "API key" in combined_err

        # 9. Optional live test behind explicit opt-in environment variable
        if os.environ.get("COMIT_RUN_LIVE_TESTS") == "1" and os.environ.get("GROQ_API_KEY"):
            env_with_key = env.copy()
            env_with_key["GROQ_API_KEY"] = os.environ["GROQ_API_KEY"]
            res_live = subprocess.run(
                ["git", "ai", "commit", "-y"],
                cwd=str(clean_repo),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env_with_key,
            )
            assert res_live.returncode == 0
            assert "Commit created successfully" in res_live.stdout

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_clean_installation()
