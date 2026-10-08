from comit.prompts import (
    truncate_diff,
    build_commit_prompt,
    sanitize_commit_message,
)


def test_truncate_diff_under_limit():
    short_diff = "diff --git a/app.py b/app.py\n+print('test')"
    truncated = truncate_diff(short_diff, max_chars=100)
    assert truncated == short_diff
    assert "truncated" not in truncated


def test_truncate_diff_over_limit():
    long_diff = "line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8"
    truncated = truncate_diff(long_diff, max_chars=25)
    assert len(truncated) < len(long_diff) + 120
    assert "[... Staged diff truncated" in truncated
    assert "line1" in truncated


def test_build_commit_prompt_with_history():
    diff = "diff --git a/main.py b/main.py\n+def run(): pass"
    history = ["feat: add user login", "fix: correct token expiry"]
    prompt = build_commit_prompt(diff, history)

    assert "feat: add user login" in prompt
    assert "fix: correct token expiry" in prompt
    assert "+def run(): pass" in prompt
    assert "Recent commit history from this repository" in prompt


def test_build_commit_prompt_without_history():
    diff = "diff --git a/init.py b/init.py\n+x = 1"
    prompt = build_commit_prompt(diff, [])

    assert "+x = 1" in prompt
    assert "Repository has no previous commits" in prompt


def test_sanitize_commit_message_clean():
    msg = "feat: add user authentication"
    assert sanitize_commit_message(msg) == "feat: add user authentication"


def test_sanitize_commit_message_quotes():
    assert sanitize_commit_message('"feat: add feature"') == "feat: add feature"
    assert sanitize_commit_message("'fix: typo in readme'") == "fix: typo in readme"
    assert sanitize_commit_message("`refactor: clean up git helper`") == "refactor: clean up git helper"
    assert sanitize_commit_message("“chore: update dependencies”") == "chore: update dependencies"


def test_sanitize_commit_message_markdown_fences():
    raw = "```\nfeat: implement caching layer\n```"
    assert sanitize_commit_message(raw) == "feat: implement caching layer"

    raw_git = "```git\nfeat: implement caching layer\n```"
    assert sanitize_commit_message(raw_git) == "feat: implement caching layer"


def test_sanitize_commit_message_preamble():
    raw = "Here is the commit message:\nfeat: add dark mode support"
    assert sanitize_commit_message(raw) == "feat: add dark mode support"

    raw2 = "Commit message: fix: prevent duplicate submissions"
    assert sanitize_commit_message(raw2) == "fix: prevent duplicate submissions"

    raw3 = "Suggested commit:\n\nfeat: add JWT auth"
    assert sanitize_commit_message(raw3) == "feat: add JWT auth"


def test_sanitize_commit_message_empty():
    assert sanitize_commit_message("") == ""
    assert sanitize_commit_message("   ") == ""
