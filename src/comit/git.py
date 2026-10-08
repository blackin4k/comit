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

    return None


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

