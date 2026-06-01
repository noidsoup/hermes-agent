#!/usr/bin/env python3
"""Mine commit metadata from local Git clones into the GitHub intelligence vault.

This collector is read-only with respect to GitHub and local working trees. By
default it only reads existing local refs. Pass --fetch to update remote-tracking
refs/tags before scanning so commits currently reachable on remotes are included.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

# Reuse redaction + vault helpers from the API collector when run from repo root.
try:
    from github_intelligence_collect import DEFAULT_OUT, atomic_write_jsonl, ensure_layout, iso_now, load_existing_jsonl, redact, write_json
except ImportError:  # pragma: no cover - direct path fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from github_intelligence_collect import DEFAULT_OUT, atomic_write_jsonl, ensure_layout, iso_now, load_existing_jsonl, redact, write_json

DEFAULT_REPO_ROOTS = [Path.home() / "Repos", Path.home() / ".hermes" / "hermes-agent"]
CREDENTIAL_RE = re.compile(r"(https?://)([^/@\s:]+)(?::[^/@\s]+)?@", re.I)
REMOTE_SUFFIX_RE = re.compile(r"(?:\.git)?/?$")


def run_git(repo: Path, args: list[str], timeout: int = 300) -> tuple[int, str, str]:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def discover_repos(roots: Iterable[Path]) -> list[Path]:
    repos: set[Path] = set()
    for root in roots:
        root = root.expanduser().resolve()
        if not root.exists():
            continue
        if (root / ".git").exists():
            repos.add(root)
        for git_dir in root.rglob(".git"):
            if git_dir.is_dir():
                repos.add(git_dir.parent.resolve())
    return sorted(repos, key=lambda p: str(p).lower())


def sanitize_remote_url(url: str) -> str:
    url = CREDENTIAL_RE.sub(r"\1REDACTED@", url.strip())
    return redact(url)


def repo_key_from_remote(url: str) -> str | None:
    clean = sanitize_remote_url(url)
    if not clean:
        return None
    if "github.com:" in clean:
        part = clean.split("github.com:", 1)[1]
    elif "github.com/" in clean:
        part = clean.split("github.com/", 1)[1]
    else:
        return None
    part = REMOTE_SUFFIX_RE.sub("", part)
    bits = part.split("/")
    if len(bits) >= 2:
        return f"{bits[-2]}/{bits[-1]}"
    return None


def remote_info(repo: Path) -> tuple[dict[str, str], str]:
    rc, out, _ = run_git(repo, ["remote", "-v"], timeout=60)
    remotes: dict[str, str] = {}
    key = repo.name
    if rc == 0:
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0] not in remotes:
                remotes[parts[0]] = sanitize_remote_url(parts[1])
                maybe_key = repo_key_from_remote(parts[1])
                if maybe_key and (parts[0] == "origin" or "/" not in key):
                    key = maybe_key
    return remotes, key


def fetch_repo(repo: Path) -> dict[str, Any]:
    rc, out, err = run_git(repo, ["fetch", "--all", "--tags", "--prune"], timeout=900)
    return {"ok": rc == 0, "stdout_tail": out[-1000:], "stderr_tail": err[-2000:]}


def read_refs(repo: Path) -> dict[str, list[str]]:
    rc, out, err = run_git(repo, ["for-each-ref", "--format=%(objectname)%09%(refname:short)%09%(refname)"], timeout=120)
    if rc != 0:
        raise RuntimeError(err.strip() or "git for-each-ref failed")
    refs_by_sha: dict[str, list[str]] = defaultdict(list)
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and re.fullmatch(r"[0-9a-f]{40}", parts[0]):
            refs_by_sha[parts[0]].append(parts[1])
    return refs_by_sha


def iter_commit_rows(repo: Path, repo_key: str, remotes: dict[str, str], refs_by_sha: dict[str, list[str]], max_commits: int | None = None) -> list[dict[str, Any]]:
    fmt = "%H%x1f%P%x1f%an%x1f%ae%x1f%aI%x1f%cn%x1f%ce%x1f%cI%x1f%s%x1f%B%x1e"
    cmd = ["log", "--all", "--date=iso-strict", f"--format={fmt}"]
    if max_commits:
        cmd.insert(1, f"-{max_commits}")
    rc, out, err = run_git(repo, cmd, timeout=1200)
    if rc != 0:
        raise RuntimeError(err.strip() or "git log --all failed")
    rows: list[dict[str, Any]] = []
    for rec in out.split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        fields = rec.split("\x1f", 9)
        if len(fields) != 10:
            continue
        sha, parents, author_name, author_email, authored_at, committer_name, committer_email, committed_at, subject, body = fields
        rows.append({
            "repo": repo_key,
            "local_path": str(repo),
            "sha": sha,
            "parents": [p for p in parents.split() if p],
            "author_name": author_name,
            "author_email": author_email,
            "authored_at": authored_at,
            "committer_name": committer_name,
            "committer_email": committer_email,
            "committed_at": committed_at,
            "subject": subject,
            "body": body.strip(),
            "refs": sorted(refs_by_sha.get(sha, [])),
            "remotes": remotes,
            "collected_at": iso_now(),
        })
    return rows


def merge_commits(existing: Iterable[dict], new_rows: Iterable[dict]) -> list[dict]:
    by_key: dict[str, dict] = {}
    for row in [*existing, *new_rows]:
        key = f"{row.get('repo')}:{row.get('sha')}"
        prior = by_key.get(key)
        if prior:
            refs = sorted(set(prior.get("refs") or []) | set(row.get("refs") or []))
            prior.update(row)
            prior["refs"] = refs
        else:
            by_key[key] = row
    return sorted(by_key.values(), key=lambda r: ((r.get("repo") or ""), (r.get("committed_at") or ""), (r.get("sha") or "")))


def collect_commits(data: Path, repo_roots: list[Path], fetch: bool = False, max_repos: int | None = None, max_commits_per_repo: int | None = None) -> dict[str, Any]:
    ensure_layout(data)
    repos = discover_repos(repo_roots)
    if max_repos:
        repos = repos[:max_repos]
    manifest: dict[str, Any] = {
        "started_at": iso_now(),
        "data": str(data),
        "repo_roots": [str(p.expanduser()) for p in repo_roots],
        "fetch": fetch,
        "repo_count": len(repos),
        "repos": [],
        "errors": [],
    }
    all_new: list[dict[str, Any]] = []
    for idx, repo in enumerate(repos, 1):
        print(f"[{idx}/{len(repos)}] scanning {repo}", flush=True)
        rec: dict[str, Any] = {"path": str(repo), "started_at": iso_now()}
        try:
            remotes, repo_key = remote_info(repo)
            rec["repo"] = repo_key
            rec["remotes"] = remotes
            if fetch:
                rec["fetch"] = fetch_repo(repo)
            refs = read_refs(repo)
            rows = iter_commit_rows(repo, repo_key, remotes, refs, max_commits=max_commits_per_repo)
            rec["commit_count"] = len(rows)
            rec["ref_count"] = sum(len(v) for v in refs.values())
            all_new.extend(rows)
        except Exception as exc:
            rec["error"] = str(exc)
            manifest["errors"].append({"repo": str(repo), "error": str(exc)})
        rec["finished_at"] = iso_now()
        manifest["repos"].append(rec)
    commits_path = data / "raw" / "commits.jsonl"
    merged = merge_commits(load_existing_jsonl(commits_path), all_new)
    manifest["new_commit_rows"] = len(all_new)
    manifest["total_commit_rows"] = atomic_write_jsonl(commits_path, merged)
    manifest["finished_at"] = iso_now()
    write_json(data / "state" / "commit-scan.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=str(DEFAULT_OUT), help="GitHub intelligence vault path")
    parser.add_argument("--repo-root", action="append", default=None, help="Root to recursively scan for .git dirs; repeatable. Default: ~/Repos and ~/.hermes/hermes-agent")
    parser.add_argument("--fetch", action="store_true", help="Run git fetch --all --tags --prune before scanning each repo")
    parser.add_argument("--max-repos", type=int, default=None, help="Limit repos for smoke tests")
    parser.add_argument("--max-commits-per-repo", type=int, default=None, help="Limit commits per repo for smoke tests")
    parser.add_argument("--json", action="store_true", help="Print full JSON manifest")
    args = parser.parse_args()
    roots = [Path(p).expanduser() for p in args.repo_root] if args.repo_root else DEFAULT_REPO_ROOTS
    manifest = collect_commits(Path(args.data).expanduser().resolve(), roots, fetch=args.fetch, max_repos=args.max_repos, max_commits_per_repo=args.max_commits_per_repo)
    if args.json:
        print(json.dumps(redact(manifest), indent=2, ensure_ascii=False))
    else:
        print(f"scanned {manifest['repo_count']} repos; new rows {manifest['new_commit_rows']}; total rows {manifest['total_commit_rows']}; errors {len(manifest['errors'])}")
    return 0 if not manifest.get("errors") else 1


if __name__ == "__main__":
    raise SystemExit(main())
