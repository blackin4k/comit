from __future__ import annotations

from pathlib import Path
from typing import List

from comit.commit.context import CommitContext
from comit.review.base import BaseAnalyzer
from comit.review.models import ReviewFinding, ReviewSeverity

DATABASE_EXTENSIONS = {
    ".db",
    ".sqlite",
    ".sqlite3",
    ".rdb",
    ".mdb",
    ".accdb",
}


class DatabaseAnalyzer(BaseAnalyzer):
    def analyze(self, context: CommitContext) -> List[ReviewFinding]:
        findings: List[ReviewFinding] = []

        for f in context.changed_files:
            if f.status == "D":
                continue

            suffix = Path(f.path).suffix.lower()
            if suffix in DATABASE_EXTENSIONS:
                findings.append(
                    ReviewFinding(
                        severity=ReviewSeverity.WARNING,
                        category="Database File",
                        message="Database file staged",
                        file_path=f.path,
                        details="Binary database files should typically not be tracked in version control.",
                    )
                )

        return findings
