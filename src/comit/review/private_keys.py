from __future__ import annotations

from typing import List, Tuple

from comit.commit.context import CommitContext
from comit.review.base import BaseAnalyzer
from comit.review.models import ReviewFinding, ReviewSeverity

KEY_MARKERS = [
    "-----BEGIN PRIVATE KEY-----",
    "-----BEGIN RSA PRIVATE KEY-----",
    "-----BEGIN EC PRIVATE KEY-----",
    "-----BEGIN OPENSSH PRIVATE KEY-----",
    "-----BEGIN DSA PRIVATE KEY-----",
    "-----BEGIN PGP PRIVATE KEY BLOCK-----",
]


class PrivateKeyAnalyzer(BaseAnalyzer):
    def analyze(self, context: CommitContext) -> List[ReviewFinding]:
        findings: List[ReviewFinding] = []
        if not context.staged_diff:
            return findings

        added_lines = self._extract_added_lines(context.staged_diff)
        flagged_files = set()

        for file_path, line in added_lines:
            if file_path in flagged_files:
                continue

            for marker in KEY_MARKERS:
                if marker in line:
                    findings.append(
                        ReviewFinding(
                            severity=ReviewSeverity.HIGH,
                            category="Private Key",
                            message="Private key detected in staged changes",
                            file_path=file_path,
                            details="PEM private key header found in added lines.",
                        )
                    )
                    flagged_files.add(file_path)
                    break

        return findings

    def _extract_added_lines(self, diff: str) -> List[Tuple[str, str]]:
        results: List[Tuple[str, str]] = []
        current_file = "unknown"

        for raw_line in diff.splitlines():
            if raw_line.startswith("diff --git "):
                parts = raw_line.split()
                if len(parts) >= 4 and parts[3].startswith("b/"):
                    current_file = parts[3][2:]
                elif len(parts) >= 3 and parts[2].startswith("a/"):
                    current_file = parts[2][2:]
                continue
            elif raw_line.startswith("+++ b/"):
                current_file = raw_line[6:].strip()
                continue
            elif raw_line.startswith("+++ "):
                continue

            if raw_line.startswith("+") and not raw_line.startswith("+++"):
                results.append((current_file, raw_line[1:]))

        return results
