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

def test_clean_installation():
    temp_dir = Path(tempfile.mkdtemp(prefix="comit_clean_env_"))
    print(f"Clean Test Base Directory: {temp_dir}")
    try:
        clean_venv = temp_dir / "test_venv"
        clean_repo = temp_dir / "external_project"

        # 1. Create a clean virtual environment
        print("\n1. Creating clean virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(clean_venv)], check=True)
        
        venv_pip = clean_venv / "Scripts" / "pip.exe"
        venv_scripts = clean_venv / "Scripts"

        # 2. Install comit package into clean environment
        print("2. Installing comit package into clean virtual environment...")
        res = subprocess.run([str(venv_pip), "install", "-e", str(COMIT_ROOT)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        assert res.returncode == 0
        print("   Installation succeeded.")

        # Set up clean environment PATH so git discovers git-ai
        env = os.environ.copy()
        env["PATH"] = f"{venv_scripts};{env.get('PATH', '')}"
        env["PYTHONIOENCODING"] = "utf-8"

        # Pass GROQ_API_KEY from .env
        env_vals = dotenv_values(COMIT_ROOT / ".env")
        for k, v in env_vals.items():
            if "groq" in k.lower() and v:
                env["GROQ_API_KEY"] = v.strip()
                break

        # 3. Test git-ai --version
        print("\n3. Testing git-ai --version...")
        git_ai_bin = shutil.which("git-ai", path=env["PATH"])
        assert git_ai_bin is not None
        res = subprocess.run([git_ai_bin, "--version"], capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        print("   git-ai --version output:", res.stdout.strip())
        assert res.returncode == 0
        assert "Comit version 0.1.0" in res.stdout

        # 4. Create an external Git repository
        print("\n4. Creating external Git repository outside Comit...")
        clean_repo.mkdir()
        subprocess.run(["git", "init"], cwd=str(clean_repo), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "External Dev"], cwd=str(clean_repo), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "external@dev.com"], cwd=str(clean_repo), check=True, capture_output=True)

        # Initial commit
        main_py = clean_repo / "main.py"
        main_py.write_text("def main():\n    print('hello')\n", encoding="utf-8")
        subprocess.run(["git", "add", "main.py"], cwd=str(clean_repo), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "feat: initial commit"], cwd=str(clean_repo), check=True, capture_output=True)

        # 5. Test git ai --version from external repo
        print("\n5. Testing git ai --version from external repository...")
        res = subprocess.run(["git", "ai", "--version"], cwd=str(clean_repo), capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        print("   git ai --version output:", res.stdout.strip())
        assert res.returncode == 0
        assert "Comit version 0.1.0" in res.stdout

        # 6. Test git ai commit -y from external repo with real Groq generation
        print("\n6. Testing git ai commit -y from external repository with real Groq...")
        main_py.write_text(
            "def calculate_total(items):\n    return sum(item['price'] for item in items)\n\n"
            "def main():\n    print('hello')\n",
            encoding="utf-8"
        )
        subprocess.run(["git", "add", "main.py"], cwd=str(clean_repo), check=True, capture_output=True)

        res = subprocess.run(["git", "ai", "commit", "-y"], cwd=str(clean_repo), capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        print("   git ai commit -y output:\n", res.stdout.strip())
        assert res.returncode == 0
        assert "Commit created successfully" in res.stdout

        log_res = subprocess.run(["git", "log", "-1", "--pretty=format:%s"], cwd=str(clean_repo), capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(f"   Generated commit subject: {log_res.stdout.strip()}")

        # 7. Test git ai commit (interactive accept)
        print("\n7. Testing git ai commit (interactive accept) from external repository...")
        main_py.write_text(
            "def calculate_total(items, tax_rate=0.05):\n    subtotal = sum(item['price'] for item in items)\n    return subtotal * (1 + tax_rate)\n\n"
            "def main():\n    print('hello')\n",
            encoding="utf-8"
        )
        subprocess.run(["git", "add", "main.py"], cwd=str(clean_repo), check=True, capture_output=True)

        res = subprocess.run(
            ["git", "ai", "commit"],
            cwd=str(clean_repo),
            input="a\n",
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env
        )
        print("   git ai commit interactive output:\n", res.stdout.strip())
        assert res.returncode == 0
        assert "Commit created successfully" in res.stdout

        log_res2 = subprocess.run(["git", "log", "-1", "--pretty=format:%s"], cwd=str(clean_repo), capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(f"   Generated commit subject: {log_res2.stdout.strip()}")

        print("\n=======================================================")
        print(" CLEAN ENVIRONMENT INSTALLATION TEST: 100% SUCCESS ")
        print("=======================================================")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_clean_installation()
