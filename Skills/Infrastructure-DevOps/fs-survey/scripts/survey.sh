#!/usr/bin/env bash
# fs-survey — map a directory tree, separating signal (user content) from noise
# (OS/dependency dirs). Treats code projects as ONE unit; never descends into deps.
#
# Usage: survey.sh [TARGET_DIR]   (default: $HOME)
# Writes: <TARGET>/survey.json   +   a human summary to stdout
set -euo pipefail

TARGET="${1:-$HOME}"
TARGET="$(cd "$TARGET" && pwd)"   # absolute, no trailing slash

python3 - "$TARGET" <<'PY'
import json, os, sys, time

target = sys.argv[1]

# Never descend into / treat as noise (Global skip-list).
SKIP_DIRS = {"node_modules", ".git", ".venv", "venv", "site-packages",
             "__pycache__", ".Trash", "Library", "System", "usr", "bin",
             "private", ".cache", ".npm"}
# Markers that make a directory a single "code_unit".
CODE_MARKERS = {".git", "package.json", "pyproject.toml", "Cargo.toml",
                "go.mod", "requirements.txt", "Gemfile", "pom.xml",
                "build.gradle", ".venv", "venv"}
JUNK_NAMES = {".DS_Store", ".localized", "Thumbs.db"}
JUNK_PREFIXES = ("test", "tmp", "temp", "TEMP_", "TO_BE_DELETED",
                 "TEMP_REMOVAL", "untitled", "Untitled")

DOC_EXT = {".docx", ".pdf", ".pptx", ".md", ".csv", ".xlsx", ".ipynb",
           ".txt", ".eml", ".doc", ".ppt", ".xls", ".rtf", ".pages",
           ".key", ".numbers", ".json", ".yml", ".yaml"}
MEDIA_EXT = {".png", ".jpg", ".jpeg", ".gif", ".mp4", ".webm", ".mov",
             ".tif", ".tiff", ".svg", ".heic", ".webp", ".mp3", ".wav", ".m4a"}
ARCHIVE_EXT = {".zip", ".dmg", ".pkg", ".tar", ".gz", ".tgz", ".bz2", ".7z", ".rar"}


def is_junk_name(name):
    if name in JUNK_NAMES:
        return True
    low = name.lower()
    return any(low.startswith(p.lower()) for p in JUNK_PREFIXES)


def dir_is_empty(path):
    try:
        return not any(os.scandir(path))
    except OSError:
        return False


def is_code_unit(path):
    try:
        entries = {e.name for e in os.scandir(path)}
    except OSError:
        return False
    return bool(entries & CODE_MARKERS)


def classify_file(name):
    if name in JUNK_NAMES:
        return "junk_candidate"
    ext = os.path.splitext(name)[1].lower()
    if ext in DOC_EXT:
        return "document"
    if ext in MEDIA_EXT:
        return "media"
    if ext in ARCHIVE_EXT:
        return "archive"
    return "other"


def du_size(path):
    if os.path.isfile(path):
        try:
            return os.path.getsize(path)
        except OSError:
            return 0
    total = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


units = []
skipped = []
try:
    entries = sorted(os.scandir(target), key=lambda e: e.name)
except OSError as e:
    print(f"error: cannot read {target}: {e}", file=sys.stderr)
    sys.exit(1)

for e in entries:
    name = e.name
    if name in ("survey.json", "FILESYSTEM_MAP.md", "AGENTS.md") or name.endswith(".filesystem-index"):
        continue
    path = e.path
    if e.is_dir(follow_symlinks=False):
        if name in SKIP_DIRS:
            skipped.append(path)
            continue
        if dir_is_empty(path) or is_junk_name(name):
            kind = "junk_candidate"
        elif is_code_unit(path):
            kind = "code_unit"
        else:
            kind = "dir"
    elif e.is_file(follow_symlinks=False):
        kind = classify_file(name)
    else:
        continue
    try:
        mtime = int(e.stat(follow_symlinks=False).st_mtime)
    except OSError:
        mtime = 0
    units.append({"path": path, "kind": kind, "size": du_size(path), "mtime": mtime})

doc = {
    "target": target,
    "total_units": len(units),
    "units": units,
    "skipped_noise_dirs": skipped,
}
out_path = os.path.join(target, "survey.json")
with open(out_path, "w") as fh:
    json.dump(doc, fh, indent=2)

# Human summary
from collections import Counter
counts = Counter(u["kind"] for u in units)
total_size = sum(u["size"] for u in units)
print(f"Survey of {target}")
print(f"total_units: {len(units)}   (skipped {len(skipped)} noise dirs)")
print(f"total_size: {total_size/1e9:.2f} GB")
print("by kind:")
for k, n in counts.most_common():
    print(f"  {k:16} {n}")
print(f"-> {out_path}")
PY
