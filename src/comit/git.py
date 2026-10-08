from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple


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


def get_staged_diff(cwd: Optional[Path | str] = None) -> str:
    if not is_git_repository(cwd):
        raise NotAGitRepositoryError("Not a Git repository.")

    res = _run_git_command(["diff", "--cached"], cwd=cwd)
    if res.returncode != 0:
        raise GitError(f"Failed to get staged diff: {res.stderr.strip()}")
    return res.stdout.strip()


def get_recent_commits(count: int = 15, cwd: Optional[Path | str] = None) -> List[str]:
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
