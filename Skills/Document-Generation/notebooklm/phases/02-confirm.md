# Phase 2: Save & Confirm

Save state files and get user confirmation before processing.

## Contents

- Step 1: Save State Files
- Step 2: Validate State Files
- Step 3: Confirmation Summary

---

## Step 1: Save State Files

Write these 3 files to the **project root** (not the skill directory). All 3 must be written BEFORE any NotebookLM operations.

### File 1: `.notebook-decks-meta.json`

```json
{
  "version": "1.0",
  "created_at": "<ISO timestamp>",
  "updated_at": "<ISO timestamp>",
  "source_path": "<user provided path>",
  "output_path": "<output directory>",
  "primary_file_types": [".md"],
  "grouping": "individual_file",
  "companion_files": {
    "enabled": true,
    "types": [".png"],
    "pairing": "positional"
  },
  "shared_files": ["/path/to/shared/assets/"],
  "naming_convention": "{filename}_{format}",
  "output_formats": ["slide_deck"],
  "format_options": {
    "slide_deck": { "format": "detailed_deck", "length": "default" }
  },
  "focus_prompt": "<user prompt or null>",
  "clean_watermarks": true,
  "batches": [
    {
      "batch_id": "batch_001",
      "name": "<descriptive name>",
      "primary_file": "<path to primary file>",
      "companion_files": ["<path to companion>"],
      "shared_files": ["<path to shared>"],
      "status": "pending",
      "notebook_id": null,
      "outputs": {}
    }
  ]
}
```

Fill in ALL fields with the actual values from the user's answers. Generate the full `batches` array based on the grouping logic and file analysis.

### File 2: `tasks.md`

```markdown
# Notebook Decks - Task Progress

## Configuration
- Source: <source_path>
- Output: <output_path>
- Primary files: <types>
- Grouping: <grouping>
- Companions: <companion_config>
- Shared files: <shared_files or "none">
- Formats: <format_list>
- Prompt: <focus_prompt or "none">
- Watermark cleaning: <yes/no>

## Tasks

| # | Batch | Primary File | Companions | Shared | Status | Notebook ID | Outputs |
|---|-------|-------------|------------|--------|--------|-------------|---------|
| 1 | <name> | <file> | <companion_files> | <count> shared | pending | - | - |
| 2 | <name> | <file> | <companion_files> | <count> shared | pending | - | - |
...

## Log
- [<ISO timestamp>] Session created with <N> batches
```

### File 3: `generation-config.jsonl`

One JSON object per line, one per batch:

```
{"batch_id":"batch_001","name":"<name>","primary_file":"<path>","companion_files":["<path>"],"shared_files":["<path>"],"formats":["slide_deck"],"format_options":{"slide_deck":{"format":"detailed_deck","length":"default"}},"focus_prompt":"<prompt>","status":"pending"}
{"batch_id":"batch_002","name":"<name>","primary_file":"<path>","companion_files":["<path>"],"shared_files":["<path>"],"formats":["slide_deck"],"format_options":{"slide_deck":{"format":"detailed_deck","length":"default"}},"focus_prompt":"<prompt>","status":"pending"}
```

---

## Step 2: Validate State Files

After writing all 3 files, verify they're valid:

1. `.notebook-decks-meta.json` — Valid JSON, all required fields present, batch count > 0
2. `tasks.md` — Markdown table renders correctly, row count matches batch count
3. `generation-config.jsonl` — Each line is valid JSON, line count matches batch count

If validation fails, fix the file before proceeding.

---

## Step 3: Confirmation Summary

Display a formatted summary of ALL decisions to the user:

```
=== Notebook Decks Configuration ===
Source:       <path>
Output:       <output path>
Primary type: <types> (<count> files)
Grouping:     <grouping> (<N> notebooks)
Companions:   <types> (<pairing>) or "none"
Shared files: <path> (<count> files) or "none"
Format:       <format(s)> (<sub-options>)
Prompt:       "<focus_prompt>" or "none"
Watermark:    auto-clean enabled/disabled

=== First 3 Batches Preview ===
Batch 1: "<name>"
  - Primary: <filename>
  - Companion: <filename(s)> or "none"
  - Shared: <count> files or "none"

Batch 2: "<name>"
  - Primary: <filename>
  - Companion: <filename(s)> or "none"
  - Shared: <count> files or "none"

Batch 3: "<name>"
  - Primary: <filename>
  - Companion: <filename(s)> or "none"
  - Shared: <count> files or "none"

... and <remaining> more batches

Proceed? (yes / edit configuration)
```

**GATE: Wait for the user to say "yes" or "proceed". Do NOT continue until the user explicitly confirms. If the user says "edit", go back to the relevant step in Phase 1.**

---

## Phase 2 Complete

User confirmed. State files saved.

**Phase 2 done.** Return to SKILL.md routing — next is Phase 3.
