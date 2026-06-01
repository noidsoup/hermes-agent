#!/usr/bin/env python3
"""Generate MeMo-style reflection QA records for stable repo knowledge.

This is a lightweight pilot, not model training. It distills stable markdown
and selected source files into source-linked QA/reflection JSONL records that
can be queried by scripts/query_memory_oracle.py.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_OUTPUT = Path("wiki/memory/reflections.jsonl")
EXCLUDE_PARTS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "logs",
    "sessions",
    "secrets",
}
EXCLUDE_NAMES = {
    ".env",
    ".env.local",
    "auth.json",
    "credentials.json",
    "memories.json",
}
STABLE_ROOT_FILES = ("AGENTS.md", "CLAUDE.md", "README.md", "pyproject.toml")
STABLE_CODE_FILES = (
    "toolsets.py",
    "model_tools.py",
    "hermes_constants.py",
    "cron/jobs.py",
    "cron/scheduler.py",
    "tools/registry.py",
    "hermes_cli/commands.py",
)


@dataclass(frozen=True)
class SourceDoc:
    path: Path
    rel: str
    text: str


def _repo_path(value: str | None) -> Path:
    return Path(value or ".").expanduser().resolve()


def _safe_text(path: Path, max_chars: int = 80_000) -> str | None:
    try:
        if path.name in EXCLUDE_NAMES or any(part in EXCLUDE_PARTS for part in path.parts):
            return None
        data = path.read_bytes()
        if b"\0" in data[:4096]:
            return None
        text = data.decode("utf-8", errors="ignore")
        return text[:max_chars]
    except OSError:
        return None


def _iter_sources(repo: Path, include_website: bool) -> Iterable[SourceDoc]:
    candidates: list[Path] = []
    for name in STABLE_ROOT_FILES:
        p = repo / name
        if p.is_file():
            candidates.append(p)
    wiki = repo / "wiki"
    if wiki.is_dir():
        candidates.extend(sorted(wiki.glob("**/*.md")))
    if include_website:
        docs = repo / "website" / "docs"
        if docs.is_dir():
            # Keep v0 bounded: top-level docs and feature docs, skip optional skill catalog bulk.
            for p in sorted(docs.glob("**/*.md*")):
                rel = p.relative_to(repo).as_posix()
                if "/optional/" in rel or "skills-catalog" in rel:
                    continue
                candidates.append(p)
    for rel_name in STABLE_CODE_FILES:
        p = repo / rel_name
        if p.is_file():
            candidates.append(p)

    seen: set[Path] = set()
    for path in candidates:
        try:
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            text = _safe_text(path)
            if not text or not text.strip():
                continue
            yield SourceDoc(path=path, rel=path.relative_to(repo).as_posix(), text=text)
        except ValueError:
            continue


def _strip_frontmatter(text: str) -> str:
    return re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)


def _title_from_doc(doc: SourceDoc) -> str:
    text = _strip_frontmatter(doc.text)
    m = re.search(r"^#\s+(.+)$", text, flags=re.M)
    if m:
        return re.sub(r"[`*_\[\]]", "", m.group(1)).strip()
    return doc.path.stem.replace("-", " ").replace("_", " ").title()


def _first_paragraph(text: str) -> str:
    text = _strip_frontmatter(text)
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("|") or line.startswith("```"):
            if lines:
                break
            continue
        if line.startswith(">"):
            line = line.lstrip("> ")
        lines.append(line)
        if len(" ".join(lines)) > 360:
            break
    return _clean_answer(" ".join(lines))


def _clean_answer(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("[[", "").replace("]]", "")
    return text[:900].rstrip()


def _record_id(question: str, sources: list[str]) -> str:
    h = hashlib.sha256((question + "\0" + "\0".join(sources)).encode()).hexdigest()[:12]
    return f"refl-{h}"


def _mk_record(question: str, answer: str, sources: list[str], typ: str, stability: str = "stable") -> dict:
    now = datetime.now(timezone.utc).date().isoformat()
    return {
        "id": _record_id(question, sources),
        "question": question,
        "answer": answer,
        "type": typ,
        "stability": stability,
        "sources": sources,
        "created_at": now,
        "updated_at": now,
        "generator": "scripts/generate_reflections.py:v0",
    }


def _heading_records(doc: SourceDoc) -> list[dict]:
    text = _strip_frontmatter(doc.text)
    title = _title_from_doc(doc)
    records: list[dict] = []
    summary = _first_paragraph(doc.text)
    if summary:
        records.append(
            _mk_record(
                f"What does {title} cover?",
                summary,
                [doc.rel],
                "summary",
            )
        )

    headings = list(re.finditer(r"^(#{2,3})\s+(.+)$", text, flags=re.M))
    for i, match in enumerate(headings):
        heading = re.sub(r"[`*_\[\]]", "", match.group(2)).strip()
        start = match.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        section = text[start:end].strip()
        answer = _section_answer(section)
        if not answer:
            continue
        records.append(
            _mk_record(
                f"What should I know about {heading} in {title}?",
                answer,
                [doc.rel],
                "section",
            )
        )
        records.extend(_label_records(section, title, heading, doc.rel))
    return records


def _label_records(section: str, title: str, heading: str, rel: str) -> list[dict]:
    """Extract mini-records for prose labels followed by bullet lists.

    Markdown often has a section like "What belongs here" containing labels
    such as "Good candidates:" and "Bad candidates:". Treat those labels as
    queryable subtopics so negated questions retrieve the right bullets.
    """
    records: list[dict] = []
    lines = section.splitlines()
    for i, raw in enumerate(lines):
        label = raw.strip()
        if not re.match(r"^[A-Z][A-Za-z0-9 /_-]{2,60}:$", label):
            continue
        bullets: list[str] = []
        for nxt in lines[i + 1 :]:
            line = nxt.strip()
            if not line:
                if bullets:
                    break
                continue
            if line.startswith(("-", "*")) or re.match(r"^\d+[.)]\s+", line):
                bullets.append(line)
                if len(bullets) >= 8:
                    break
                continue
            if bullets:
                break
        answer = _clean_answer(" ".join(bullets))
        if answer:
            topic = label.rstrip(":")
            records.append(
                _mk_record(
                    f"What are {topic.lower()} for {heading} in {title}?",
                    answer,
                    [rel],
                    "section-label",
                )
            )
    return records


def _section_answer(section: str) -> str:
    lines: list[str] = []
    in_code = False
    seen_content = False
    for raw in section.splitlines():
        line = raw.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line or line.startswith("|"):
            if seen_content and not line:
                break
            continue
        if re.match(r"^#{1,6}\s+", line):
            continue
        # Keep consecutive bullets/numbered items. This is important for sections
        # like "Bad candidates" where every line is a bullet and no paragraph leads.
        if line.startswith(("-", "*")) or re.match(r"^\d+[.)]\s+", line):
            lines.append(line)
            seen_content = True
        elif not lines:
            lines.append(line)
            seen_content = True
        elif seen_content:
            # Preserve short follow-up prose after the first paragraph/bullet block.
            if len(" ".join(lines)) < 260:
                lines.append(line)
            else:
                break
        if len(" ".join(lines)) > 720 or len(lines) >= 10:
            break
    return _clean_answer(" ".join(lines))


def _code_records(doc: SourceDoc) -> list[dict]:
    if doc.path.suffix not in {".py", ".toml"}:
        return []
    rel = doc.rel
    stem = doc.path.name
    text = doc.text
    records: list[dict] = []
    module_doc = re.search(r'\A(?:#!.*\n)?\s*"""(.*?)"""', text, flags=re.S)
    if module_doc:
        records.append(
            _mk_record(
                f"What is the purpose of {rel}?",
                _clean_answer(module_doc.group(1)),
                [rel],
                "code-summary",
            )
        )
    names = re.findall(r"^(?:class|def)\s+([A-Za-z_][A-Za-z0-9_]*)", text, flags=re.M)
    if names:
        answer = f"{stem} defines notable symbols: " + ", ".join(names[:20]) + "."
        records.append(_mk_record(f"What are the notable symbols in {rel}?", answer, [rel], "code-symbols"))
    return records


def generate(repo: Path, include_website: bool, max_records: int) -> list[dict]:
    records: list[dict] = []
    for doc in _iter_sources(repo, include_website=include_website):
        records.extend(_heading_records(doc))
        records.extend(_code_records(doc))
        if len(records) >= max_records:
            break
    dedup: dict[str, dict] = {}
    for rec in records:
        if rec["answer"] and len(rec["answer"]) >= 24:
            dedup[rec["id"]] = rec
    return list(dedup.values())[:max_records]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Repository root (default: cwd)")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output JSONL path relative to repo")
    parser.add_argument("--max-records", type=int, default=250)
    parser.add_argument("--include-website", action="store_true", help="Include bounded website/docs pages")
    args = parser.parse_args()

    repo = _repo_path(args.repo)
    output = Path(args.output)
    if not output.is_absolute():
        output = repo / output
    records = generate(repo, include_website=args.include_website, max_records=args.max_records)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"wrote {len(records)} reflections to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
