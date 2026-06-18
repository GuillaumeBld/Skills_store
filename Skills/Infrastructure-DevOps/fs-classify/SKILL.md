---
name: fs-classify
description: "Classify the units of a directory into a taxonomy with dynamic per-item depth (read README for code projects, sample contents for documents, filename-only for media/archives), producing a reviewable manifest.csv + classification_report.md. Resumable and batchable so it runs under /loop until every in-scope file is read and classified (exit code 42 = coverage complete). Read-only — proposes moves, never performs them. Use when you need to categorize a directory, build a file manifest, or classify files before reorganizing. Second stage of the system-organizer suite."
---

# fs-classify

Turns a directory's units into a **reviewable plan** — which category each item
belongs to, and whether it should move or be quarantined. Read-only: it samples
content but changes nothing. Output feeds `fs-reorganize`.

## Usage

```bash
python3 scripts/classify.py TARGET \
  [--out manifest.csv] [--report classification_report.md] \
  [--taxonomy taxonomy.default.json] [--batch N] [--resume]
```

## Loop-until-complete

Designed to run under `/loop`. Each call classifies up to `--batch` (default 50)
not-yet-seen units, appends to `manifest.csv`, then exits:

- **exit 0** — classified ≥1 new unit this run (more may remain) → loop continues.
- **exit 42** — every in-scope unit is already in the manifest → loop **stops**.

`--resume` makes it idempotent: it skips paths already present in `manifest.csv`,
so the loop survives interruption/restart and never re-reads a classified file.

## Dynamic-depth policy (the core IP)

| kind | depth → label source |
|------|----------------------|
| `code_unit` | read `README`/`package.json`/`pyproject.toml` only → name, stack, purpose |
| `document` | sample first ~4 KB of text-readable docs → keywords + category |
| `media` | filename + extension (no content read; OCR is out of scope) |
| `archive` | filename + extension |
| `junk_candidate` | flagged → `proposed_action=quarantine`, never read |

Categories are scored by keyword + extension hits; the best-scoring category wins
with a `confidence` in `[0.4, 0.95]`. Low-confidence rows are surfaced in the
report for human review.

## Output

- `manifest.csv` — columns `current_path,kind,size,category,proposed_action,target_path,confidence,note`; `proposed_action` ∈ `move|keep|quarantine`.
- `classification_report.md` — grouped by category, with **Proposed deletions /
  quarantine** and **Low-confidence — needs review** sections up top.

## Taxonomy

Default categories (`taxonomy.default.json`): `Academic_Work, Business_Work,
Development_Projects, Dev_Tools, Personal_Admin, Media_Documents, Media_Photos,
Junk_Candidate`. Override per system with `--taxonomy <file>` (same shape:
`{categories: {Name: {keywords:[], ext:[]}}, fallback: "Name"}`).

## Notes

- **Read-only.** Proposes; never moves. Mutation is `fs-reorganize`'s job, behind
  an approval gate.
- System-agnostic; works on macOS and Linux. Run `bash tests/test_classify.sh`.
