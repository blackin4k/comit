from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple

from comit.commit.context import ChangedFile, DiffStat, CommitContext


class GitError(Exception):
    pass


class GitNotInstalledError(GitError):
    pass


class NotAGitRepositoryError(GitError):
    pass


class NoStagedChangesError(GitError):
    pass


class GitCommitError(GitError):
    pass


def _run_git_command(args: List[str], cwd: Optional[Path | str] = None) -> subprocess.CompletedProcess[str]:
    cmd = ["git"] + args
    try:
        return subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GitNotInstalledError(
            "Git is not installed or not found in system PATH. Please install Git to use Comit."
        ) from exc


def is_git_repository(cwd: Optional[Path | str] = None) -> bool:
    res = _run_git_command(["rev-parse", "--is-inside-work-tree"], cwd=cwd)
    return res.returncode == 0 and res.stdout.strip() == "true"


def get_repository_name(cwd: Optional[Path | str] = None) -> str:
    if not is_git_repository(cwd):
        target_dir = Path(cwd).resolve() if cwd else Path.cwd()
        return target_dir.name or "repository"

    res = _run_git_command(["rev-parse", "--show-toplevel"], cwd=cwd)
    if res.returncode == 0 and res.stdout.strip():
        top_dir = Path(res.stdout.strip()).resolve()
        return top_dir.name

    target_dir = Path(cwd).resolve() if cwd else Path.cwd()
    return target_dir.name or "repository"


def get_staged_diff(cwd: Optional[Path | str] = None) -> str:
    if not is_git_repository(cwd):
        raise NotAGitRepositoryError("Not a Git repository.")

    res = _run_git_command(["diff", "--cached"], cwd=cwd)
    if res.returncode != 0:
        raise GitError(f"Failed to get staged diff: {res.stderr.strip()}")
    return res.stdout.strip()


def get_staged_changed_files(cwd: Optional[Path | str] = None) -> List[ChangedFile]:
    if not is_git_repository(cwd):
        raise NotAGitRepositoryError("Not a Git repository.")

    res = _run_git_command(["diff", "--cached", "--name-status"], cwd=cwd)
    if res.returncode != 0:
        return []

    changed_files: List[ChangedFile] = []
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 3:
            raw_status = parts[0].strip()
            status_code = raw_status[0].upper() if raw_status else "M"
            old_path = parts[1].strip()
            new_path = parts[2].strip()
            changed_files.append(ChangedFile(path=new_path, status=status_code, old_path=old_path))
        elif len(parts) == 2:
            raw_status = parts[0].strip()
            status_code = raw_status[0].upper() if raw_status else "M"
            path = parts[1].strip()
            changed_files.append(ChangedFile(path=path, status=status_code))
    return changed_files


def get_diff_stat(cwd: Optional[Path | str] = None) -> DiffStat:
    if not is_git_repository(cwd):
        raise NotAGitRepositoryError("Not a Git repository.")

    res = _run_git_command(["diff", "--cached", "--shortstat"], cwd=cwd)
    if res.returncode != 0 or not res.stdout.strip():
        return DiffStat()

    text = res.stdout.strip()
    files_changed = 0
    insertions = 0
    deletions = 0

    m_files = re.search(r"(\d+)\s+file", text)
    if m_files:
        files_changed = int(m_files.group(1))

    m_ins = re.search(r"(\d+)\s+insertion", text)
    if m_ins:
        insertions = int(m_ins.group(1))

    m_del = re.search(r"(\d+)\s+deletion", text)
    if m_del:
        deletions = int(m_del.group(1))

    return DiffStat(
        files_changed=files_changed,
        insertions=insertions,
        deletions=deletions,
        summary_text=text,
    )


def get_recent_commits(count: int = 5, cwd: Optional[Path | str] = None) -> List[str]:
    if not is_git_repository(cwd):
        raise NotAGitRepositoryError("Not a Git repository.")

    res = _run_git_command(["log", f"-{count}", "--pretty=format:%s"], cwd=cwd)
    if res.returncode != 0:
        return []
    
    output = res.stdout.strip()
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def get_git_status_short(cwd: Optional[Path | str] = None) -> str:
    if not is_git_repository(cwd):
        raise NotAGitRepositoryError("Not a Git repository.")

    res = _run_git_command(["status", "--short"], cwd=cwd)
    return res.stdout.strip()


def create_commit(message: str, cwd: Optional[Path | str] = None) -> Tuple[bool, str]:
    if not is_git_repository(cwd):
        raise NotAGitRepositoryError("Not a Git repository.")

    clean_message = message.strip()
    if not clean_message:
        raise GitCommitError("Cannot create commit with an empty commit message.")

    res = _run_git_command(["commit", "-m", clean_message], cwd=cwd)
    if res.returncode == 0:
        return True, res.stdout.strip()
    return False, res.stderr.strip() or res.stdout.strip()


def get_remotes(cwd: Optional[Path | str] = None) -> List[str]:
    if not is_git_repository(cwd):
        raise NotAGitRepositoryError("Not a Git repository.")

    res = _run_git_command(["remote"], cwd=cwd)
    if res.returncode != 0:
        return []
    output = res.stdout.strip()
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def get_default_remote(cwd: Optional[Path | str] = None) -> Optional[str]:
    remotes = get_remotes(cwd=cwd)
    if "origin" in remotes:
        return "origin"
    return None


def get_current_branch(cwd: Optional[Path | str] = None) -> Optional[str]:
    if not is_git_repository(cwd):
        raise NotAGitRepositoryError("Not a Git repository.")

    res = _run_git_command(["branch", "--show-current"], cwd=cwd)
    if res.returncode == 0 and res.stdout.strip():
        return res.stdout.strip()

    res_head = _run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
    if res_head.returncode == 0:
        out = res_head.stdout.strip()
        if out and out != "HEAD":
            return out

    res_sha = _run_git_command(["rev-parse", "--short", "HEAD"], cwd=cwd)
    if res_sha.returncode == 0 and res_sha.stdout.strip():
        return f"HEAD (detached at {res_sha.stdout.strip()})"

    return "HEAD (detached)"


def push_commit(remote: str, branch: str, cwd: Optional[Path | str] = None) -> Tuple[bool, str]:
    if not is_git_repository(cwd):
        raise NotAGitRepositoryError("Not a Git repository.")

    res = _run_git_command(["push", remote, branch], cwd=cwd)
    if res.returncode == 0:
        return True, res.stdout.strip() or f"Pushed to {remote}/{branch}"

    err = res.stderr.strip() or res.stdout.strip()
    err_lower = err.lower()

    if "rejected" in err_lower and ("fetch first" in err_lower or "behind" in err_lower or "non-fast-forward" in err_lower):
        clean_err = "The remote rejected the push because the branch is behind the remote."
    elif "permission denied" in err_lower or "authentication failed" in err_lower or "invalid username or password" in err_lower or "403" in err_lower or "401" in err_lower:
        clean_err = "Authentication failed for the remote repository."
    elif "could not resolve host" in err_lower or "connection refused" in err_lower or "fatal: unable to access" in err_lower:
        clean_err = "Could not connect to the remote repository. Please check your network connection."
    elif "src refspec" in err_lower or "does not match any" in err_lower:
        clean_err = f"Branch '{branch}' does not exist locally."
    elif "no upstream" in err_lower or "set-upstream" in err_lower:
        clean_err = f"No upstream branch configured for '{branch}'."
    else:
        first_line = err.splitlines()[0] if err.splitlines() else "Git push failed."
        clean_err = first_line

    return False, clean_err


def get_commit_context(cwd: Optional[Path | str] = None, recent_commit_count: int = 5) -> CommitContext:
    if not is_git_repository(cwd):
        raise NotAGitRepositoryError("Not a Git repository.")

    repo_name = get_repository_name(cwd=cwd)
    branch = get_current_branch(cwd=cwd) or "HEAD (detached)"
    changed_files = get_staged_changed_files(cwd=cwd)
    diff_stat = get_diff_stat(cwd=cwd)
    recent_commits = get_recent_commits(count=recent_commit_count, cwd=cwd)
    staged_diff = get_staged_diff(cwd=cwd)

    return CommitContext(
        repository_name=repo_name,
        current_branch=branch,
        changed_files=changed_files,
        recent_commits=recent_commits,
        diff_stat=diff_stat,
        staged_diff=staged_diff,
    )
