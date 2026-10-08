from __future__ import annotations

from typing import List

from comit.commit.context import CommitContext
from comit.git import get_staged_file_size
from comit.review.base import BaseAnalyzer
from comit.review.models import ReviewFinding, ReviewSeverity

DEFAULT_MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


class LargeFileAnalyzer(BaseAnalyzer):
    def __init__(self, max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES):
        self.max_size_bytes = max_size_bytes

    def analyze(self, context: CommitContext) -> List[ReviewFinding]:
        findings: List[ReviewFinding] = []

        for f in context.changed_files:
            if f.status == "D":
                continue

            size = get_staged_file_size(f.path)
            if size > self.max_size_bytes:
                size_mb = size / (1024 * 1024)
                threshold_mb = self.max_size_bytes / (1024 * 1024)
                findings.append(
                    ReviewFinding(
                        severity=ReviewSeverity.WARNING,
                        category="Large File",
                        message="Large file staged",
                        file_path=f.path,
                        details=f"File size is {size_mb:.1f} MB (threshold: {threshold_mb:.1f} MB). Consider Git LFS or excluding it.",
                    )
                )

        return findings
