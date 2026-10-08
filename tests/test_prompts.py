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
    assert "Recent commits:" in prompt


def test_build_commit_prompt_without_history():
    diff = "diff --git a/init.py b/init.py\n+x = 1"
    prompt = build_commit_prompt(diff, [])

    assert "+x = 1" in prompt
    assert "No previous commits found" in prompt


def test_build_commit_prompt_with_avoid_messages():
    diff = "diff --git a/app.py b/app.py\n+y = 2"
    prompt = build_commit_prompt(diff, avoid_messages=["feat: previous suggestion"])

    assert "Previous suggestion(s) to avoid repeating" in prompt
    assert "feat: previous suggestion" in prompt


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


def test_build_commit_prompt_with_commit_context():
    from comit.commit.context import CommitContext, ChangedFile, DiffStat

    ctx = CommitContext(
        repository_name="my-project",
        current_branch="feature/auth",
        changed_files=[
            ChangedFile(path="src/auth.py", status="M"),
            ChangedFile(path="src/token.py", status="A"),
            ChangedFile(path="src/legacy.py", status="D"),
            ChangedFile(path="src/new_name.py", status="R", old_path="src/old_name.py"),
        ],
        recent_commits=["feat: initial login", "fix: token validation"],
        diff_stat=DiffStat(files_changed=4, insertions=120, deletions=45, summary_text="4 files changed, 120 insertions(+), 45 deletions(-)"),
        staged_diff="diff --git a/src/auth.py b/src/auth.py\n+jwt_auth()",
    )

    prompt = build_commit_prompt(ctx)

    assert "Repository: my-project" in prompt
    assert "Branch: feature/auth" in prompt
    assert "Changed files:" in prompt
    assert "  M src/auth.py" in prompt
    assert "  A src/token.py" in prompt
    assert "  D src/legacy.py" in prompt
    assert "  R src/old_name.py -> src/new_name.py" in prompt
    assert "Change statistics:\n  4 files changed, 120 insertions(+), 45 deletions(-)" in prompt
    assert "Recent commits:" in prompt
    assert "  feat: initial login" in prompt
    assert "  fix: token validation" in prompt
    assert "Staged diff:" in prompt
    assert "+jwt_auth()" in prompt


def test_build_commit_prompt_context_with_avoid_messages():
    from comit.commit.context import CommitContext, ChangedFile, DiffStat

    ctx = CommitContext(
        repository_name="my-project",
        current_branch="main",
        changed_files=[ChangedFile(path="README.md", status="M")],
        recent_commits=[],
        diff_stat=DiffStat(files_changed=1, insertions=5, deletions=1),
        staged_diff="diff --git a/README.md b/README.md\n+updated docs",
    )

    prompt = build_commit_prompt(ctx, avoid_messages=["docs: update readme"])

    assert "Repository: my-project" in prompt
    assert "Branch: main" in prompt
    assert "Previous suggestion(s) to avoid repeating:" in prompt
    assert 'docs: update readme' in prompt
