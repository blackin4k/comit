import subprocess
import sys
from pathlib import Path
import comit

COMIT_ROOT = Path(__file__).parent.parent.resolve()


def test_version_consistency():
    assert comit.__version__ == "0.2.0"

    pyproject_text = (COMIT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.2.0"' in pyproject_text


def test_package_metadata_and_name():
    pyproject_text = (COMIT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "comit"' in pyproject_text
    assert 'requires-python = ">=3.11"' in pyproject_text


def test_entry_points_defined():
    pyproject_text = (COMIT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'comit = "comit.cli:app"' in pyproject_text
    assert 'git-ai = "comit.cli:app"' in pyproject_text


def test_optional_dependency_groups():
    pyproject_text = (COMIT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "[project.optional-dependencies]" in pyproject_text
    assert "gemini =" in pyproject_text
    assert "openai =" in pyproject_text
    assert "ollama =" in pyproject_text
    assert "test =" in pyproject_text
    assert "all =" in pyproject_text


def test_build_and_twine_check(tmp_path):
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()

    # Build sdist and wheel into tmp_path/dist
    res_build = subprocess.run(
        [sys.executable, "-m", "build", "--outdir", str(dist_dir), str(COMIT_ROOT)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert res_build.returncode == 0, f"build failed:\n{res_build.stdout}\n{res_build.stderr}"

    wheel_files = list(dist_dir.glob("*.whl"))
    sdist_files = list(dist_dir.glob("*.tar.gz"))
    assert len(wheel_files) == 1, "Expected exactly 1 wheel file"
    assert len(sdist_files) == 1, "Expected exactly 1 sdist file"
    assert "comit-0.2.0" in wheel_files[0].name
    assert "comit-0.2.0" in sdist_files[0].name

    # Check distribution metadata with twine
    res_twine = subprocess.run(
        [sys.executable, "-m", "twine", "check", "--strict", str(wheel_files[0]), str(sdist_files[0])],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert res_twine.returncode == 0, f"twine check failed:\n{res_twine.stdout}\n{res_twine.stderr}"
    assert "PASSED" in res_twine.stdout
