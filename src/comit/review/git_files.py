from __future__ import annotations

from pathlib import Path
from typing import List

from comit.commit.context import CommitContext
from comit.review.base import BaseAnalyzer
from comit.review.models import ReviewFinding, ReviewSeverity


class GitFileAnalyzer(BaseAnalyzer):
    def analyze(self, context: CommitContext) -> List[ReviewFinding]:
        findings: List[ReviewFinding] = []

        for f in context.changed_files:
            if f.status == "D":
                continue

            path_obj = Path(f.path)
            parts = [p.lower() for p in path_obj.parts]
            name = path_obj.name.lower()

            if name == ".git-credentials":
                findings.append(
                    ReviewFinding(
                        severity=ReviewSeverity.HIGH,
                        category="Git Internal File",
                        message="Sensitive Git credentials file staged",
                        file_path=f.path,
                        details="Git credentials files contain plaintext passwords or tokens.",
                    )
                )
            elif name == ".gitconfig":
                findings.append(
                    ReviewFinding(
                        severity=ReviewSeverity.WARNING,
                        category="Git Internal File",
                        message="Git configuration file staged",
                        file_path=f.path,
                        details="Local or global Git configuration should usually not be committed to repositories.",
                    )
                )
            elif ".git" in parts:
                findings.append(
                    ReviewFinding(
                        severity=ReviewSeverity.WARNING,
                        category="Git Internal File",
                        message="Git internal repository directory staged",
                        file_path=f.path,
                        details="Files inside .git/ must not be tracked in repository trees.",
                    )
                )

        return findings
