#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
grep -q 'fs-survey' "$HERE/SKILL.md" && grep -q 'fs-classify' "$HERE/SKILL.md"
grep -q 'fs-reorganize' "$HERE/SKILL.md" && grep -q 'fs-index' "$HERE/SKILL.md"
grep -qi 'approval\|checkpoint' "$HERE/SKILL.md"
grep -qi 'loop' "$HERE/SKILL.md"
grep -q 'exit 42\|exit code 42\|42' "$HERE/SKILL.md"
echo "PASS"
