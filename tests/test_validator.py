from __future__ import annotations

import pytest
from comit.commit.context import CommitContext, ChangedFile, DiffStat
from comit.commit.validator import (
    CommitValidator,
    ValidationSeverity,
    ValidationFinding,
    ValidationResult,
    validate_commit_message,
)


def test_empty_commit_message():
    res = validate_commit_message("")
    assert not res.is_valid
    assert res.has_errors
    assert any(f.category == "syntax" and "empty" in f.message for f in res.findings)


def test_whitespace_only_commit_message():
    res = validate_commit_message("   \n\t  ")
    assert not res.is_valid
    assert res.has_errors


def test_valid_conventional_commit():
    res = validate_commit_message("feat: add user authentication")
    assert res.is_valid
    assert not res.has_errors
    assert not res.has_warnings


def test_valid_conventional_commit_with_scope():
    res = validate_commit_message("feat(auth): add JWT token refresh")
    assert res.is_valid
    assert not res.has_errors
    assert not res.has_warnings


def test_valid_conventional_commit_breaking_change():
    res = validate_commit_message("feat!: change configuration format")
    assert res.is_valid
    assert not res.has_errors
    assert not res.has_warnings


def test_valid_conventional_commit_scope_and_breaking():
    res = validate_commit_message("fix(api)!: remove deprecated v1 endpoints")
    assert res.is_valid
    assert not res.has_errors
    assert not res.has_warnings


def test_missing_subject_description():
    res = validate_commit_message("feat:")
    assert not res.is_valid
    assert res.has_errors
    assert any("missing a subject" in f.message for f in res.findings)


def test_non_conventional_commit_format():
    res = validate_commit_message("updated some files and fixed a bug")
    assert res.is_valid
    assert not res.has_errors
    assert any(f.severity == ValidationSeverity.INFO for f in res.findings)


def test_custom_allowed_types():
    validator = CommitValidator(allowed_types={"release", "hotfix"})
    res = validator.validate("hotfix: patch security vulnerability")
    assert res.is_valid
    assert not res.has_errors
    assert not res.has_warnings


def test_doc_only_mismatch_with_feat():
    ctx = CommitContext(
        repository_name="test-repo",
        current_branch="main",
        changed_files=[
            ChangedFile(path="README.md", status="M"),
            ChangedFile(path="docs/guide.rst", status="M"),
        ],
    )
    res = validate_commit_message("feat: implement oauth2 login flow", context=ctx)
    assert res.has_warnings
    assert any("documentation-only" in f.message for f in res.findings)


def test_doc_only_clean_with_docs_type():
    ctx = CommitContext(
        repository_name="test-repo",
        current_branch="main",
        changed_files=[
            ChangedFile(path="README.md", status="M"),
            ChangedFile(path="docs/guide.rst", status="M"),
        ],
    )
    res = validate_commit_message("docs: update installation guide", context=ctx)
    assert not res.has_warnings


def test_docs_type_with_no_doc_files():
    ctx = CommitContext(
        repository_name="test-repo",
        current_branch="main",
        changed_files=[
            ChangedFile(path="src/main.py", status="M"),
            ChangedFile(path="src/auth.py", status="M"),
        ],
    )
    res = validate_commit_message("docs: update api documentation", context=ctx)
    assert res.has_warnings
    assert any("no documentation files are staged" in f.message for f in res.findings)


def test_test_only_mismatch_with_feat():
    ctx = CommitContext(
        repository_name="test-repo",
        current_branch="main",
        changed_files=[
            ChangedFile(path="tests/test_auth.py", status="M"),
            ChangedFile(path="tests/unit/test_cli.py", status="A"),
        ],
    )
    res = validate_commit_message("feat: implement user registration", context=ctx)
    assert res.has_warnings
    assert any("test-only" in f.message for f in res.findings)


def test_test_only_clean_with_test_type():
    ctx = CommitContext(
        repository_name="test-repo",
        current_branch="main",
        changed_files=[
            ChangedFile(path="tests/test_auth.py", status="M"),
        ],
    )
    res = validate_commit_message("test: add edge case test for auth", context=ctx)
    assert not res.has_warnings


def test_test_type_with_no_test_files():
    ctx = CommitContext(
        repository_name="test-repo",
        current_branch="main",
        changed_files=[
            ChangedFile(path="src/app.py", status="M"),
        ],
    )
    res = validate_commit_message("test: verify database connections", context=ctx)
    assert res.has_warnings
    assert any("no test files are staged" in f.message for f in res.findings)


def test_referenced_absent_file():
    ctx = CommitContext(
        repository_name="test-repo",
        current_branch="main",
        changed_files=[
            ChangedFile(path="README.md", status="M"),
        ],
    )
    res = validate_commit_message("fix: update src/config.py and auth.py", context=ctx)
    assert res.has_warnings
    assert any("src/config.py" in f.message or "auth.py" in f.message for f in res.findings)


def test_referenced_staged_file_no_false_positive():
    ctx = CommitContext(
        repository_name="test-repo",
        current_branch="main",
        changed_files=[
            ChangedFile(path="src/config.py", status="M"),
        ],
    )
    res = validate_commit_message("fix: update src/config.py options", context=ctx)
    assert not res.has_warnings


def test_multiple_validation_findings():
    ctx = CommitContext(
        repository_name="test-repo",
        current_branch="main",
        changed_files=[
            ChangedFile(path="README.md", status="M"),
        ],
    )
    res = validate_commit_message("feat: update database.py for user models", context=ctx)
    assert res.has_warnings
    assert len(res.findings) >= 2
    categories = [f.category for f in res.findings]
    assert "context_mismatch" in categories
    assert "file_mismatch" in categories


def test_mixed_staged_changes_normal_feat():
    ctx = CommitContext(
        repository_name="test-repo",
        current_branch="main",
        changed_files=[
            ChangedFile(path="src/auth.py", status="M"),
            ChangedFile(path="tests/test_auth.py", status="M"),
            ChangedFile(path="README.md", status="M"),
        ],
    )
    res = validate_commit_message("feat(auth): add OAuth2 provider support", context=ctx)
    assert not res.has_warnings
