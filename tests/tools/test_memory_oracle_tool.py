from pathlib import Path
import json

from tools.memory_oracle_tool import memory_oracle_query


def test_memory_oracle_query_returns_hit_for_repo():
    repo = Path(__file__).resolve().parents[2]
    result = memory_oracle_query(
        "What is the purpose of the memory oracle?",
        repo=str(repo),
        limit=2,
        min_score=10,
        verify_sources=True,
    )
    assert result["success"] is True
    assert result["no_hit"] is False
    assert result["results"]
    assert "memory" in result["results"][0]["answer"].lower()
    assert "source_verification" in result["results"][0]


def test_memory_oracle_query_no_hit_threshold():
    repo = Path(__file__).resolve().parents[2]
    result = memory_oracle_query(
        "How should I debug voice transcription?",
        repo=str(repo),
        limit=2,
        min_score=10,
    )
    assert result["success"] is True
    assert result["no_hit"] is True
    assert result["results"] == []


def test_memory_oracle_query_missing_repo_returns_structured_error(tmp_path):
    result = memory_oracle_query("anything", repo=str(tmp_path), limit=1)
    assert result["success"] is False
    assert result["no_hit"] is True
    assert "not found" in result["error"]
