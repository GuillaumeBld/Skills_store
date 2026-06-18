---
name: fs-classify
description: "Agent-driven classification harness for a directory's units. Does NOT decide by keyword alone — it enumerates units, extracts a dynamic-depth snippet per item (README for code projects, sampled text for documents, filename/metadata for media), and hands batches to an AI agent that identifies and categorizes each with real judgment while the taxonomy improves as we go. Resumable/batchable so it runs under /loop until every in-scope unit is classified (emit exits 42 when coverage is complete). Read-only — proposes moves, never performs them. Use to categorize a directory, build a file manifest, or classify files before reorganizing. Second stage of the system-organizer suite."
---

# fs-classify (agent-driven)

The classifier's *judgment* is the agent's; this harness handles enumeration,
dynamic-depth content extraction, and bookkeeping. It is read-only on your files.

## The loop (emit → agent judges → record)

```bash
# 1. Harness emits the next batch of unclassified units, each with a content
#    snippet (dynamic depth) and a heuristic hint_category to assist:
python3 scripts/classify.py emit  TARGET --out batch.json --batch 50 --resume
#    → exit 0 with work; exit 42 when nothing remains (loop stop signal).

# 2. The AGENT reads batch.json, identifies each unit, and writes decisions.json:
#    [{"path": "...", "category": "...", "proposed_action": "move|quarantine|keep",
#      "target_path": "Category/name", "confidence": 0.0-1.0, "note": "..."}]
#    The agent may introduce a NEW category here (taxonomy grows as we go) and may
#    re-judge earlier low-confidence units by including them again.

# 3. Harness records decisions into the manifest (idempotent per path):
python3 scripts/classify.py record TARGET --decisions decisions.json --out manifest.csv

# 4. Regenerate the human report at any time:
python3 scripts/classify.py report TARGET --out manifest.csv --report classification_report.md
```

Repeat 1–3 under `/loop` until `emit` returns **exit 42**.

## Dynamic-depth snippet policy (what the agent sees per item)

| kind | snippet source (never slurps huge files) |
|------|------------------------------------------|
| `code_unit` | README/`package.json`/`pyproject.toml` (first 2 KB) + top-level file list |
| `document` | first ~4 KB of text-readable docs (`.md .txt .csv .json .eml …`) |
| `media` | filename + extension (no content read; OCR out of scope) |
| `archive` | filename + extension |
| `junk_candidate` | flagged; agent confirms quarantine |

## Taxonomy: seed + grow

`taxonomy.default.json` seeds the categories (`Academic_Work, Business_Work,
Development_Projects, Dev_Tools, Personal_Admin, Media_Documents, Media_Photos,
Junk_Candidate`). The agent **adds or splits a category only when the data clearly
demands it** — folders serve the *human* mental model, while the AI navigates via
the index (see `fs-index`), so the two audiences never conflict. Override the seed
per-system with `--taxonomy <file>`.

## Output

- `manifest.csv` — `current_path,kind,size,category,proposed_action,target_path,confidence,note`.
- `classification_report.md` — grouped by category; **Proposed deletions** and
  **Low-confidence — needs review** sections up top for the approval checkpoint.

## Notes

- **Read-only.** Proposes; never moves. Mutation is `fs-reorganize`'s job, gated
  on human approval of the manifest.
- System-agnostic (macOS + Linux). Run `bash tests/test_classify.sh`.
