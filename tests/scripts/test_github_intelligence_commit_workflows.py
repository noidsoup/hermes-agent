from scripts.github_intelligence_commit_workflows import classify_commits, classify_subject, is_remote_reachable


def test_classify_subject_maps_common_workflows():
    assert "bugfix_loops" in classify_subject("fix(auth): preserve OAuth next param")
    assert "ci_github_actions" in classify_subject("chore(ci): add GitHub Actions PR verify workflow")
    assert "airtable_apfs" in classify_subject("feat(fub): Airtable invoice sync")
    assert "agent_cursor_hermes" in classify_subject("fix(hermes): gateway launchd restart")
    assert "memory_wiki_docs" in classify_subject("docs: SimpleMem wiki runbook")


def test_remote_reachable_ignores_tags_only():
    assert is_remote_reachable({"refs": ["origin/main"]}) is True
    assert is_remote_reachable({"refs": ["tags/v1.0.0"]}) is False
    assert is_remote_reachable({"refs": []}) is False


def test_classify_commits_builds_workflows_and_repo_profiles():
    commits = [
        {"repo": "noidsoup/APFS-Database", "sha": "a" * 40, "subject": "fix(fub): Airtable invoice sync queue", "refs": ["origin/main"], "committed_at": "2026-01-01T00:00:00Z"},
        {"repo": "noidsoup/APFS-Database", "sha": "b" * 40, "subject": "docs: SimpleMem wiki runbook", "refs": [], "committed_at": "2026-01-02T00:00:00Z"},
        {"repo": "NousResearch/hermes-agent", "sha": "c" * 40, "subject": "fix(hermes): gateway launchd watchdog", "refs": ["origin/main"], "committed_at": "2026-01-03T00:00:00Z"},
    ]
    out = classify_commits(commits)
    by_key = {row["key"]: row for row in out["workflows"]}
    assert out["total_commits"] == 3
    assert out["remote_ref_count"] == 2
    assert by_key["airtable_apfs"]["count"] == 1
    assert by_key["automation_cron_sync"]["count"] == 2
    assert by_key["agent_cursor_hermes"]["count"] == 1
    apfs = next(row for row in out["repo_profiles"] if row["repo"] == "noidsoup/APFS-Database")
    assert apfs["total"] == 2
    assert apfs["remote_ref_count"] == 1
    assert apfs["top_workflows"][0][1] >= 1
