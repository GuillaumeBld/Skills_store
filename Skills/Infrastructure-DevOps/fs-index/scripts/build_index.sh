#!/usr/bin/env bash
# fs-index — build the grep-first, agent-navigable RAG layer over a directory.
# Emits: per-area INDEX.md, .filesystem-index/catalog.jsonl, and a master
# FILESYSTEM_MAP.md (<=25KB) that EXPLICITLY links every INDEX.md. With --wire it
# also inserts a pointer block into ~/.claude/CLAUDE.md and writes ~/AGENTS.md so
# agents auto-discover the map. Additive: creates index files, moves nothing.
#
# Usage: build_index.sh [TARGET] [--wire]   (default TARGET: $HOME)
set -euo pipefail

TARGET="$HOME"; WIRE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --wire) WIRE=1; shift ;;
    *) TARGET="$1"; shift ;;
  esac
done
TARGET="$(cd "$TARGET" && pwd)"

WIRE="$WIRE" python3 - "$TARGET" <<'PY'
import json, os, sys, time

target = sys.argv[1]
wire = os.environ.get("WIRE") == "1"
idx_dir = os.path.join(target, ".filesystem-index")
os.makedirs(idx_dir, exist_ok=True)
catalog_path = os.path.join(idx_dir, "catalog.jsonl")

SKIP = {"node_modules", ".git", ".venv", "venv", "site-packages", "__pycache__",
        ".Trash", "Library", "System", "usr", "bin", "private", ".cache",
        ".npm", ".filesystem-index"}
RESERVED = {"survey.json", "manifest.csv", "classification_report.md",
            "FILESYSTEM_MAP.md", "AGENTS.md", "INDEX.md", "moves.log",
            "undo.sh", "batch.json", "decisions.json"}
SAMPLE = {".md", ".txt", ".csv", ".json", ".yml", ".yaml", ".eml", ".log"}
CODE_MARKERS = {".git", "package.json", "pyproject.toml", "Cargo.toml", "go.mod"}


def summarize(path, name):
    if os.path.isdir(path):
        for r in ("README.md", "README", "README.txt"):
            rp = os.path.join(path, r)
            if os.path.isfile(rp):
                try:
                    with open(rp, errors="ignore") as fh:
                        for line in fh:
                            s = line.strip().lstrip("# ").strip()
                            if s:
                                return s[:160]
                except OSError:
                    pass
        return f"folder: {name}"
    ext = os.path.splitext(name)[1].lower()
    if ext in SAMPLE:
        try:
            with open(path, errors="ignore") as fh:
                for line in fh:
                    s = line.strip().lstrip("# ").strip()
                    if s:
                        return s[:160]
        except OSError:
            pass
    return name


def keywords(name):
    base = os.path.splitext(name)[0]
    toks = [t.lower() for t in base.replace("_", " ").replace("-", " ").split()
            if len(t) > 2]
    return sorted(set(toks))[:8]


def size_of(path):
    if os.path.isfile(path):
        try:
            return os.path.getsize(path)
        except OSError:
            return 0
    tot = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in files:
            try:
                tot += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return tot


def kind_of(path, name):
    if os.path.isdir(path):
        try:
            if {e.name for e in os.scandir(path)} & CODE_MARKERS:
                return "code_unit"
        except OSError:
            pass
        return "dir"
    return "file"


def list_children(area_path):
    try:
        return sorted((e for e in os.scandir(area_path)
                       if e.name not in SKIP and e.name not in RESERVED
                       and not e.name.startswith(".")),
                      key=lambda e: e.name)
    except OSError:
        return []


# Top-level areas + loose files.
top = [e for e in sorted(os.scandir(target), key=lambda e: e.name)
       if e.name not in SKIP and e.name not in RESERVED
       and not e.name.startswith(".")]

records = []
area_indexes = []   # (area_name, rel_index_path, count, summary)

for e in top:
    if e.is_dir(follow_symlinks=False):
        area = e.name
        children = list_children(e.path)
        # area INDEX.md
        lines = [f"# {area}", "", f"_{len(children)} items_", ""]
        for c in children:
            cpath = c.path
            kind = kind_of(cpath, c.name)
            summ = summarize(cpath, c.name)
            lines.append(f"- **{c.name}** — {summ}")
            records.append({
                "path": cpath, "kind": kind, "category": area,
                "size": size_of(cpath), "mtime": int(c.stat().st_mtime),
                "summary": summ, "keywords": keywords(c.name)})
        index_path = os.path.join(e.path, "INDEX.md")
        with open(index_path, "w") as fh:
            fh.write("\n".join(lines) + "\n")
        rel = os.path.relpath(index_path, target)
        area_indexes.append((area, rel, len(children),
                             summarize(e.path, area)))
    else:
        summ = summarize(e.path, e.name)
        records.append({
            "path": e.path, "kind": "file", "category": "(root)",
            "size": size_of(e.path), "mtime": int(e.stat().st_mtime),
            "summary": summ, "keywords": keywords(e.name)})

with open(catalog_path, "w") as fh:
    for r in records:
        fh.write(json.dumps(r) + "\n")

# Master MAP (<=25KB). Legend + "Where do I find X?" + explicit INDEX links.
M = [f"# Filesystem Map — {target}", "",
     "> Agent entry point. To find something: grep "
     "`.filesystem-index/catalog.jsonl` (fields: path, kind, category, summary, "
     "keywords) or open the relevant area INDEX.md linked below. "
     "Regenerate with `fs-index`.", "",
     "## Top-level legend", ""]
for area, rel, n, summ in area_indexes:
    M.append(f"- **{area}/** ({n}) — {summ}  ·  [INDEX]({rel})")
M += ["", "## Where do I find X?", "",
      "| Looking for | Area |", "|---|---|"]
HINTS = [("academic / research / ESG", "Academic_Work"),
         ("business / ChiBizHub / decks", "Business_Work"),
         ("code projects", "Development_Projects"),
         ("scripts / tools / configs", "Dev_Tools"),
         ("resume / CV / job / finance / health", "Personal_Admin"),
         ("documents / reports / notes", "Media_Documents"),
         ("screenshots / photos / video", "Media_Photos"),
         ("junk to review", "_REVIEW_DELETE")]
present = {a for a, _, _, _ in area_indexes}
for label, area in HINTS:
    if area in present:
        M.append(f"| {label} | [{area}/]({area}/INDEX.md) |")
M += ["", f"## Catalog", "",
      f"- `{os.path.relpath(catalog_path, target)}` — "
      f"{len(records)} records, one JSON object per line (query with rg/jq).", ""]

text = "\n".join(M) + "\n"
if len(text.encode()) > 25600:
    text = text.encode()[:25400].decode("utf-8", "ignore") + "\n\n_(truncated to 25KB budget)_\n"
with open(os.path.join(target, "FILESYSTEM_MAP.md"), "w") as fh:
    fh.write(text)

# AGENTS.md at the tree root (cross-vendor convention).
agents = (f"# AGENTS.md\n\nThis machine has a filesystem map for agents.\n"
          f"Read `FILESYSTEM_MAP.md` first, then grep "
          f"`.filesystem-index/catalog.jsonl` to locate files.\n"
          f"Regenerate the index with the `fs-index` skill.\n")
with open(os.path.join(target, "AGENTS.md"), "w") as fh:
    fh.write(agents)

if wire:
    claude_md = os.path.expanduser("~/.claude/CLAUDE.md")
    block = ("\n<!-- fs-index -->\n"
             "## Filesystem map\n"
             f"Read `{os.path.join(target, 'FILESYSTEM_MAP.md')}` first to locate "
             f"files; structured catalog at "
             f"`{os.path.relpath(catalog_path, os.path.expanduser('~'))}` "
             "(grep/jq). Regenerate with the fs-index skill.\n"
             "<!-- /fs-index -->\n")
    existing = ""
    if os.path.isfile(claude_md):
        with open(claude_md) as fh:
            existing = fh.read()
    if "<!-- fs-index -->" not in existing:
        os.makedirs(os.path.dirname(claude_md), exist_ok=True)
        with open(claude_md, "a") as fh:
            fh.write(block)
        print(f"wired pointer into {claude_md}")
    else:
        print(f"pointer already present in {claude_md}")

print(f"catalog: {len(records)} records -> {catalog_path}")
print(f"areas indexed: {len(area_indexes)}")
print(f"map: {os.path.join(target, 'FILESYSTEM_MAP.md')} "
      f"({len(text.encode())} bytes)")
PY
