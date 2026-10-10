import os
import shutil
import subprocess
import sys
import sysconfig
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

COMIT_ROOT = Path(__file__).parent.parent.resolve()


def test_git_ai_subcommand():
    temp_dir = Path(tempfile.mkdtemp(prefix="git_ai_subcmd_"))
    try:
        # Initialize a clean, isolated Git repository
        subprocess.run(["git", "init"], cwd=str(temp_dir), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test Dev"], cwd=str(temp_dir), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(temp_dir), check=True, capture_output=True)

        # Locate scripts directory across platforms and Python environments
        scripts_path = sysconfig.get_path("scripts")
        candidate_dirs = [
            Path(scripts_path) if scripts_path else None,
            Path(sys.executable).parent,
            Path(sys.executable).parent / "Scripts",
            Path(sys.prefix) / "Scripts",
            Path(sys.prefix) / "bin",
            COMIT_ROOT / ".venv" / ("Scripts" if sys.platform == "win32" else "bin"),
        ]
        existing_dirs = [str(d.resolve()) for d in candidate_dirs if d and d.is_dir()]

        env = os.environ.copy()
        env["PATH"] = os.pathsep.join(existing_dirs + [env.get("PATH", "")])
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONPATH"] = f"{COMIT_ROOT / 'src'}{os.pathsep}{env.get('PYTHONPATH', '')}"

        # Ensure offline determinism
        env.pop("GROQ_API_KEY", None)
        env.pop("OPENAI_API_KEY", None)
        env.pop("GEMINI_API_KEY", None)

        # If git-ai executable is not already in PATH, create an isolated wrapper
        git_ai_bin = shutil.which("git-ai", path=env["PATH"])
        if git_ai_bin is None:
            bin_dir = temp_dir / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            if sys.platform == "win32":
                shim = bin_dir / "git-ai.cmd"
                shim.write_text(f'@"{sys.executable}" -m comit.cli %*\n', encoding="utf-8")
            else:
                shim = bin_dir / "git-ai"
                shim.write_text(f'#!/bin/sh\nexec "{sys.executable}" -m comit.cli "$@"\n', encoding="utf-8")
                shim.chmod(0o755)
            env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
            git_ai_bin = shutil.which("git-ai", path=env["PATH"])

        assert git_ai_bin is not None, f"git-ai executable not found in PATH: {env['PATH']}"

        # 1. Test 'git ai --version' (Git extension discovery and version output)
        res_version = subprocess.run(
            ["git", "ai", "--version"],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        assert res_version.returncode == 0
        assert "Comit version 0.2.0" in res_version.stdout

        # 2. Test 'git ai settings show' (Subcommand forwarding)
        res_settings = subprocess.run(
            ["git", "ai", "settings", "show"],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        assert res_settings.returncode == 0
        assert "AI Provider:" in res_settings.stdout
        assert "Comit Configuration" in res_settings.stdout

        # 3. Test 'git ai review' on staged changes (Deterministic offline review)
        sample_file = temp_dir / "sample.py"
        sample_file.write_text("print('sample code')\n", encoding="utf-8")
        subprocess.run(["git", "add", "sample.py"], cwd=str(temp_dir), check=True, capture_output=True)

        res_review = subprocess.run(
            ["git", "ai", "review"],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        assert res_review.returncode == 0
        assert "No issues detected." in res_review.stdout

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_git_ai_subcommand()
