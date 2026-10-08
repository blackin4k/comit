from __future__ import annotations

import re
from typing import List, Tuple, Optional

from comit.commit.context import CommitContext
from comit.review.base import BaseAnalyzer
from comit.review.models import ReviewFinding, ReviewSeverity

SPECIFIC_SECRET_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    ("AWS Access Key ID", re.compile(r"\b(AKIA[0-9A-Z]{16})\b")),
    ("OpenAI API Key", re.compile(r"\b(sk-(?:proj-)?[a-zA-Z0-9_-]{20,})\b")),
    ("Groq API Key", re.compile(r"\b(gsk_[a-zA-Z0-9]{20,})\b")),
    ("Google API Key", re.compile(r"\b(AIza[0-9A-Za-z_-]{30,})\b")),
    ("GitHub Personal Access Token", re.compile(r"\b(gh[pousr]_[a-zA-Z0-9]{36})\b")),
    ("GitHub Fine-Grained Token", re.compile(r"\b(github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59})\b")),
]

GENERIC_ASSIGNMENT_PATTERN = re.compile(
    r"""(?i)\b(?:api_key|apikey|secret_key|secret|auth_token|access_token|client_secret|db_password|password|passwd)\s*[:=]\s*["']([^"'\s]{8,})["']"""
)

IGNORE_VALUE_SUBSTRINGS = {
    "dummy",
    "mock",
    "sample",
    "example",
    "placeholder",
    "changeme",
    "your_",
    "<your",
    "********",
    "xxxxxx",
}

EXACT_IGNORE_VALUES = {
    "password",
    "password123",
    "admin",
    "secret",
    "12345678",
    "true",
    "false",
    "none",
    "null",
    "undefined",
}


def mask_secret(value: str) -> str:
    if len(value) <= 8:
        return "****"
    return f"{value[:3]}...{value[-3:]}"


class SecretAnalyzer(BaseAnalyzer):
    def analyze(self, context: CommitContext) -> List[ReviewFinding]:
        findings: List[ReviewFinding] = []
        if not context.staged_diff:
            return findings

        added_lines = self._extract_added_lines(context.staged_diff)

        for file_path, line in added_lines:
            finding = self._check_line_for_secrets(file_path, line)
            if finding:
                findings.append(finding)

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
                added_content = raw_line[1:]
                results.append((current_file, added_content))

        return results

    def _check_line_for_secrets(self, file_path: str, line: str) -> Optional[ReviewFinding]:
        for name, pattern in SPECIFIC_SECRET_PATTERNS:
            match = pattern.search(line)
            if match:
                masked = mask_secret(match.group(1))
                return ReviewFinding(
                    severity=ReviewSeverity.HIGH,
                    category="Secret",
                    message="Possible hardcoded secret or API key detected",
                    file_path=file_path,
                    details=f"Pattern: {name} ({masked})",
                )

        generic_match = GENERIC_ASSIGNMENT_PATTERN.search(line)
        if generic_match:
            value = generic_match.group(1)
            val_lower = value.lower()

            if val_lower in EXACT_IGNORE_VALUES:
                return None

            if any(ign in val_lower for ign in IGNORE_VALUE_SUBSTRINGS):
                return None

            masked = mask_secret(value)
            return ReviewFinding(
                severity=ReviewSeverity.HIGH,
                category="Secret",
                message="Possible hardcoded secret or credential assignment detected",
                file_path=file_path,
                details=f"Literal credential value detected ({masked})",
            )

        return None
