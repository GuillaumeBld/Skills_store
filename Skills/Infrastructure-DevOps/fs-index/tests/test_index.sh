#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/Academic_Work"; echo "esg study" > "$T/Academic_Work/paper.md"
bash "$HERE/scripts/build_index.sh" "$T"
[ -f "$T/FILESYSTEM_MAP.md" ]
[ -f "$T/.filesystem-index/catalog.jsonl" ]
[ -f "$T/Academic_Work/INDEX.md" ]
python3 -c "import json,sys; [json.loads(l) for l in open('$T/.filesystem-index/catalog.jsonl')]"  # valid JSONL
grep -q 'Academic_Work/INDEX.md' "$T/FILESYSTEM_MAP.md"   # MAP explicitly links detail
[ "$(wc -c < "$T/FILESYSTEM_MAP.md")" -le 25600 ]          # 25KB budget
# reindex is incremental and idempotent
bash "$HERE/scripts/reindex.sh" "$T" > /dev/null
[ -f "$T/.filesystem-index/hashes" ]
echo "PASS"
