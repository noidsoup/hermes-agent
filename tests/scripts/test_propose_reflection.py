from pathlib import Path

from scripts.propose_reflection import propose


def test_propose_reflection_quarantines_secret_and_path_escape(tmp_path):
    result = propose(
        tmp_path,
        "Where is the token?",
        "TOKEN=***",  # gitleaks:allow test fixture for redaction/quarantine
        ["../outside.md"],
        approve=True,
    )
    rec = result["record"]
    assert rec["status"] == "quarantined"
    assert rec["risk_flags"]
    assert rec["sources"] == []
    assert result["written"].endswith("rejected.jsonl")


def test_propose_reflection_approves_safe_relative_source(tmp_path):
    (tmp_path / "wiki").mkdir()
    result = propose(tmp_path, "What is stable?", "Stable durable knowledge.", ["wiki/source.md"], approve=True)
    rec = result["record"]
    assert rec["status"] == "approved"
    assert rec["sources"] == ["wiki/source.md"]
