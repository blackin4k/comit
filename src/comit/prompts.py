from __future__ import annotations

import re
from typing import List, Optional, Union

from comit.commit.context import CommitContext, DiffStat

MAX_DIFF_CHARS = 12000

SYSTEM_PROMPT = """You are an expert Git commit assistant.
Your task is to generate ONE concise, accurate, and high-quality Git commit message based on the provided staged diff and repository context.

Requirements:
1. The staged diff is the ultimate source of truth. Examine the staged diff to understand the exact changes made. Do NOT invent features or mention files/changes not present in the diff.
2. Use the repository context (repository name, current branch, changed files, statistics) to understand the intent, scope, and domain of the modifications.
3. Examine the recent commit history to infer and match the repository's existing style:
   - If the repository uses Conventional Commits (e.g. feat:, fix:, refactor:, chore:, docs:, test:, style:), adhere to Conventional Commits.
   - If the repository uses another consistent style (capitalization, prefix convention, imperative vs descriptive verbs, issue references), follow that style.
   - If there is no commit history or style is mixed, use standard Conventional Commits.
4. Do not let previous commits or branch names override what is actually present in the staged diff.
5. Keep the commit message concise (single-line subject, ideally under 72 characters).
6. Do NOT wrap the message in quotation marks.
7. Do NOT use markdown code blocks or backticks in the response.
8. Do NOT include explanations, greetings, preamble, or commentary (e.g. do not write "Here is the commit message:").
9. Return ONLY the commit message text.
"""


def truncate_diff(diff: str, max_chars: int = MAX_DIFF_CHARS) -> str:
    if len(diff) <= max_chars:
        return diff

    truncated = diff[:max_chars]
    last_newline = truncated.rfind("\n")
    if last_newline > 0:
        truncated = truncated[:last_newline]

    return (
        f"{truncated}\n\n"
        "[... Staged diff truncated: changes were too large. Focus on the primary modifications shown above ...]"
    )


def build_commit_prompt(
    context: Union[CommitContext, str],
    recent_commits: Optional[List[str]] = None,
    avoid_messages: Optional[List[str]] = None,
) -> str:
    if isinstance(context, str):
        context_obj = CommitContext(
            repository_name="",
            current_branch="",
            changed_files=[],
            recent_commits=recent_commits or [],
            diff_stat=DiffStat(),
            staged_diff=context,
        )
    else:
        context_obj = context
        if recent_commits and not context_obj.recent_commits:
            context_obj.recent_commits = recent_commits

    safe_diff = truncate_diff(context_obj.staged_diff)
    sections: List[str] = []

    repo_meta: List[str] = []
    if context_obj.repository_name:
        repo_meta.append(f"Repository: {context_obj.repository_name}")
    if context_obj.current_branch:
        repo_meta.append(f"Branch: {context_obj.current_branch}")
    if repo_meta:
        sections.append("\n".join(repo_meta))

    if context_obj.changed_files:
        files_lines = [f.format_line() for f in context_obj.changed_files]
        sections.append("Changed files:\n" + "\n".join(files_lines))

    stat_summary = context_obj.diff_stat.format_summary()
    if stat_summary and stat_summary != "0 files changed":
        sections.append(f"Change statistics:\n  {stat_summary}")

    if context_obj.recent_commits:
        history_str = "\n".join(f"  {c}" for c in context_obj.recent_commits[:15])
        sections.append(f"Recent commits:\n{history_str}")
    else:
        sections.append("Recent commits:\n  (No previous commits found; use Conventional Commits style)")

    sections.append(f"Staged diff:\n```diff\n{safe_diff}\n```")

    if avoid_messages:
        avoid_str = "\n".join(f'- "{m}"' for m in avoid_messages if m and m.strip())
        sections.append(
            f"Previous suggestion(s) to avoid repeating:\n{avoid_str}\n\n"
            "Please generate a DIFFERENT, alternative commit message that accurately describes the staged changes without repeating the previous suggestion(s)."
        )
    else:
        sections.append("Generate ONE commit message for these changes:")

    return "\n\n".join(sections)


def sanitize_commit_message(raw_text: str) -> str:
    if not raw_text:
        return ""

    text = raw_text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z0-9_-]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()

    prefixes_to_strip = [
        r"^commit\s*message\s*:\s*",
        r"^suggested\s*commit\s*(message)?\s*:\s*",
        r"^here\s+is\s+(the|a)\s+suggested\s+commit\s+message\s*:\s*",
        r"^here\s+is\s+the\s+commit\s+message\s*:\s*",
        r"^here\s+is\s+your\s+commit\s+message\s*:\s*",
    ]
    for prefix in prefixes_to_strip:
        text = re.sub(prefix, "", text, flags=re.IGNORECASE).strip()

    quote_pairs = [
        ('"', '"'),
        ("'", "'"),
        ("`", "`"),
        ("“", "”"),
        ("‘", "’"),
    ]
    for start_q, end_q in quote_pairs:
        if text.startswith(start_q) and text.endswith(end_q) and len(text) >= 2:
            text = text[len(start_q):-len(end_q)].strip()

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""

    if len(lines) > 1 and lines[0].lower().endswith(":") and len(lines[0].split()) < 8:
        text = "\n\n".join(lines[1:])
    else:
        text = "\n\n".join(lines)

    for start_q, end_q in quote_pairs:
        if text.startswith(start_q) and text.endswith(end_q) and len(text) >= 2:
            text = text[len(start_q):-len(end_q)].strip()

    return text.strip()
