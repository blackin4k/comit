from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Set

from comit.commit.context import CommitContext, ChangedFile


class ValidationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class ValidationFinding:
    severity: ValidationSeverity
    category: str
    message: str
    details: Optional[str] = None


@dataclass
class ValidationResult:
    message: str
    is_valid: bool = True
    findings: List[ValidationFinding] = field(default_factory=list)

    @property
    def has_findings(self) -> bool:
        return bool(self.findings)

    @property
    def has_warnings(self) -> bool:
        return any(f.severity in (ValidationSeverity.WARNING, ValidationSeverity.ERROR) for f in self.findings)

    @property
    def has_errors(self) -> bool:
        return any(f.severity == ValidationSeverity.ERROR for f in self.findings)


DEFAULT_CONVENTIONAL_TYPES = {
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "build",
    "ci",
    "chore",
    "revert",
}

DOC_EXTENSIONS = {
    ".md",
    ".markdown",
    ".mdown",
    ".rst",
    ".txt",
    ".adoc",
    ".asciidoc",
    ".doc",
    ".docx",
    ".pdf",
}

DOC_FILENAMES = {
    "readme",
    "license",
    "contributing",
    "changelog",
    "authors",
    "code_of_conduct",
    "notice",
    "todo",
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

CONVENTIONAL_REGEX = re.compile(
    r"^(?P<type>[a-zA-Z0-9_-]+)(?:\((?P<scope>[^()\r\n]+)\))?(?P<breaking>!)?:\s*(?P<subject>.*)$"
)

FILE_PATH_PATTERN = re.compile(
    r"(?:\b|['\"`])(?P<path>(?:[a-zA-Z0-9_\-\.]+[/\\])+[a-zA-Z0-9_\-\.]+|[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+)(?:\b|['\"`])"
)


def _is_doc_file(path_str: str) -> bool:
    norm_path = path_str.replace("\\", "/").lower()
    path_obj = Path(norm_path)
    if any(part in ("docs", "doc", "documentation") for part in path_obj.parts):
        return True
    if path_obj.suffix.lower() in DOC_EXTENSIONS:
        return True
    if path_obj.stem.lower() in DOC_FILENAMES:
        return True
    return False


def _is_test_file(path_str: str) -> bool:
    norm_path = path_str.replace("\\", "/").lower()
    path_obj = Path(norm_path)
    if any(part in ("tests", "test", "testing", "__tests__", "spec", "specs") for part in path_obj.parts):
        return True
    stem = path_obj.stem.lower()
    name = path_obj.name.lower()
    if stem.startswith("test_") or stem.endswith("_test") or stem.endswith("_spec"):
        return True
    if any(name.endswith(ext) for ext in TEST_EXTENSIONS):
        return True
    return False


def _extract_referenced_files(text: str) -> Set[str]:
    referenced = set()
    for match in FILE_PATH_PATTERN.finditer(text):
        candidate = match.group("path").strip("'\"`")
        if candidate.endswith((".", ",")):
            candidate = candidate[:-1]
        if not candidate:
            continue
        p = Path(candidate)
        suffix = p.suffix.lower()
        if suffix in (
            ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".toml", ".yaml", ".yml",
            ".md", ".rst", ".txt", ".html", ".css", ".rs", ".go", ".c", ".cpp",
            ".h", ".java", ".kt", ".rb", ".php", ".sh", ".bat", ".ps1", ".sql",
            ".env", ".lock", ".cfg", ".ini",
        ) or "/" in candidate or "\\" in candidate:
            referenced.add(candidate.replace("\\", "/").lower())
    return referenced


class CommitValidator:
    def __init__(self, allowed_types: Optional[Set[str]] = None):
        self.allowed_types = set(allowed_types) if allowed_types else DEFAULT_CONVENTIONAL_TYPES

    def validate(self, message: str, context: Optional[CommitContext] = None) -> ValidationResult:
        result = ValidationResult(message=message)

        if not message or not message.strip():
            result.is_valid = False
            result.findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.ERROR,
                    category="syntax",
                    message="Commit message is empty.",
                )
            )
            return result

        lines = message.strip().splitlines()
        first_line = lines[0].strip()

        match = CONVENTIONAL_REGEX.match(first_line)
        msg_type: Optional[str] = None
        msg_scope: Optional[str] = None
        msg_subject: Optional[str] = None

        if match:
            msg_type = match.group("type").lower()
            msg_scope = match.group("scope")
            msg_subject = match.group("subject").strip()

            if not msg_subject:
                result.is_valid = False
                result.findings.append(
                    ValidationFinding(
                        severity=ValidationSeverity.ERROR,
                        category="syntax",
                        message=f"Commit message type '{msg_type}' is missing a subject description.",
                    )
                )
        else:
            result.findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.INFO,
                    category="syntax",
                    message="Commit message does not follow Conventional Commit format (type: description).",
                )
            )

        if context and context.changed_files:
            staged_paths = [f.path.replace("\\", "/").lower() for f in context.changed_files]
            staged_basenames = [Path(p).name.lower() for p in staged_paths]

            is_all_docs = all(_is_doc_file(p) for p in staged_paths)
            is_all_tests = all(_is_test_file(p) for p in staged_paths)
            has_any_docs = any(_is_doc_file(p) for p in staged_paths)
            has_any_tests = any(_is_test_file(p) for p in staged_paths)

            if msg_type:
                if is_all_docs and msg_type in ("feat", "fix", "perf", "refactor"):
                    result.findings.append(
                        ValidationFinding(
                            severity=ValidationSeverity.WARNING,
                            category="context_mismatch",
                            message=f"Commit message type '{msg_type}' does not match documentation-only staged changes.",
                            details=f"All {len(staged_paths)} staged file(s) are documentation files.",
                        )
                    )
                elif msg_type == "docs" and not has_any_docs:
                    result.findings.append(
                        ValidationFinding(
                            severity=ValidationSeverity.WARNING,
                            category="context_mismatch",
                            message="Commit message type is 'docs' but no documentation files are staged.",
                        )
                    )

                if is_all_tests and msg_type in ("feat", "fix", "perf"):
                    result.findings.append(
                        ValidationFinding(
                            severity=ValidationSeverity.WARNING,
                            category="context_mismatch",
                            message=f"Commit message type '{msg_type}' does not match test-only staged changes.",
                            details=f"All {len(staged_paths)} staged file(s) are test files.",
                        )
                    )
                elif msg_type == "test" and not has_any_tests:
                    result.findings.append(
                        ValidationFinding(
                            severity=ValidationSeverity.WARNING,
                            category="context_mismatch",
                            message="Commit message type is 'test' but no test files are staged.",
                        )
                    )

            referenced_files = _extract_referenced_files(message)
            for ref in referenced_files:
                ref_basename = Path(ref).name.lower()
                matches_staged = any(
                    ref == staged_p or staged_p.endswith(f"/{ref}") or ref_basename == base
                    for staged_p, base in zip(staged_paths, staged_basenames)
                )
                if not matches_staged:
                    result.findings.append(
                        ValidationFinding(
                            severity=ValidationSeverity.WARNING,
                            category="file_mismatch",
                            message=f"Commit message references '{ref}' which is not in staged changes.",
                        )
                    )

        return result


def validate_commit_message(
    message: str,
    context: Optional[CommitContext] = None,
    allowed_types: Optional[Set[str]] = None,
) -> ValidationResult:
    validator = CommitValidator(allowed_types=allowed_types)
    return validator.validate(message=message, context=context)
