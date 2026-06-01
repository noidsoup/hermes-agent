from pathlib import Path

from scripts.github_intelligence_commits import merge_commits, repo_key_from_remote, sanitize_remote_url


def test_sanitize_remote_url_redacts_credentials():
    cleaned = sanitize_remote_url("https://user:***@example.com/owner/repo.git")
    assert "supersecret" not in cleaned
    assert cleaned == "https://REDACTED@example.com/owner/repo.git"


def test_repo_key_from_github_remotes():
    assert repo_key_from_remote("git@github.com:noidsoup/hermes-agent.git") == "noidsoup/hermes-agent"
    assert repo_key_from_remote("https://github.com/NousResearch/hermes-agent.git") == "NousResearch/hermes-agent"


def test_merge_commits_dedupes_and_unions_refs():
    merged = merge_commits(
        [{"repo": "o/r", "sha": "abc", "refs": ["main"], "committed_at": "2026-01-01T00:00:00Z"}],
        [{"repo": "o/r", "sha": "abc", "refs": ["origin/main"], "committed_at": "2026-01-01T00:00:00Z"}, {"repo": "o/r", "sha": "def", "refs": []}],
    )
    assert len(merged) == 2
    by_sha = {row["sha"]: row for row in merged}
    assert by_sha["abc"]["refs"] == ["main", "origin/main"]
