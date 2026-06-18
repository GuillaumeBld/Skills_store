#!/usr/bin/env bash
# fs-index reindex — incremental refresh of the RAG layer.
# Computes per-file content hashes (skipping noise dirs), records them under
# .filesystem-index/hashes for change detection, then rebuilds the index. On
# reruns, an unchanged hash set means the catalog/MAP are already current.
#
# Usage: reindex.sh [TARGET] [--wire]   (default TARGET: $HOME)
set -euo pipefail

TARGET="$HOME"; WIRE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --wire) WIRE="--wire"; shift ;;
    *) TARGET="$1"; shift ;;
  esac
done
TARGET="$(cd "$TARGET" && pwd)"
HERE="$(cd "$(dirname "$0")" && pwd)"
IDX="$TARGET/.filesystem-index"
mkdir -p "$IDX"
NEW="$IDX/hashes.new"; CUR="$IDX/hashes"

python3 - "$TARGET" > "$NEW" <<'PY'
import hashlib, os, sys
target = sys.argv[1]
SKIP = {"node_modules", ".git", ".venv", "venv", "site-packages", "__pycache__",
        ".Trash", "Library", "System", "usr", "bin", "private", ".cache",
        ".npm", ".filesystem-index"}
for root, dirs, files in os.walk(target):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in sorted(files):
        p = os.path.join(root, f)
        try:
            h = hashlib.sha256()
            with open(p, "rb") as fh:
                for chunk in iter(lambda: fh.read(65536), b""):
                    h.update(chunk)
            print(f"{h.hexdigest()}  {os.path.relpath(p, target)}")
        except OSError:
            pass
PY

if [ -f "$CUR" ] && cmp -s "$NEW" "$CUR"; then
  rm -f "$NEW"
  echo "no changes since last reindex — index is current"
  exit 0
fi

mv "$NEW" "$CUR"
echo "changes detected — rebuilding index"
bash "$HERE/build_index.sh" "$TARGET" $WIRE
