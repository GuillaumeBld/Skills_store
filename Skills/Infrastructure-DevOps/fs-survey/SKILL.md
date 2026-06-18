---
name: fs-survey
description: "Survey and map any directory tree (default $HOME), separating user-content signal from OS/dependency noise. Treats code projects as single units and never descends into node_modules/.git/venvs. Emits survey.json (machine-readable unit list) plus a human summary. Use when you need to recon a system before organizing it, answer 'what's on this machine', map a directory tree, or produce the input for fs-classify. First stage of the system-organizer suite."
---

# fs-survey

Read-only reconnaissance of a directory tree. Produces the **unit list** that the
rest of the system-organizer suite (`fs-classify` → `fs-reorganize` → `fs-index`)
consumes.

## Usage

```bash
bash scripts/survey.sh [TARGET_DIR]   # default: $HOME
```

Writes `<TARGET>/survey.json` and prints a summary (total units, size, by-kind
counts).

## What it does

- Walks the **top level** of `TARGET` and classifies each entry as a *unit*.
- A directory containing a code marker (`.git`, `package.json`, `pyproject.toml`,
  `Cargo.toml`, `go.mod`, `requirements.txt`, venv, …) becomes ONE `code_unit` —
  it is **not** descended into. This is why a 475k-file machine surveys in seconds.
- Loose files are typed by extension: `document | media | archive | other`.
- Empty dirs, `.DS_Store`, and scratch names (`test*`, `TEMP_*`, `TO_BE_DELETED`,
  `tmp*`, `untitled*`) become `junk_candidate`.
- Dependency/OS dirs are skipped entirely (recorded under `skipped_noise_dirs`).

## Output schema (`survey.json`)

```json
{
  "target": "/abs/path",
  "total_units": 88,
  "units": [{"path": "...", "kind": "code_unit", "size": 1234, "mtime": 1700000000}],
  "skipped_noise_dirs": ["/abs/path/node_modules"]
}
```

`kind` ∈ `code_unit | document | media | archive | dir | junk_candidate | other`.

## Skip-list (never descended into)

`node_modules`, `.git`, `.venv`/`venv`/`site-packages`, `__pycache__`,
`~/Library`, `/System`, `/usr`, `/bin`, `/private`, `.cache`, `.npm`, `.Trash`.

## Notes

- Purely **read-only** — creates only `survey.json`.
- System-agnostic: works on macOS and Linux; target dir is an argument.
- Run `bash tests/test_survey.sh` to validate.
