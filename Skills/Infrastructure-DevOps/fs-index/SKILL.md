---
name: fs-index
description: "Build a grep-first, agent-navigable RAG layer over a directory (default $HOME): per-area INDEX.md files, a machine-queryable .filesystem-index/catalog.jsonl (path/kind/category/summary/keywords per line), and a master FILESYSTEM_MAP.md (<=25KB) that explicitly links every INDEX.md and answers 'where do I find X'. With --wire it makes the map auto-discoverable by inserting a pointer into ~/.claude/CLAUDE.md and writing AGENTS.md. reindex.sh refreshes incrementally via content-hash change detection. Use to make a machine agent-navigable, build a filesystem map, or create a RAG index of files. Final stage of the system-organizer suite."
---

# fs-index — the RAG at the base

Makes a directory navigable for both humans and agents. **Additive**: it creates
index files and changes nothing else.

## Usage

```bash
bash scripts/build_index.sh [TARGET] [--wire]   # full build (default $HOME)
bash scripts/reindex.sh    [TARGET] [--wire]    # incremental refresh
```

`--wire` inserts an idempotent pointer block into `~/.claude/CLAUDE.md` and writes
`AGENTS.md` — do this for a real home/root run so agents auto-discover the map.
Omit it for ad-hoc indexing of an arbitrary directory.

## What it produces (tiered, grep-first)

- **Tier 1 — `FILESYSTEM_MAP.md`** (master, ≤25 KB): top-level legend, a
  **"Where do I find X?"** table, and **explicit links to every area `INDEX.md`**.
- **Tier 2 — per-area `INDEX.md`**: each top-level area lists its items + summaries.
- **Tier 3 — `.filesystem-index/catalog.jsonl`**: one JSON record per item
  (`path, kind, category, size, mtime, summary, keywords`) — query with `rg`/`jq`.
- **Tier 0 — auto-discovery** (`--wire`): `~/.claude/CLAUDE.md` pointer + `AGENTS.md`.

## Design rationale (research-backed)

- **Grep-first, not vectors.** Lexical retrieval is ~<0.02s with zero index-build
  cost and competitive quality; a semantic/vector tier earns its keep only at
  scale. So this builds the markdown+JSONL backbone and leaves embeddings as an
  opt-in upgrade (Tier 4, below).
- **25 KB MAP budget.** Mirrors Claude Code's MEMORY.md (index loaded each
  session; detail read on demand). The MAP stays small; detail lives in INDEX.md.
- **Explicit links are mandatory.** Agents do NOT auto-walk-up the tree to find the
  "nearest" INDEX.md — unlinked detail files are invisible, so the MAP links them all.

## Tier 4 — semantic search (deferred, opt-in)

If lexical search proves insufficient for semantic queries, layer an existing
on-device hybrid engine over the *same* summaries rather than building one:
- **qmd** (BM25 + vector + LLM rerank; CLI + MCP), or
- **claude-context** (MCP, hybrid, Merkle-tree incremental reindex).

## Freshness

`reindex.sh` hashes file contents into `.filesystem-index/hashes`; an unchanged
hash set means the index is already current, otherwise it rebuilds. Run manually,
from a `launchd`/cron schedule, or a file-watcher.

System-agnostic (macOS + Linux). Run `bash tests/test_index.sh`.
