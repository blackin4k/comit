import os
import subprocess
from pathlib import Path
import pytest

from comit.git import (
    is_git_repository,
    get_staged_diff,
    get_recent_commits,
    create_commit,
    NotAGitRepositoryError,
    GitCommitError,
)


@pytest.fixture
def temp_git_repo(tmp_path: Path):
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()

    subprocess.run(["git", "init"], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(repo_dir), check=True, capture_output=True)

    return repo_dir


def test_is_git_repository_true(temp_git_repo: Path):
    assert is_git_repository(cwd=temp_git_repo) is True


def test_is_git_repository_false(tmp_path: Path):
    non_repo = tmp_path / "not_a_repo"
    non_repo.mkdir()
    assert is_git_repository(cwd=non_repo) is False


def test_get_staged_diff_outside_repo(tmp_path: Path):
    non_repo = tmp_path / "not_a_repo"
    non_repo.mkdir()
    with pytest.raises(NotAGitRepositoryError):
        get_staged_diff(cwd=non_repo)


def test_get_staged_diff_empty(temp_git_repo: Path):
    diff = get_staged_diff(cwd=temp_git_repo)
    assert diff == ""


def test_get_staged_diff_with_staged_files(temp_git_repo: Path):
    test_file = temp_git_repo / "hello.py"
    test_file.write_text("print('hello world')\n", encoding="utf-8")
    
    assert get_staged_diff(cwd=temp_git_repo) == ""

    subprocess.run(["git", "add", "hello.py"], cwd=str(temp_git_repo), check=True, capture_output=True)

    diff = get_staged_diff(cwd=temp_git_repo)
    assert "print('hello world')" in diff
    assert "diff --git a/hello.py b/hello.py" in diff


def test_get_recent_commits_empty_repo(temp_git_repo: Path):
    commits = get_recent_commits(cwd=temp_git_repo)
    assert commits == []


def test_get_recent_commits_with_history(temp_git_repo: Path):
    f1 = temp_git_repo / "file1.txt"
    f1.write_text("content 1", encoding="utf-8")
    subprocess.run(["git", "add", "file1.txt"], cwd=str(temp_git_repo), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feat: initial feature"], cwd=str(temp_git_repo), check=True, capture_output=True)

    f2 = temp_git_repo / "file2.txt"
    f2.write_text("content 2", encoding="utf-8")
    subprocess.run(["git", "add", "file2.txt"], cwd=str(temp_git_repo), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "fix: resolve bug in parser"], cwd=str(temp_git_repo), check=True, capture_output=True)

    commits = get_recent_commits(count=10, cwd=temp_git_repo)
    assert len(commits) == 2
    assert commits[0] == "fix: resolve bug in parser"
    assert commits[1] == "feat: initial feature"


def test_create_commit_success(temp_git_repo: Path):
    f = temp_git_repo / "test.txt"
    f.write_text("sample", encoding="utf-8")
    subprocess.run(["git", "add", "test.txt"], cwd=str(temp_git_repo), check=True, capture_output=True)

    success, output = create_commit("feat: add sample file", cwd=temp_git_repo)
    assert success is True
    assert "feat: add sample file" in output

    recent = get_recent_commits(cwd=temp_git_repo)
    assert len(recent) == 1
    assert recent[0] == "feat: add sample file"


def test_create_commit_empty_message(temp_git_repo: Path):
    with pytest.raises(GitCommitError):
        create_commit("   ", cwd=temp_git_repo)
