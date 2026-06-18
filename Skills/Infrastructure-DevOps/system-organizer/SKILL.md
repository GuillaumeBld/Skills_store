---
name: system-organizer
description: "Take ANY system (macOS or Linux, default $HOME) and make it simultaneously human-legible, AI-navigable, and safely manipulable. Orchestrates the fs-* suite — fs-survey → fs-classify (agent-driven, loop-until-complete) → [human approval checkpoint] → fs-reorganize (reversible) → fs-index (grep-first RAG layer + auto-discovery wiring). Read-only until the user approves the manifest; every move is reversible (undo.sh) and junk is quarantined, never deleted. Use when asked to organize/clean/index a machine, give a computer a 'RAG at its base', or make a system human + AI friendly."
---

# system-organizer

Turns a messy machine into one where any agent — and any human — instantly knows
where everything is, and can act on it safely. One pipeline, four focused skills,
one hard safety gate.

## Pipeline

```
fs-survey  →  fs-classify  →  [APPROVAL CHECKPOINT]  →  fs-reorganize  →  fs-index
(map tree)   (agent judges,    (human signs off on        (reversible       (grep-first
 signal vs    loop-until-       the manifest; nothing       moves, undo.sh,   RAG layer +
 noise)       complete)         has moved yet)              quarantine)       auto-discovery)
```

### 1. Survey (read-only)
`bash fs-survey/scripts/survey.sh TARGET` → `survey.json` (units; code projects
and dependency trees collapsed to single units / skipped).

### 2. Classify — agent-driven, loop-until-complete (read-only)
Run under **`/loop`** (dynamic self-paced). Each iteration:
```
fs-classify/scripts/classify.py emit   TARGET --out batch.json --resume   # exit 42 ⇒ done
# agent reads batch.json, identifies each unit, writes decisions.json
fs-classify/scripts/classify.py record TARGET --decisions decisions.json
```
- The **agent** identifies every in-scope unit with real judgment (the script only
  enumerates + extracts snippets + records).
- The **taxonomy grows as we go**; earlier low-confidence units may be re-emitted
  and re-judged so classifications sharpen with coverage.
- `emit` returns **exit code 42** when every in-scope unit is classified — the
  signal to **stop looping**.

### 3. APPROVAL CHECKPOINT (hard gate)
Present `classification_report.md` — especially **Proposed deletions / quarantine**
and **Low-confidence — needs review**. **Nothing moves until the user approves.**
This is non-negotiable: stages 1–2 are strictly read-only.

### 4. Reorganize (reversible — only after approval)
`bash fs-reorganize/scripts/reorganize.sh manifest.csv --base TARGET --apply`
- Moves into category folders; junk → `_REVIEW_DELETE/` (**never `rm`**).
- Logs `moves.log`; generates `undo.sh`. Verify it round-trips on a sample.

### 5. Index (additive)
`bash fs-index/scripts/build_index.sh TARGET --wire`
- Builds `FILESYSTEM_MAP.md` (≤25 KB) + per-area `INDEX.md` + `catalog.jsonl`.
- `--wire` adds the pointer to `~/.claude/CLAUDE.md` + `AGENTS.md` for
  auto-discovery. Keep fresh with `fs-index/scripts/reindex.sh`.

## Non-negotiable constraints

- **Read-only until approval.** Survey + classify never mutate user files.
- **Reversible.** Every move logged + `undo.sh`. Collisions suffixed, never overwritten.
- **Never delete.** Junk is quarantined to `_REVIEW_DELETE/`.
- **Skip noise.** `node_modules`, `.git`, venvs, `~/Library`, `/System`, … are never
  descended into; code projects are single units.
- **Secrets:** record credential *locations* only; never read or copy contents.
- **System-agnostic.** Target is an argument (default `$HOME`); runs on any node.

## Why split this way

Split by **function, not audience**: every artifact serves humans and agents at
once. Folders match the *human* mental model; the *AI* navigates via the index
(catalog + MAP), so the two never conflict.

Run `bash tests/test_orchestrator.sh` to validate the documented contract.
