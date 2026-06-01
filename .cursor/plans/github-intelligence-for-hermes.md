# GitHub Intelligence for Hermes Implementation Plan

> **For Hermes:** Implement read-only GitHub collection and local analysis. Do not mutate GitHub state. Do not clone private code by default. Do not store GitHub raw data in Hermes persistent memory. Keep raw data local under `~/Data/github-intelligence/`.

**Goal:** Bring Nicholas's accessible GitHub history into a local, source-linked intelligence vault and use it to improve Hermes through evidence-backed reports, query tools, and future reflection generation.

**Architecture:** Use `gh` as the authenticated read-only transport. Store raw API payloads as JSONL/JSON under a local data directory. Generate derived markdown/JSON reports and lightweight indexes. Promote only stable, non-sensitive high-level insights into Hermes/skills after review.

**Tech Stack:** Python stdlib, `gh` CLI, JSONL, local filesystem, optional SQLite later.

---

## Safety Boundaries

- Read-only GitHub operations only:
  - Allowed: `gh api GET`, `gh search`, GraphQL queries, local report generation.
  - Forbidden: `gh repo edit`, `gh pr merge`, `gh pr close`, `gh issue edit`, `gh secret set`, pushes to user/org repos.
- Do not clone every repo in this first pass. Metadata/PR/issues first; clone or fetch code only after explicit follow-up approval.
- Do not write raw private org data into Hermes memory.
- Do not index secrets into memory/reflections. Redact token-looking strings in derived reports.
- All data lives under `~/Data/github-intelligence/`.

## Directory Layout

```text
~/Data/github-intelligence/
  README.md
  raw/
    user.json
    orgs.jsonl
    repos.jsonl
    prs-authored.jsonl
    prs-involved.jsonl
    issues-authored.jsonl
    issues-involved.jsonl
    reviews.jsonl
    events.jsonl
    gists.jsonl
  state/
    manifest.json
    errors.jsonl
  reports/
    inventory.md
    hermes-improvement-opportunities.md
    project-themes.md
    pr-timeline.md
    dormant-projects.md
  index/
    github_actions.jsonl
```

## Phase 1: Collector

### Task 1.1: Create collector script

**Files:**
- Create: `scripts/github_intelligence_collect.py`

**Behavior:**
- Runs `gh auth status` and `gh api user`.
- Collects:
  - authenticated user
  - orgs
  - accessible repos via `/user/repos?type=all&affiliation=owner,collaborator,organization_member`
  - authored PRs via GraphQL search pagination
  - involved PRs via GraphQL search pagination
  - authored/involved issues
  - public/reachable events from `/users/{login}/events/public`
  - gists metadata
- Writes JSONL incrementally.
- Has `--max-pages` for safe smoke tests.
- Has `--since YYYY-MM-DD` for future incremental refresh.
- Prints progress.
- Never calls mutating endpoints.

### Task 1.2: Add tests for parsing/writing helpers

**Files:**
- Create: `tests/scripts/test_github_intelligence_collect.py`

**Test:**
- JSONL append/write works.
- Search query builder includes `author:noidsoup` / `involves:noidsoup`.
- Redaction removes token-looking strings.

## Phase 2: Initial Collection

### Task 2.1: Run smoke collection

```bash
python3 scripts/github_intelligence_collect.py --out ~/Data/github-intelligence --max-pages 1
```

Expected:
- auth succeeds as `noidsoup`
- orgs include currently visible orgs
- raw JSONL files have records

### Task 2.2: Run broader collection in background

```bash
python3 scripts/github_intelligence_collect.py --out ~/Data/github-intelligence
```

Use Hermes background process with notify-on-complete if it may take a while.

## Phase 3: Reports for Hermes Improvement

### Task 3.1: Create analysis script

**Files:**
- Create: `scripts/github_intelligence_analyze.py`

**Reports:**
- `reports/inventory.md`: org/repo/language/activity inventory.
- `reports/hermes-improvement-opportunities.md`: concrete ways Nicholas's history can improve Hermes.
- `reports/project-themes.md`: recurring domains/stacks/patterns.
- `reports/pr-timeline.md`: PR activity by year/org/repo.
- `reports/dormant-projects.md`: old repos that may be worth revisiting.

### Task 3.2: Verify reports cite data

Each claim should cite repo/PR/issue URLs when possible.

## Phase 4: Query Tool

### Task 4.1: Create local query script

**Files:**
- Create: `scripts/github_intelligence_query.py`

**Behavior:**
- lexical search across raw and reports
- returns source URL/repo/type
- supports `--json`

### Task 4.2: Optional Hermes integration later

Do not register as default Hermes tool until raw-data shape and privacy strategy are validated.

## Phase 5: Improve Hermes

Use reports to propose:
- new Hermes skills based on recurring workflows Nicholas has used
- repo-specific AGENTS.md/rules improvements
- model routing improvements based on real stacks
- project revival queue
- prior-code reuse suggestions
- personalized planning/testing conventions

Only promote stable high-level insights after review.

## Verification Commands

```bash
python3 -m py_compile scripts/github_intelligence_collect.py scripts/github_intelligence_analyze.py scripts/github_intelligence_query.py
python3 -m pytest tests/scripts/test_github_intelligence_collect.py -q -o 'addopts='
python3 scripts/github_intelligence_collect.py --out ~/Data/github-intelligence --max-pages 1
python3 scripts/github_intelligence_analyze.py --data ~/Data/github-intelligence
python3 scripts/github_intelligence_query.py --data ~/Data/github-intelligence "Hermes" --limit 5
```
