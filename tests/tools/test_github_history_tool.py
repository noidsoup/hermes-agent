from __future__ import annotations

import json
from pathlib import Path

from tools.github_history_tool import query_github_history
from tools.registry import registry


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")


def test_query_github_history_searches_jsonl_and_reports(tmp_path: Path) -> None:
    vault = tmp_path / "github-intelligence"
    _write_jsonl(
        vault / "raw" / "prs-authored.jsonl",
        [
            {
                "title": "Automate Airtable registry sync",
                "html_url": "https://github.com/noidsoup/APFS-Database/pull/211",
                "body": "Cloud Automations sync and shadow scripts",
            },
            {
                "title": "Unrelated UI polish",
                "html_url": "https://github.com/example/repo/pull/1",
                "body": "CSS cleanup",
            },
        ],
    )
    reports = vault / "reports"
    reports.mkdir(parents=True)
    (reports / "project-themes.md").write_text("Airtable automation shows repeated workflow patterns\n", encoding="utf-8")

    result = query_github_history("airtable automation", data_dir=str(vault), limit=5)

    assert result["success"] is True
    assert result["scanned_records"] == 3
    assert result["count"] == 2
    assert result["hits"][0]["score"] >= result["hits"][1]["score"]
    assert any(hit["url"] == "https://github.com/noidsoup/APFS-Database/pull/211" for hit in result["hits"])
    assert any(hit["dataset"] == "report:project-themes" for hit in result["hits"])


def test_query_github_history_validates_query(tmp_path: Path) -> None:
    result = query_github_history("", data_dir=str(tmp_path), limit=5)

    assert result["success"] is False
    assert "query is required" in result["error"]


def test_query_github_history_missing_vault(tmp_path: Path) -> None:
    result = query_github_history("airtable", data_dir=str(tmp_path / "missing"), limit=5)

    assert result["success"] is False
    assert "vault not found" in result["error"]


def test_github_history_tool_registered() -> None:
    entry = registry.get_entry("github_history_query")

    assert entry is not None
    assert entry.toolset == "github_history"
    assert entry.schema["parameters"]["required"] == ["query"]
