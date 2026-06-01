import json
from pathlib import Path

from scripts.generate_reflections import generate


def test_generate_reflections_includes_code_structure_and_tool_relations():
    repo = Path(__file__).resolve().parents[2]
    records = generate(repo, include_website=False, max_records=500)
    assert any(r["type"] == "code-structure" and "tools/memory_oracle_tool.py" in r["sources"] for r in records)
    assert any(r["type"] == "code-relations" and "memory_oracle_query" in r["answer"] for r in records)
