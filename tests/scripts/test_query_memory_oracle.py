from pathlib import Path

from scripts.query_memory_oracle import verify_result_sources


def test_verify_result_sources_reports_existing_and_missing(tmp_path):
    (tmp_path / "exists.md").write_text("ok", encoding="utf-8")
    rec = {"sources": ["exists.md", "missing.md"]}
    checks = verify_result_sources(rec, tmp_path)
    assert checks[0]["exists"] is True
    assert checks[1]["exists"] is False
