from pathlib import Path
from unittest.mock import patch
import pytest

from comit.commit.context import ChangedFile, CommitContext, DiffStat
from comit.review import (
    DatabaseAnalyzer,
    GeneratedFileAnalyzer,
    GitFileAnalyzer,
    LargeFileAnalyzer,
    PrivateKeyAnalyzer,
    ReviewEngine,
    ReviewFinding,
    ReviewResult,
    ReviewSeverity,
    SecretAnalyzer,
    SensitiveFileAnalyzer,
    review_changes,
)


# 1. SensitiveFileAnalyzer tests
def test_sensitive_file_analyzer_env_files():
    analyzer = SensitiveFileAnalyzer()
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        changed_files=[
            ChangedFile(path=".env", status="A"),
            ChangedFile(path="subfolder/.env.local", status="M"),
            ChangedFile(path="config/production.env", status="A"),
            ChangedFile(path="credentials.json", status="A"),
            ChangedFile(path="api/secrets.yaml", status="M"),
            ChangedFile(path="keys/id_rsa", status="A"),
        ],
    )
    findings = analyzer.analyze(ctx)
    paths = [f.file_path for f in findings]
    assert ".env" in paths
    assert "subfolder/.env.local" in paths
    assert "config/production.env" in paths
    assert "credentials.json" in paths
    assert "api/secrets.yaml" in paths
    assert "keys/id_rsa" in paths
    assert all(f.severity == ReviewSeverity.WARNING for f in findings)


def test_sensitive_file_analyzer_exemptions():
    analyzer = SensitiveFileAnalyzer()
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        changed_files=[
            ChangedFile(path=".env.example", status="A"),
            ChangedFile(path=".env.sample", status="A"),
            ChangedFile(path=".env.template", status="A"),
            ChangedFile(path=".env.dist", status="A"),
            ChangedFile(path="example.env", status="A"),
            ChangedFile(path="sample.env", status="A"),
            ChangedFile(path="settings.py", status="M"),
            ChangedFile(path="config.py", status="M"),
        ],
    )
    findings = analyzer.analyze(ctx)
    assert len(findings) == 0


def test_sensitive_file_analyzer_deleted_ignored():
    analyzer = SensitiveFileAnalyzer()
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        changed_files=[
            ChangedFile(path=".env", status="D"),
            ChangedFile(path="credentials.json", status="D"),
        ],
    )
    findings = analyzer.analyze(ctx)
    assert len(findings) == 0


# 2. SecretAnalyzer tests
def test_secret_analyzer_known_patterns():
    analyzer = SecretAnalyzer()
    diff = """diff --git a/src/keys.py b/src/keys.py
--- a/src/keys.py
+++ b/src/keys.py
@@ -1,3 +1,7 @@
+aws_key = "AKIA1234567890ABCDEF"
+openai_key = "sk-proj-12345678901234567890abcdef"
+groq_key = "gsk_12345678901234567890abcdef"
+google_key = "AIzaSyD1234567890123456789012345678901"
+github_pat = "ghp_123456789012345678901234567890abcdef"
"""
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        staged_diff=diff,
    )
    findings = analyzer.analyze(ctx)
    assert len(findings) >= 5
    assert all(f.severity == ReviewSeverity.HIGH for f in findings)
    assert all(f.category == "Secret" for f in findings)
    # Ensure full secret is not exposed in message or details
    for f in findings:
        assert "AKIA1234567890ABCDEF" not in f.message
        assert "AKIA1234567890ABCDEF" not in (f.details or "")
        assert "gsk_12345678901234567890abcdef" not in f.message


def test_secret_analyzer_generic_literal_assignment():
    analyzer = SecretAnalyzer()
    diff = """diff --git a/config.py b/config.py
--- a/config.py
+++ b/config.py
@@ -1,2 +1,3 @@
+client_secret = "super_secret_production_token_xyz"
+db_password = "MyComplexPassword123!"
"""
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        staged_diff=diff,
    )
    findings = analyzer.analyze(ctx)
    assert len(findings) == 2
    assert all(f.severity == ReviewSeverity.HIGH for f in findings)


def test_secret_analyzer_ignores_property_access_and_placeholders():
    analyzer = SecretAnalyzer()
    diff = """diff --git a/auth.py b/auth.py
--- a/auth.py
+++ b/auth.py
@@ -1,5 +1,8 @@
+password = user.password
+api_key = os.environ.get("API_KEY")
+token = get_auth_token(request)
+api_key = "your_api_key_here"
+secret = "dummy_secret_value"
+is_auth = True
"""
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        staged_diff=diff,
    )
    findings = analyzer.analyze(ctx)
    assert len(findings) == 0


def test_secret_analyzer_ignores_deleted_and_context_lines():
    analyzer = SecretAnalyzer()
    diff = """diff --git a/keys.py b/keys.py
--- a/keys.py
+++ b/keys.py
@@ -1,4 +1,4 @@
 aws_key = "AKIA1234567890ABCDEF"
-openai_key = "sk-12345678901234567890abcdef"
+openai_key = os.environ.get("OPENAI_KEY")
"""
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        staged_diff=diff,
    )
    findings = analyzer.analyze(ctx)
    assert len(findings) == 0


# 3. PrivateKeyAnalyzer tests
def test_private_key_analyzer():
    analyzer = PrivateKeyAnalyzer()
    diff = """diff --git a/cert.pem b/cert.pem
--- a/cert.pem
+++ b/cert.pem
@@ -0,0 +1,5 @@
+-----BEGIN RSA PRIVATE KEY-----
+MIIEowIBAAKCAQEA0Y...
+-----END RSA PRIVATE KEY-----
+-----BEGIN OPENSSH PRIVATE KEY-----
+b3BlbnNzaC...
"""
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        staged_diff=diff,
    )
    findings = analyzer.analyze(ctx)
    assert len(findings) >= 1
    assert findings[0].severity == ReviewSeverity.HIGH
    assert findings[0].category == "Private Key"
    assert "MIIEowIBAAKCAQEA0Y" not in findings[0].message


# 4. DatabaseAnalyzer tests
def test_database_analyzer():
    analyzer = DatabaseAnalyzer()
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        changed_files=[
            ChangedFile(path="data/app.db", status="A"),
            ChangedFile(path="store/production.sqlite3", status="M"),
            ChangedFile(path="dump.sqlite", status="A"),
            ChangedFile(path="old.db", status="D"),
        ],
    )
    findings = analyzer.analyze(ctx)
    paths = [f.file_path for f in findings]
    assert "data/app.db" in paths
    assert "store/production.sqlite3" in paths
    assert "dump.sqlite" in paths
    assert "old.db" not in paths
    assert all(f.severity == ReviewSeverity.WARNING for f in findings)


# 5. LargeFileAnalyzer tests
def test_large_file_analyzer():
    analyzer = LargeFileAnalyzer(max_size_bytes=5 * 1024 * 1024)
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        changed_files=[
            ChangedFile(path="assets/small.png", status="A"),
            ChangedFile(path="assets/large.bin", status="A"),
        ],
    )

    def mock_size(path):
        if "large" in path:
            return 8 * 1024 * 1024
        return 500 * 1024

    with patch("comit.review.large_files.get_staged_file_size", side_effect=mock_size):
        findings = analyzer.analyze(ctx)
        assert len(findings) == 1
        assert findings[0].file_path == "assets/large.bin"
        assert findings[0].severity == ReviewSeverity.WARNING
        assert "8.0 MB" in (findings[0].details or "")


# 6. GeneratedFileAnalyzer tests
def test_generated_file_analyzer():
    analyzer = GeneratedFileAnalyzer()
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        changed_files=[
            ChangedFile(path="src/__pycache__/module.cpython-313.pyc", status="A"),
            ChangedFile(path="dist/package-0.1.0.tar.gz", status="A"),
            ChangedFile(path="build/lib/app.py", status="A"),
            ChangedFile(path="node_modules/lodash/index.js", status="A"),
            ChangedFile(path=".pytest_cache/v/cache/nodeids", status="A"),
            ChangedFile(path="htmlcov/index.html", status="A"),
            ChangedFile(path="src/normal_file.py", status="M"),
        ],
    )
    findings = analyzer.analyze(ctx)
    paths = [f.file_path for f in findings]
    assert "src/__pycache__/module.cpython-313.pyc" in paths
    assert "dist/package-0.1.0.tar.gz" in paths
    assert "build/lib/app.py" in paths
    assert "node_modules/lodash/index.js" in paths
    assert ".pytest_cache/v/cache/nodeids" in paths
    assert "htmlcov/index.html" in paths
    assert "src/normal_file.py" not in paths


# 7. GitFileAnalyzer tests
def test_git_file_analyzer():
    analyzer = GitFileAnalyzer()
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        changed_files=[
            ChangedFile(path=".git-credentials", status="A"),
            ChangedFile(path=".gitconfig", status="A"),
            ChangedFile(path=".git/HEAD", status="A"),
            ChangedFile(path="README.md", status="M"),
        ],
    )
    findings = analyzer.analyze(ctx)
    paths = [f.file_path for f in findings]
    assert ".git-credentials" in paths
    assert ".gitconfig" in paths
    assert ".git/HEAD" in paths
    assert "README.md" not in paths


# 8. ReviewEngine tests
def test_review_engine_clean():
    engine = ReviewEngine()
    ctx = CommitContext(
        repository_name="clean_repo",
        current_branch="main",
        changed_files=[
            ChangedFile(path="src/main.py", status="M"),
            ChangedFile(path="tests/test_main.py", status="A"),
        ],
        diff_stat=DiffStat(files_changed=2, insertions=20, deletions=5),
        staged_diff="diff --git a/src/main.py b/src/main.py\n+def run(): pass",
    )
    result = engine.run(ctx)
    assert isinstance(result, ReviewResult)
    assert not result.has_findings
    assert result.files_checked == 2
    assert result.added_files_count == 1
    assert result.modified_files_count == 1
    assert result.high_count == 0
    assert result.warning_count == 0
    assert result.info_count == 0


def test_review_engine_multiple_findings_sorted():
    engine = ReviewEngine()
    ctx = CommitContext(
        repository_name="dirty_repo",
        current_branch="main",
        changed_files=[
            ChangedFile(path=".env", status="A"),
            ChangedFile(path="src/__pycache__/app.pyc", status="A"),
            ChangedFile(path="app.py", status="M"),
        ],
        diff_stat=DiffStat(files_changed=3, insertions=10, deletions=0),
        staged_diff="diff --git a/app.py b/app.py\n+groq_key = 'gsk_123456789012345678901234'",
    )
    result = engine.run(ctx)
    assert result.has_findings
    assert result.high_count >= 1
    assert result.warning_count >= 1
    assert result.info_count >= 1
    # Check sorting: HIGH comes before WARNING, which comes before INFO
    severities = [f.severity for f in result.findings]
    assert severities[0] == ReviewSeverity.HIGH


# 9. Test-aware secret detection & deduplication tests
def test_secret_analyzer_fake_placeholder_in_test_file():
    analyzer = SecretAnalyzer()
    diff = """diff --git a/tests/test_auth.py b/tests/test_auth.py
--- a/tests/test_auth.py
+++ b/tests/test_auth.py
@@ -1,3 +1,5 @@
+TEST_API_KEY = "test-secret-placeholder"
+MOCK_TOKEN = "example-token"
+DUMMY_KEY = "fake-secret-key-123"
+YOUR_KEY = "YOUR_API_KEY"
"""
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        staged_diff=diff,
    )
    findings = analyzer.analyze(ctx)
    assert all(f.severity == ReviewSeverity.INFO for f in findings) or len(findings) == 0


def test_secret_analyzer_realistic_secret_in_test_file():
    analyzer = SecretAnalyzer()
    diff = """diff --git a/tests/test_auth.py b/tests/test_auth.py
--- a/tests/test_auth.py
+++ b/tests/test_auth.py
@@ -1,2 +1,3 @@
+REAL_GROQ_KEY = "gsk_live_12345678901234567890abcdef"
"""
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        staged_diff=diff,
    )
    findings = analyzer.analyze(ctx)
    assert len(findings) >= 1
    assert any(f.severity in (ReviewSeverity.HIGH, ReviewSeverity.WARNING) for f in findings)
    assert "gsk_live_12345678901234567890abcdef" not in findings[0].message
    assert "gsk_live_12345678901234567890abcdef" not in (findings[0].details or "")


def test_secret_analyzer_fixture_path_windows_and_posix():
    analyzer = SecretAnalyzer()
    diff = """diff --git a/fixtures/mock_data.py b/fixtures/mock_data.py
--- a/fixtures/mock_data.py
+++ b/fixtures/mock_data.py
@@ -1,2 +1,3 @@
+api_key = "test-secret-placeholder"
diff --git a/tests\\sub\\test_api.py b/tests\\sub\\test_api.py
--- a/tests\\sub\\test_api.py
+++ b/tests\\sub\\test_api.py
@@ -1,2 +1,3 @@
+api_key = "example-token"
"""
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        staged_diff=diff,
    )
    findings = analyzer.analyze(ctx)
    assert all(f.severity == ReviewSeverity.INFO for f in findings) or len(findings) == 0


def test_private_key_in_test_file_retained_high():
    analyzer = PrivateKeyAnalyzer()
    diff = """diff --git a/tests/fixtures/test_key.pem b/tests/fixtures/test_key.pem
--- a/tests/fixtures/test_key.pem
+++ b/tests/fixtures/test_key.pem
@@ -0,0 +1,3 @@
+-----BEGIN RSA PRIVATE KEY-----
+MIIEowIBAAKCAQEA...
"""
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        staged_diff=diff,
    )
    findings = analyzer.analyze(ctx)
    assert len(findings) == 1
    assert findings[0].severity == ReviewSeverity.HIGH


def test_review_engine_deduplicate_overlapping_private_key_and_secret():
    engine = ReviewEngine()
    diff = """diff --git a/src/keys.pem b/src/keys.pem
--- a/src/keys.pem
+++ b/src/keys.pem
@@ -0,0 +1,3 @@
+-----BEGIN RSA PRIVATE KEY-----
+MIIEowIBAAKCAQEA...
"""
    ctx = CommitContext(
        repository_name="test",
        current_branch="main",
        changed_files=[ChangedFile(path="src/keys.pem", status="A")],
        staged_diff=diff,
    )
    result = engine.run(ctx)
    # Should only flag one finding for the private key on that file, not duplicate warnings
    assert len(result.findings) == 1
    assert result.findings[0].category == "Private Key"
