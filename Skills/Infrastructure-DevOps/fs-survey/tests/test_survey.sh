#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/proj/node_modules/foo" "$T/proj/.git" "$T/empty_dir"
echo '{}' > "$T/proj/package.json"; echo "# readme" > "$T/proj/README.md"
echo "hello" > "$T/notes.md"; printf '\x89PNG' > "$T/pic.png"
bash "$HERE/scripts/survey.sh" "$T" > "$T/out.txt"
grep -q '"kind": *"code_unit"' "$T/survey.json"        # proj is ONE unit
! grep -q 'node_modules' "$T/survey.json"               # noise skipped
grep -q '"kind": *"junk_candidate"' "$T/survey.json"    # empty_dir flagged
grep -q '"kind": *"document"' "$T/survey.json"          # notes.md
grep -q 'total_units' "$T/out.txt"
echo "PASS"
