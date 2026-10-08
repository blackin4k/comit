import os
import subprocess
from pathlib import Path
import pytest

from comit.git import (
    is_git_repository,
    get_staged_diff,
    get_recent_commits,
    create_commit,
    get_remotes,
    get_default_remote,
    get_current_branch,
    push_commit,
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


def test_get_remotes_empty(temp_git_repo: Path):
    remotes = get_remotes(cwd=temp_git_repo)
    assert remotes == []
    assert get_default_remote(cwd=temp_git_repo) is None


def test_get_remotes_with_origin(temp_git_repo: Path):
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/example/repo.git"], cwd=str(temp_git_repo), check=True)
    remotes = get_remotes(cwd=temp_git_repo)
    assert remotes == ["origin"]
    assert get_default_remote(cwd=temp_git_repo) == "origin"


def test_get_remotes_multiple_with_origin(temp_git_repo: Path):
    subprocess.run(["git", "remote", "add", "upstream", "https://github.com/upstream/repo.git"], cwd=str(temp_git_repo), check=True)
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/example/repo.git"], cwd=str(temp_git_repo), check=True)
    remotes = get_remotes(cwd=temp_git_repo)
    assert "origin" in remotes
    assert "upstream" in remotes
    assert get_default_remote(cwd=temp_git_repo) == "origin"


def test_get_remotes_without_origin(temp_git_repo: Path):
    subprocess.run(["git", "remote", "add", "backup", "https://github.com/backup/repo.git"], cwd=str(temp_git_repo), check=True)
    subprocess.run(["git", "remote", "add", "upstream", "https://github.com/upstream/repo.git"], cwd=str(temp_git_repo), check=True)
    assert get_default_remote(cwd=temp_git_repo) is None


def test_get_current_branch(temp_git_repo: Path):
    f = temp_git_repo / "init.txt"
    f.write_text("initial", encoding="utf-8")
    subprocess.run(["git", "add", "init.txt"], cwd=str(temp_git_repo), check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(temp_git_repo), check=True)

    branch = get_current_branch(cwd=temp_git_repo)
    assert branch in ("master", "main")

    subprocess.run(["git", "checkout", "-b", "feature-test"], cwd=str(temp_git_repo), check=True)
    assert get_current_branch(cwd=temp_git_repo) == "feature-test"


def test_push_commit_success(temp_git_repo: Path):
    from unittest.mock import patch, MagicMock
    from comit.git import _run_git_command as real_run

    def mock_run(args, cwd=None):
        if args and args[0] == "push":
            res = MagicMock()
            res.returncode = 0
            res.stdout = "Everything up-to-date"
            res.stderr = ""
            return res
        return real_run(args, cwd=cwd)

    with patch("comit.git._run_git_command", side_effect=mock_run):
        success, output = push_commit("origin", "main", cwd=temp_git_repo)
        assert success is True
        assert "origin/main" in output or "up-to-date" in output


def test_push_commit_rejection_behind(temp_git_repo: Path):
    from unittest.mock import patch, MagicMock
    from comit.git import _run_git_command as real_run

    def mock_run(args, cwd=None):
        if args and args[0] == "push":
            res = MagicMock()
            res.returncode = 1
            res.stdout = ""
            res.stderr = "error: failed to push some refs to '...'\nhint: Updates were rejected because the remote contains work that you do\nhint: not have locally (fetch first)."
            return res
        return real_run(args, cwd=cwd)

    with patch("comit.git._run_git_command", side_effect=mock_run):
        success, output = push_commit("origin", "main", cwd=temp_git_repo)
        assert success is False
        assert "behind the remote" in output


def test_push_commit_auth_failure(temp_git_repo: Path):
    from unittest.mock import patch, MagicMock
    from comit.git import _run_git_command as real_run

    def mock_run(args, cwd=None):
        if args and args[0] == "push":
            res = MagicMock()
            res.returncode = 1
            res.stdout = ""
            res.stderr = "fatal: Authentication failed for 'https://github.com/example/repo.git/'"
            return res
        return real_run(args, cwd=cwd)

    with patch("comit.git._run_git_command", side_effect=mock_run):
        success, output = push_commit("origin", "main", cwd=temp_git_repo)
        assert success is False
        assert "Authentication failed" in output


def test_get_repository_name(temp_git_repo: Path):
    from comit.git import get_repository_name
    name = get_repository_name(cwd=temp_git_repo)
    assert name == "test_repo"


def test_get_repository_name_non_git(tmp_path: Path):
    from comit.git import get_repository_name
    non_repo = tmp_path / "custom_folder"
    non_repo.mkdir()
    name = get_repository_name(cwd=non_repo)
    assert name == "custom_folder"


def test_get_current_branch_detached_head(temp_git_repo: Path):
    f = temp_git_repo / "init.txt"
    f.write_text("initial", encoding="utf-8")
    subprocess.run(["git", "add", "init.txt"], cwd=str(temp_git_repo), check=True)
    subprocess.run(["git", "commit", "-m", "init commit"], cwd=str(temp_git_repo), check=True)

    res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(temp_git_repo), check=True, capture_output=True, text=True)
    head_sha = res.stdout.strip()

    subprocess.run(["git", "checkout", head_sha], cwd=str(temp_git_repo), check=True, capture_output=True)
    branch = get_current_branch(cwd=temp_git_repo)
    assert "detached" in branch
    assert head_sha in branch


def test_get_staged_changed_files_statuses(temp_git_repo: Path):
    from comit.git import get_staged_changed_files

    # 1. Baseline commit for modified, deleted, renamed files
    f2 = temp_git_repo / "file2.txt"
    f2.write_text("file 2 content", encoding="utf-8")
    f3 = temp_git_repo / "file3.txt"
    f3.write_text("file 3 content", encoding="utf-8")
    f4 = temp_git_repo / "file4.txt"
    f4.write_text("file 4 content", encoding="utf-8")
    subprocess.run(["git", "add", "file2.txt", "file3.txt", "file4.txt"], cwd=str(temp_git_repo), check=True)
    subprocess.run(["git", "commit", "-m", "setup baseline"], cwd=str(temp_git_repo), check=True)

    # 2. Add brand new file
    f1 = temp_git_repo / "file1_added.txt"
    f1.write_text("file 1 content", encoding="utf-8")
    subprocess.run(["git", "add", "file1_added.txt"], cwd=str(temp_git_repo), check=True)

    # 3. Modify f2
    f2.write_text("file 2 modified content", encoding="utf-8")
    subprocess.run(["git", "add", "file2.txt"], cwd=str(temp_git_repo), check=True)

    # 4. Delete f3
    subprocess.run(["git", "rm", "file3.txt"], cwd=str(temp_git_repo), check=True)

    # 5. Rename f4 -> f4_renamed
    subprocess.run(["git", "mv", "file4.txt", "file4_renamed.txt"], cwd=str(temp_git_repo), check=True)

    # Also make an UNSTAGED change to ensure it is isolated
    unstaged_file = temp_git_repo / "unstaged.txt"
    unstaged_file.write_text("unstaged", encoding="utf-8")

    staged_files = get_staged_changed_files(cwd=temp_git_repo)
    status_by_path = {f.path: f for f in staged_files}

    assert "file1_added.txt" in status_by_path
    assert status_by_path["file1_added.txt"].status == "A"
    assert status_by_path["file1_added.txt"].display_status == "Added"

    assert "file2.txt" in status_by_path
    assert status_by_path["file2.txt"].status == "M"
    assert status_by_path["file2.txt"].display_status == "Modified"

    assert "file3.txt" in status_by_path
    assert status_by_path["file3.txt"].status == "D"
    assert status_by_path["file3.txt"].display_status == "Deleted"

    assert "file4_renamed.txt" in status_by_path
    assert status_by_path["file4_renamed.txt"].status == "R"
    assert status_by_path["file4_renamed.txt"].old_path == "file4.txt"
    assert status_by_path["file4_renamed.txt"].display_status == "Renamed"

    # Ensure unstaged file is not present
    assert "unstaged.txt" not in status_by_path


def test_get_diff_stat(temp_git_repo: Path):
    from comit.git import get_diff_stat

    stat_empty = get_diff_stat(cwd=temp_git_repo)
    assert stat_empty.files_changed == 0
    assert stat_empty.insertions == 0
    assert stat_empty.deletions == 0

    f1 = temp_git_repo / "a.txt"
    f1.write_text("line1\nline2\nline3\n", encoding="utf-8")
    subprocess.run(["git", "add", "a.txt"], cwd=str(temp_git_repo), check=True)

    stat = get_diff_stat(cwd=temp_git_repo)
    assert stat.files_changed == 1
    assert stat.insertions == 3
    assert stat.deletions == 0
    assert "1 file changed" in stat.format_summary()


def test_get_commit_context_complete(temp_git_repo: Path):
    from comit.git import get_commit_context

    f = temp_git_repo / "main.py"
    f.write_text("print('comit')\n", encoding="utf-8")
    subprocess.run(["git", "add", "main.py"], cwd=str(temp_git_repo), check=True)
    subprocess.run(["git", "commit", "-m", "chore: setup repo"], cwd=str(temp_git_repo), check=True)

    f2 = temp_git_repo / "feature.py"
    f2.write_text("def run():\n    return True\n", encoding="utf-8")
    subprocess.run(["git", "add", "feature.py"], cwd=str(temp_git_repo), check=True)

    context = get_commit_context(cwd=temp_git_repo)
    assert context.repository_name == "test_repo"
    assert context.current_branch in ("master", "main")
    assert len(context.changed_files) == 1
    assert context.changed_files[0].path == "feature.py"
    assert context.changed_files[0].status == "A"
    assert context.diff_stat.files_changed == 1
    assert context.diff_stat.insertions >= 1
    assert context.recent_commits == ["chore: setup repo"]
    assert "def run():" in context.staged_diff


def test_review_staged_unstaged_safety(temp_git_repo: Path):
    from comit.git import get_commit_context
    from comit.review import ReviewEngine

    safe_file = temp_git_repo / "safe.py"
    safe_file.write_text("print('safe code')\n", encoding="utf-8")
    subprocess.run(["git", "add", "safe.py"], cwd=str(temp_git_repo), check=True)

    # Create unstaged dangerous files and modifications
    dangerous_env = temp_git_repo / ".env"
    dangerous_env.write_text("SECRET_KEY=supersecret\n", encoding="utf-8")

    dangerous_code = temp_git_repo / "leak.py"
    dangerous_code.write_text("groq_key = 'gsk_123456789012345678901234'\n", encoding="utf-8")

    # The review must ONLY inspect staged changes
    ctx = get_commit_context(cwd=temp_git_repo)
    result = ReviewEngine().run(ctx)

    assert not result.has_findings
    assert result.files_checked == 1
    assert result.findings == []

    # Now stage the dangerous file
    subprocess.run(["git", "add", ".env"], cwd=str(temp_git_repo), check=True)
    ctx_updated = get_commit_context(cwd=temp_git_repo)
    result_updated = ReviewEngine().run(ctx_updated)

    assert result_updated.has_findings
    assert any(f.file_path == ".env" for f in result_updated.findings)
