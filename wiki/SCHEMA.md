# Wiki Schema

> This file tells the LLM how to maintain this wiki. Read it at the start of every session that touches wiki pages.

## Project

- **Name**: Hermes Agent
- **Domain**: Multi-platform AI agent framework (CLI, gateway, TUI, ACP, plugins, skills, cron, kanban)

## Directory structure

```
wiki/
├── SCHEMA.md          ← you are here (LLM instructions)
├── index.md           ← content catalog, organized by type
├── log.md             ← chronological operations log
├── sources/           ← summaries of ingested documents
├── entities/          ← concrete things (tools, services, APIs, tables, configs)
├── concepts/          ← patterns, principles, architectural ideas
├── decisions/         ← architecture decision records (ADRs)
├── guides/            ← how-tos, runbooks, procedures
└── assets/            ← images, diagrams, attachments
```

## Page conventions

### Filenames

- **Kebab-case**, lowercase: `api-rate-limiting.md`, `postgres-connection-pool.md`
- Singular nouns for entities: `redis-cache.md` not `redis-caches.md`
- Verb-noun for guides: `deploy-to-production.md`, `rotate-api-keys.md`
- Decisions use numbered prefix: `0001-use-postgres-over-mysql.md`

### Frontmatter

Every page MUST have YAML frontmatter:

```yaml
---
title: Human-Readable Page Title
type: source | entity | concept | decision | guide
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [relevant, tags]
aliases: [alternate-name, abbreviation]
sources: ["[[source-page]]"]
status: active | draft | superseded | archived
---
```

### Links

Use Obsidian-style wikilinks exclusively:

- `[[page-name]]` for standard links
- `[[page-name|display text]]` for aliased links
- `[[page-name#section]]` for section links
- Never use markdown-style `[text](url)` for internal wiki links (reserve for external URLs)

### Page structure

Every page follows this skeleton:

```markdown
---
(frontmatter)
---

# Title

One-paragraph summary of what this page covers.

## Content sections
(varies by page type — see below)

## Related
- [[linked-page-1]]
- [[linked-page-2]]
```

## Page types

### Source (`sources/`)

Summary of an ingested document, article, file, or conversation.

```markdown
## Key points
(bulleted takeaways)

## Detailed notes
(expanded content, preserving important specifics)

## Entities mentioned
(list of [[entity]] links — create pages if they don't exist)

## Concepts discussed
(list of [[concept]] links)
```

### Entity (`entities/`)

A concrete thing: tool, service, API, library, database table, config file, environment.

```markdown
## What it is
(one-paragraph definition)

## How it's used in this project
(project-specific context, configuration, gotchas)

## Key details
(version, endpoints, schemas, config values — whatever's relevant)

## Related
```

### Concept (`concepts/`)

A pattern, principle, or architectural idea.

```markdown
## Definition
(what the concept means in general)

## Application here
(how this project uses or implements it, with specifics)

## Tradeoffs
(pros, cons, alternatives considered)

## Related
```

### Decision (`decisions/`)

An architecture decision record. Filename: `NNNN-short-title.md`.

```markdown
## Status
Proposed | Accepted | Superseded by [[NNNN-newer-decision]]

## Context
(what problem or question prompted this decision)

## Decision
(what was decided, concretely)

## Consequences
(what changes, what becomes easier, what becomes harder)

## Related
```

### Guide (`guides/`)

A how-to or runbook.

```markdown
## Prerequisites
(what you need before starting)

## Steps
1. Step one
2. Step two
...

## Troubleshooting
(common issues and fixes)

## Related
```

## Operations

### Obsidian (human viewer)

During **project / wiki setup**, install Obsidian if it is missing (macOS: `brew install --cask obsidian` when Homebrew exists; Windows: `winget install Obsidian.Obsidian` when available; else https://obsidian.md/download ). Then open `wiki/` as a vault.

### Ingest

When the user provides a new source (document, article, code file, conversation):

1. **Read** the source thoroughly
2. **Discuss** key takeaways with the user
3. **Create** `sources/<source-name>.md` with summary and frontmatter
4. **Update or create** entity pages for each concrete thing mentioned
5. **Update or create** concept pages for each pattern or idea discussed
6. **Create** decision pages if architectural choices are documented
7. **Update** `index.md` — add new pages under the correct category
8. **Append** to `log.md`: `## [YYYY-MM-DD] ingest | Source Title`
9. **Review** changes with the user before committing

A single source typically touches 5-15 wiki pages. Take your time.

### Ingest existing docs

When migrating a project's existing `docs/` directory:

1. **Scan** the docs directory and list all files
2. **Group** related files (e.g., all investigation docs for one feature)
3. **Read** each group and identify: entities, concepts, decisions, procedures
4. **Compile** groups into consolidated wiki pages (don't just copy — synthesize)
5. **Cross-reference** with `[[wikilinks]]` across all new pages
6. **Build** the index from scratch reflecting the compiled content
7. **Log** the migration as a batch ingest
8. **Do not delete** the original `docs/` — the user decides when to remove it

### Query

When the user asks a question against the wiki:

1. **Read** `index.md` to find relevant pages
2. **Read** the relevant pages
3. **Synthesize** an answer with `[[wikilinks]]` as citations
4. **Optionally file back**: if the answer represents new synthesis (comparison, analysis, connection), ask the user if it should become a wiki page

### Lint

Periodic health check. Run when asked or suggest after major ingests.

1. **Orphan pages**: pages with zero inbound `[[wikilinks]]` from other pages
2. **Dead links**: `[[wikilinks]]` pointing to pages that don't exist — create stubs or remove
3. **Stale pages**: pages not updated in 30+ days whose source material has changed
4. **Index drift**: pages that exist on disk but aren't listed in `index.md`
5. **Missing backlinks**: page A links to page B, but page B doesn't link back when it should
6. **Contradictions**: same entity or concept described differently across pages
7. **Thin pages**: pages with fewer than 3 sentences of content (expand or merge)

Report findings as a checklist. Fix with user approval.

## Style rules

- Write in clear, direct prose. No marketing language.
- Use the project's terminology consistently (document aliases in frontmatter).
- Prefer concrete specifics over vague summaries. Include: version numbers, config values, endpoint paths, file paths, command examples.
- When in doubt, create a new page rather than cramming content into an existing one. Pages are cheap; finding information in a bloated page is not.
- Every claim should be traceable to a source via `[[wikilinks]]`. If you can't cite it, flag it.
- Update the `updated` date in frontmatter whenever you modify a page.

## Relationship to other project files

- **AI_SESSION_MEMORY.md**: Session-level breadcrumbs. The wiki is the compiled, persistent version.
- **AI_RUNBOOK.md**: Operational procedures. These may graduate into `wiki/guides/` pages.
- **AGENTS.md**: Project-level agent instructions. SCHEMA.md is wiki-specific; both coexist.
- **SimpleMem**: Fast key-value recall. The wiki is structured long-form. Both serve different purposes.
