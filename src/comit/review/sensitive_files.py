from __future__ import annotations

from pathlib import Path
from typing import List

from comit.commit.context import CommitContext
from comit.review.base import BaseAnalyzer
from comit.review.models import ReviewFinding, ReviewSeverity

EXEMPT_ENV_SUFFIXES = {
    ".example",
    ".sample",
    ".template",
    ".dist",
    ".schema",
    ".defaults",
}

EXEMPT_ENV_FILENAMES = {
    "example.env",
    "sample.env",
    "template.env",
}

SENSITIVE_EXACT_NAMES = {
    "credentials.json",
    "credentials.yaml",
    "credentials.yml",
    "secrets.json",
    "secrets.yaml",
    "secrets.yml",
    "service-account.json",
    "service_account.json",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
}


class SensitiveFileAnalyzer(BaseAnalyzer):
    def analyze(self, context: CommitContext) -> List[ReviewFinding]:
        findings: List[ReviewFinding] = []

        for f in context.changed_files:
            if f.status == "D":
                continue

            name = Path(f.path).name.lower()

            if self._is_sensitive_file(name):
                findings.append(
                    ReviewFinding(
                        severity=ReviewSeverity.WARNING,
                        category="Sensitive File",
                        message="Sensitive environment or credential file staged",
                        file_path=f.path,
                        details="Environment files and credentials should typically not be tracked in version control.",
                    )
                )

        return findings

    def _is_sensitive_file(self, filename: str) -> bool:
        if filename in SENSITIVE_EXACT_NAMES:
            return True

        if filename == ".env":
            return True

        if filename.startswith(".env.") or filename.endswith(".env"):
            if filename in EXEMPT_ENV_FILENAMES:
                return False
            for exempt_suffix in EXEMPT_ENV_SUFFIXES:
                if filename.endswith(exempt_suffix):
                    return False
            return True

        return False
