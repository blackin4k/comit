from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple, Optional, Set

from comit.commit.context import CommitContext
from comit.review.base import BaseAnalyzer
from comit.review.models import ReviewFinding, ReviewSeverity

SPECIFIC_SECRET_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    ("AWS Access Key ID", re.compile(r"\b(AKIA[0-9A-Z]{16})\b")),
    ("OpenAI API Key", re.compile(r"\b(sk-(?:proj-)?[a-zA-Z0-9_-]{20,})\b")),
    ("Groq API Key", re.compile(r"\b(gsk_[a-zA-Z0-9_-]{20,})\b")),
    ("Google API Key", re.compile(r"\b(AIza[0-9A-Za-z_-]{30,})\b")),
    ("GitHub Personal Access Token", re.compile(r"\b(gh[pousr]_[a-zA-Z0-9]{36})\b")),
    ("GitHub Fine-Grained Token", re.compile(r"\b(github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59})\b")),
]

GENERIC_ASSIGNMENT_PATTERN = re.compile(
    r"""(?i)\b(?:api_key|apikey|secret_key|secret|auth_token|access_token|client_secret|db_password|password|passwd)\s*[:=]\s*["']([^"'\s]{8,})["']"""
)

KNOWN_TEST_DIRS = {
    "tests",
    "test",
    "testing",
    "__tests__",
    "fixtures",
    "fixture",
    "testdata",
    "mocks",
}

TEST_EXTENSIONS = {
    ".spec.js",
    ".spec.ts",
    ".spec.jsx",
    ".spec.tsx",
    ".test.js",
    ".test.ts",
    ".test.jsx",
    ".test.tsx",
    ".test.py",
}

EXACT_IGNORE_VALUES: Set[str] = {
    "password",
    "password123",
    "admin",
    "secret",
    "12345678",
    "1234567890",
    "true",
    "false",
    "none",
    "null",
    "undefined",
    "your_api_key",
    "your-api-key",
    "example-token",
    "fake-secret",
    "test-secret-placeholder",
}

PLACEHOLDER_SUBSTRINGS = (
    "dummy",
    "mock",
    "sample",
    "example",
    "placeholder",
    "changeme",
    "your_",
    "your-",
    "<your",
    "[your",
    "fake-",
    "fake_",
    "test-",
    "test_",
    "********",
    "xxxxxx",
)


def is_test_or_fixture_path(file_path: str) -> bool:
    norm = file_path.replace("\\", "/").lower()
    p = Path(norm)
    parts = set(p.parts)
    if any(part in KNOWN_TEST_DIRS for part in parts):
        return True
    stem = p.stem.lower()
    name = p.name.lower()
    if stem.startswith("test_") or stem.endswith("_test") or stem.endswith("_fixture") or stem.endswith("_mock"):
        return True
    if any(name.endswith(ext) for ext in TEST_EXTENSIONS):
        return True
    return False


def is_clear_placeholder(value: str) -> bool:
    val_lower = value.strip().lower()
    if val_lower in EXACT_IGNORE_VALUES:
        return True
    if val_lower.startswith(("your_", "your-", "fake-", "fake_", "test-", "test_", "example-", "example_", "mock-", "mock_", "dummy-", "dummy_")):
        return True
    if any(sub in val_lower for sub in PLACEHOLDER_SUBSTRINGS):
        return True
    if val_lower == "akiaiosfodnn7example":
        return True
    return False


def mask_secret(value: str) -> str:
    if len(value) <= 8:
        return "********"
    return f"{value[:3]}...{value[-3:]}"


class SecretAnalyzer(BaseAnalyzer):
    def analyze(self, context: CommitContext) -> List[ReviewFinding]:
        findings: List[ReviewFinding] = []
        if not context.staged_diff:
            return findings

        added_lines = self._extract_added_lines(context.staged_diff)

        for file_path, line, line_num in added_lines:
            finding = self._check_line_for_secrets(file_path, line, line_num)
            if finding:
                findings.append(finding)

        return findings

    def _extract_added_lines(self, diff: str) -> List[Tuple[str, str, Optional[int]]]:
        results: List[Tuple[str, str, Optional[int]]] = []
        current_file = "unknown"
        current_line_num: Optional[int] = None

        for raw_line in diff.splitlines():
            if raw_line.startswith("diff --git "):
                parts = raw_line.split()
                if len(parts) >= 4 and parts[3].startswith("b/"):
                    current_file = parts[3][2:]
                elif len(parts) >= 3 and parts[2].startswith("a/"):
                    current_file = parts[2][2:]
                current_line_num = None
                continue
            elif raw_line.startswith("+++ b/"):
                current_file = raw_line[6:].strip()
                current_line_num = None
                continue
            elif raw_line.startswith("+++ "):
                continue
            elif raw_line.startswith("@@ "):
                match = re.search(r"\+(\d+)", raw_line)
                if match:
                    current_line_num = int(match.group(1))
                continue

            if raw_line.startswith("+") and not raw_line.startswith("+++"):
                added_content = raw_line[1:]
                results.append((current_file, added_content, current_line_num))
                if current_line_num is not None:
                    current_line_num += 1
            elif not raw_line.startswith("-") and current_line_num is not None:
                current_line_num += 1

        return results

    def _check_line_for_secrets(
        self, file_path: str, line: str, line_number: Optional[int] = None
    ) -> Optional[ReviewFinding]:
        is_test = is_test_or_fixture_path(file_path)

        for name, pattern in SPECIFIC_SECRET_PATTERNS:
            match = pattern.search(line)
            if match:
                matched_val = match.group(1)
                masked = mask_secret(matched_val)

                if is_clear_placeholder(matched_val):
                    if is_test:
                        return ReviewFinding(
                            severity=ReviewSeverity.INFO,
                            category="Secret",
                            message="Test fixture or mock credential detected",
                            file_path=file_path,
                            details=f"Pattern: {name} (mock/placeholder)",
                            line_number=line_number,
                        )
                    return None

                return ReviewFinding(
                    severity=ReviewSeverity.HIGH,
                    category="Secret",
                    message="Possible hardcoded secret or API key detected",
                    file_path=file_path,
                    details=f"Pattern: {name} ({masked})",
                    line_number=line_number,
                )

        generic_match = GENERIC_ASSIGNMENT_PATTERN.search(line)
        if generic_match:
            value = generic_match.group(1)

            if is_clear_placeholder(value):
                if is_test:
                    return ReviewFinding(
                        severity=ReviewSeverity.INFO,
                        category="Secret",
                        message="Test fixture or mock credential assignment detected",
                        file_path=file_path,
                        details="Literal test placeholder value detected",
                        line_number=line_number,
                    )
                return None

            masked = mask_secret(value)
            severity = ReviewSeverity.WARNING if is_test else ReviewSeverity.HIGH
            return ReviewFinding(
                severity=severity,
                category="Secret",
                message="Possible hardcoded secret or credential assignment detected",
                file_path=file_path,
                details=f"Literal credential value detected ({masked})",
                line_number=line_number,
            )

        return None
