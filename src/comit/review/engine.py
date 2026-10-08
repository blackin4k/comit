from __future__ import annotations

from typing import List, Optional

from comit.commit.context import CommitContext
from comit.review.base import BaseAnalyzer
from comit.review.databases import DatabaseAnalyzer
from comit.review.generated_files import GeneratedFileAnalyzer
from comit.review.git_files import GitFileAnalyzer
from comit.review.large_files import LargeFileAnalyzer
from comit.review.models import ReviewFinding, ReviewResult
from comit.review.private_keys import PrivateKeyAnalyzer
from comit.review.secrets import SecretAnalyzer
from comit.review.sensitive_files import SensitiveFileAnalyzer


class ReviewEngine:
    def __init__(self, analyzers: Optional[List[BaseAnalyzer]] = None):
        if analyzers is not None:
            self.analyzers = analyzers
        else:
            self.analyzers = [
                SensitiveFileAnalyzer(),
                SecretAnalyzer(),
                PrivateKeyAnalyzer(),
                DatabaseAnalyzer(),
                LargeFileAnalyzer(),
                GeneratedFileAnalyzer(),
                GitFileAnalyzer(),
            ]

    def run(self, context: CommitContext) -> ReviewResult:
        all_findings: List[ReviewFinding] = []

        for analyzer in self.analyzers:
            findings = analyzer.analyze(context)
            all_findings.extend(findings)

        # Sort findings by severity (HIGH first, then WARNING, then INFO)
        all_findings.sort(key=lambda f: (-f.severity.rank, f.file_path, f.category))

        added_count = sum(1 for f in context.changed_files if f.status == "A")
        modified_count = sum(1 for f in context.changed_files if f.status == "M")
        deleted_count = sum(1 for f in context.changed_files if f.status == "D")
        renamed_count = sum(1 for f in context.changed_files if f.status == "R")

        return ReviewResult(
            findings=all_findings,
            files_checked=len(context.changed_files),
            diff_stat=context.diff_stat,
            added_files_count=added_count,
            modified_files_count=modified_count,
            deleted_files_count=deleted_count,
            renamed_files_count=renamed_count,
        )


def review_changes(context: CommitContext, engine: Optional[ReviewEngine] = None) -> ReviewResult:
    if engine is None:
        engine = ReviewEngine()
    return engine.run(context)
