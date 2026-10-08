from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ChangedFile:
    path: str
    status: str
    old_path: Optional[str] = None

    @property
    def display_status(self) -> str:
        status_map = {
            "A": "Added",
            "M": "Modified",
            "D": "Deleted",
            "R": "Renamed",
            "C": "Copied",
            "T": "Type changed",
            "U": "Unmerged",
        }
        return status_map.get(self.status, self.status)

    def format_line(self) -> str:
        if self.old_path:
            return f"  {self.status} {self.old_path} -> {self.path}"
        return f"  {self.status} {self.path}"


@dataclass
class DiffStat:
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0
    summary_text: str = ""

    def format_summary(self) -> str:
        if self.summary_text:
            return self.summary_text
        parts = []
        if self.files_changed:
            parts.append(f"{self.files_changed} file{'s' if self.files_changed != 1 else ''} changed")
        if self.insertions:
            parts.append(f"{self.insertions} insertion{'(+)' if self.insertions == 1 else 's(+)'}")
        if self.deletions:
            parts.append(f"{self.deletions} deletion{'(-)' if self.deletions == 1 else 's(-)'}")
        return ", ".join(parts) if parts else "0 files changed"


@dataclass
class CommitContext:
    repository_name: str
    current_branch: str
    changed_files: List[ChangedFile] = field(default_factory=list)
    recent_commits: List[str] = field(default_factory=list)
    diff_stat: DiffStat = field(default_factory=DiffStat)
    staged_diff: str = ""

