#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
echo "ESG bank systemic risk regression" > "$T/esg_paper.md"
echo "Guillaume Bolivard resume" > "$T/Resume_EN.txt"
mkdir -p "$T/TO_BE_DELETED"
M="$T/manifest.csv"

# --- emit: harness hands the agent a batch of units with snippets + hints ---
python3 "$HERE/scripts/classify.py" emit "$T" --out "$T/batch.json"
python3 - "$T/batch.json" <<'PY'
import json,sys
b=json.load(open(sys.argv[1]))
assert len(b)==3, b
u={x["name"]:x for x in b}
assert "snippet" in u["esg_paper.md"] and "esg" in u["esg_paper.md"]["snippet"].lower()
assert u["TO_BE_DELETED"]["kind"]=="junk_candidate"
assert "hint_category" in u["esg_paper.md"]
print("emit-ok")
PY

# --- the agent decides (simulated here); record writes the manifest ---
cat > "$T/decisions.json" <<EOF
[
 {"path":"$T/esg_paper.md","category":"Academic_Work","proposed_action":"move","target_path":"Academic_Work/esg_paper.md","confidence":0.95,"note":"ESG systemic risk study"},
 {"path":"$T/Resume_EN.txt","category":"Personal_Admin","proposed_action":"move","target_path":"Personal_Admin/Resume_EN.txt","confidence":0.95,"note":"resume"},
 {"path":"$T/TO_BE_DELETED","category":"Junk_Candidate","proposed_action":"quarantine","target_path":"","confidence":0.5,"note":"empty scratch"}
]
EOF
python3 "$HERE/scripts/classify.py" record "$T" --decisions "$T/decisions.json" --out "$M"
head -1 "$M" | grep -q 'current_path,kind,size,category,proposed_action,target_path,confidence,note'
grep -q 'Academic_Work' "$M" && grep -q 'Personal_Admin' "$M" && grep -q 'quarantine' "$M"

# report regenerated from manifest
python3 "$HERE/scripts/classify.py" report "$T" --out "$M" --report "$T/report.md"
grep -q 'Proposed deletions' "$T/report.md"

# --- loop-until-complete: nothing left to emit → exit 42 ---
set +e; python3 "$HERE/scripts/classify.py" emit "$T" --out "$T/batch2.json" --resume; rc=$?; set -e
[ "$rc" -eq 42 ]
echo "PASS"
