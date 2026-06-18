---
name: fs-reorganize
description: "Apply an approved manifest.csv as REVERSIBLE file moves: moves items into category folders, quarantines junk to _REVIEW_DELETE/ (never deletes), logs every move to moves.log, and generates an undo.sh that reverses everything. Defaults to dry-run; --apply executes. Collisions get a numeric suffix, never overwrite. Use to reorganize files safely, clean up a directory with an undo path, or execute a classification manifest. Third stage of the system-organizer suite — runs only after a human approves the manifest."
---

# fs-reorganize

Executes the move plan from `fs-classify` — safely and reversibly. Nothing is ever
deleted; the worst case is fully undoable.

## Usage

```bash
bash scripts/reorganize.sh MANIFEST.csv [--base DIR] [--apply]
```

- **Dry-run by default** — prints the planned operations and touches nothing.
- `--apply` — executes the moves.
- `--base DIR` — root for relative `target_path`s (default: the manifest's dir).

## Behavior

- `proposed_action=move` → `mv` into `<base>/<target_path>` (creates dirs as needed).
- `proposed_action=quarantine` → `mv` into `<base>/_REVIEW_DELETE/` (**never `rm`**).
- `proposed_action=keep` → left in place.
- **Collisions** get ` (2)`, ` (3)`, … before the extension — never overwrite.
- Every applied move is appended to `moves.log` (`orig<TAB>new`).
- An executable `undo.sh` is generated that reverses every move in reverse order.

## Safety guarantees

- No user content is deleted. Quarantine is a move, reviewable later.
- `undo.sh` makes the whole operation reversible — verify it round-trips on a
  sample before trusting a large run.
- Idempotent-safe: re-running re-reads the manifest; already-moved sources are
  skipped as missing.

## Recommended flow

1. Review `classification_report.md` (from `fs-classify`) and approve the manifest.
2. Dry-run: `reorganize.sh manifest.csv --base ~` → inspect planned ops.
3. Apply: add `--apply`.
4. Spot-check, then confirm `bash undo.sh` restores a few items before continuing.

System-agnostic (macOS + Linux). Run `bash tests/test_reorganize.sh`.
