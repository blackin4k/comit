from __future__ import annotations

from pathlib import Path
from typing import List

from comit.commit.context import CommitContext
from comit.review.base import BaseAnalyzer
from comit.review.models import ReviewFinding, ReviewSeverity

GENERATED_DIR_NAMES = {
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "htmlcov",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
}

GENERATED_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
}

GENERATED_FILE_NAMES = {
    ".coverage",
}


class GeneratedFileAnalyzer(BaseAnalyzer):
    def analyze(self, context: CommitContext) -> List[ReviewFinding]:
        findings: List[ReviewFinding] = []

        for f in context.changed_files:
            if f.status == "D":
                continue

            path_obj = Path(f.path)
            parts = [p.lower() for p in path_obj.parts]
            name = path_obj.name.lower()
            suffix = path_obj.suffix.lower()

            is_generated = False
            matched_reason = ""

            for part in parts[:-1]:
                if part in GENERATED_DIR_NAMES:
                    is_generated = True
                    matched_reason = f"Located inside '{part}' directory"
                    break

            if not is_generated:
                if name in GENERATED_FILE_NAMES:
                    is_generated = True
                    matched_reason = f"Artifact '{name}'"
                elif suffix in GENERATED_EXTENSIONS:
                    is_generated = True
                    matched_reason = f"Compiled artifact ('{suffix}')"

            if is_generated:
                findings.append(
                    ReviewFinding(
                        severity=ReviewSeverity.INFO,
                        category="Generated Artifact",
                        message="Generated build or cache artifact staged",
                        file_path=f.path,
                        details=f"{matched_reason}. Consider adding it to .gitignore.",
                    )
                )

        return findings
