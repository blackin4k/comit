from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from comit.commit.context import DiffStat


class ReviewSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"

    @property
    def rank(self) -> int:
        rank_map = {
            ReviewSeverity.INFO: 1,
            ReviewSeverity.WARNING: 2,
            ReviewSeverity.HIGH: 3,
        }
        return rank_map.get(self, 0)


@dataclass
class ReviewFinding:
    severity: ReviewSeverity
    category: str
    message: str
    file_path: str
    details: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class ReviewResult:
    findings: List[ReviewFinding] = field(default_factory=list)
    files_checked: int = 0
    diff_stat: DiffStat = field(default_factory=DiffStat)
    added_files_count: int = 0
    modified_files_count: int = 0
    deleted_files_count: int = 0
    renamed_files_count: int = 0

    @property
    def has_findings(self) -> bool:
        return bool(self.findings)

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == ReviewSeverity.HIGH)

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == ReviewSeverity.WARNING)

    @property
    def info_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == ReviewSeverity.INFO)
