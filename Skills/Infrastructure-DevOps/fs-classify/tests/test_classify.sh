#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
echo "ESG bank systemic risk regression" > "$T/esg_paper.md"
echo "Guillaume Bolivard resume" > "$T/Resume_EN.txt"
mkdir -p "$T/TO_BE_DELETED"
python3 "$HERE/scripts/classify.py" "$T" --out "$T/manifest.csv" --report "$T/report.md"
head -1 "$T/manifest.csv" | grep -q 'current_path,kind,size,category'
grep -qi 'Academic_Work\|Personal_Admin' "$T/manifest.csv"   # esg or resume categorized
grep -q 'quarantine' "$T/manifest.csv"                        # TO_BE_DELETED flagged
grep -q 'Proposed deletions' "$T/report.md"
# loop-until-complete: a second --resume run finds nothing left → exit 42
set +e; python3 "$HERE/scripts/classify.py" "$T" --out "$T/manifest.csv" --report "$T/report.md" --resume; rc=$?; set -e
[ "$rc" -eq 42 ]                                              # coverage complete signal
echo "PASS"
