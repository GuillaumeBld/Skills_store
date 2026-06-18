#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
echo "x" > "$T/a.md"; mkdir -p "$T/junkdir"
cat > "$T/manifest.csv" <<EOF
current_path,kind,size,category,proposed_action,target_path,confidence,note
$T/a.md,document,2,Academic_Work,move,Academic_Work/a.md,0.9,
$T/junkdir,dir,0,Junk_Candidate,quarantine,,0.5,empty
EOF
# dry-run changes nothing
bash "$HERE/scripts/reorganize.sh" "$T/manifest.csv" --base "$T" > /dev/null
[ -f "$T/a.md" ]
# apply
bash "$HERE/scripts/reorganize.sh" "$T/manifest.csv" --base "$T" --apply > /dev/null
[ -f "$T/Academic_Work/a.md" ] && [ ! -f "$T/a.md" ]
[ -d "$T/_REVIEW_DELETE/junkdir" ]
[ -f "$T/moves.log" ] && [ -f "$T/undo.sh" ]
bash "$T/undo.sh"                       # undo restores
[ -f "$T/a.md" ] && [ ! -f "$T/Academic_Work/a.md" ]
echo "PASS"
