#!/usr/bin/env python3
"""fs-classify — agent-driven classification harness.

This is NOT a keyword classifier that decides on its own. It is the harness that
lets an AI agent classify a directory's units with real judgment, while the
taxonomy improves as coverage grows. Three subcommands form the loop:

  emit   TARGET --out batch.json [--batch N] [--resume]
         Enumerate not-yet-classified units, attach a dynamic-depth snippet and a
         heuristic hint_category to each, write the batch for the agent to judge.
         Exit 42 when no units remain (loop-until-complete stop signal).

  record TARGET --decisions decisions.json --out manifest.csv
         Append the agent's decisions to manifest.csv (idempotent: replaces any
         prior row for the same path). New categories are accepted as-is.

  report TARGET --out manifest.csv --report report.md
         (Re)generate the human classification report from the manifest.

Read-only on user content (samples; never moves — that's fs-reorganize's job).

Exit codes: 0 ok / work remains · 42 coverage complete · 1 error.
"""
import argparse, csv, json, os, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))


def norm(p):
    """NFC-normalize a path so NFD (macOS on-disk) and NFC compare equal."""
    return unicodedata.normalize("NFC", p)

SKIP_DIRS = {"node_modules", ".git", ".venv", "venv", "site-packages",
             "__pycache__", ".Trash", "Library", "System", "usr", "bin",
             "private", ".cache", ".npm"}
CODE_MARKERS = {".git", "package.json", "pyproject.toml", "Cargo.toml",
                "go.mod", "requirements.txt", "Gemfile", "pom.xml",
                "build.gradle", ".venv", "venv"}
JUNK_NAMES = {".DS_Store", ".localized", "Thumbs.db"}
JUNK_PREFIXES = ("test", "tmp", "temp", "temp_", "to_be_deleted",
                 "temp_removal", "untitled")
DOC_EXT = {".docx", ".pdf", ".pptx", ".md", ".csv", ".xlsx", ".ipynb",
           ".txt", ".eml", ".doc", ".ppt", ".xls", ".rtf"}
MEDIA_EXT = {".png", ".jpg", ".jpeg", ".gif", ".mp4", ".webm", ".mov",
             ".tif", ".tiff", ".svg", ".heic", ".webp", ".mp3", ".wav"}
ARCHIVE_EXT = {".zip", ".dmg", ".pkg", ".tar", ".gz", ".tgz", ".bz2", ".7z"}
SAMPLEABLE = {".md", ".txt", ".csv", ".json", ".yml", ".yaml", ".eml", ".log"}
RESERVED = {"survey.json", "manifest.csv", "report.md", "batch.json",
            "batch2.json", "decisions.json", "classification_report.md",
            "FILESYSTEM_MAP.md", "AGENTS.md", "INDEX.md"}
HEADER = ["current_path", "kind", "size", "category", "proposed_action",
          "target_path", "confidence", "note"]


def dir_empty(p):
    try:
        return not any(os.scandir(p))
    except OSError:
        return False


def is_code_unit(p):
    try:
        return bool({e.name for e in os.scandir(p)} & CODE_MARKERS)
    except OSError:
        return False


def is_junk_name(name):
    low = name.lower()
    return name in JUNK_NAMES or any(low.startswith(p) for p in JUNK_PREFIXES)


def kind_of(entry):
    name = entry.name
    if entry.is_dir(follow_symlinks=False):
        if dir_empty(entry.path) or is_junk_name(name):
            return "junk_candidate"
        return "code_unit" if is_code_unit(entry.path) else "dir"
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


def list_units(target):
    out = []
    try:
        entries = sorted(os.scandir(target), key=lambda e: e.name)
    except OSError as e:
        sys.exit(f"error: cannot read {target}: {e}")
    for e in entries:
        if (e.name in RESERVED or e.name in SKIP_DIRS
                or e.name.startswith(".filesystem-index")):
            continue
        if not (e.is_dir(follow_symlinks=False) or e.is_file(follow_symlinks=False)):
            continue
        try:
            size = e.stat(follow_symlinks=False).st_size
        except OSError:
            size = 0
        out.append({"path": e.path, "name": e.name, "kind": kind_of(e), "size": size})
    return out


def snippet_for(unit):
    """Dynamic depth: read content only where it sharpens the agent's judgment."""
    name, kind, path = unit["name"], unit["kind"], unit["path"]
    text = name.replace("_", " ").replace("-", " ")
    if kind == "code_unit":
        for f in ("README.md", "README", "README.txt", "package.json",
                  "pyproject.toml"):
            rp = os.path.join(path, f)
            if os.path.isfile(rp):
                try:
                    with open(rp, errors="ignore") as fh:
                        text += " | " + fh.read(2000)
                except OSError:
                    pass
                break
        try:
            text += " | contents: " + ", ".join(
                sorted(os.listdir(path))[:20])
        except OSError:
            pass
    elif kind == "document" and os.path.splitext(name)[1].lower() in SAMPLEABLE:
        try:
            with open(path, errors="ignore") as fh:
                text += " | " + fh.read(4000)
        except OSError:
            pass
    return text.strip()


def load_taxonomy(path):
    with open(path) as fh:
        return json.load(fh)


def hint_category(text, ext, tax):
    best, score = tax.get("fallback", "Media_Documents"), 0
    low = text.lower()
    for cat, spec in tax["categories"].items():
        if cat == "Junk_Candidate":
            continue
        s = sum(1 for kw in spec.get("keywords", []) if kw in low)
        if ext in set(spec.get("ext", [])):
            s += 1
        if s > score:
            best, score = cat, s
    return best, round(min(0.95, 0.4 + 0.18 * score) if score else 0.4, 2)


def done_paths(out_path):
    done = {}
    if os.path.isfile(out_path):
        with open(out_path, newline="") as fh:
            for row in csv.DictReader(fh):
                done[norm(row["current_path"])] = row
    return done


def cmd_emit(args, tax):
    target = os.path.abspath(args.target)
    out_path = args.out or os.path.join(target, "batch.json")
    manifest = args.manifest or os.path.join(target, "manifest.csv")
    done = done_paths(manifest) if args.resume else {}
    units = [u for u in list_units(target) if norm(u["path"]) not in done]
    if not units:
        print("coverage complete: 0 units remaining", file=sys.stderr)
        sys.exit(42)
    batch = units[: args.batch]
    for u in batch:
        ext = os.path.splitext(u["name"])[1].lower()
        u["snippet"] = snippet_for(u)[:4000]
        if u["kind"] == "junk_candidate":
            u["hint_category"], u["hint_confidence"] = "Junk_Candidate", 0.5
        else:
            u["hint_category"], u["hint_confidence"] = hint_category(
                u["snippet"], ext, tax)
    with open(out_path, "w") as fh:
        json.dump(batch, fh, indent=2)
    print(f"emitted {len(batch)} units ({len(units)-len(batch)} remaining) -> {out_path}")
    sys.exit(0)


def cmd_record(args, tax):
    target = os.path.abspath(args.target)
    out_path = args.out or os.path.join(target, "manifest.csv")
    with open(args.decisions) as fh:
        decisions = json.load(fh)
    rows = done_paths(out_path)  # norm(path) -> existing row (dict)
    sizes = {norm(u["path"]): (u["size"], u["kind"]) for u in list_units(target)}
    for d in decisions:
        p = d["path"]
        size, kind = sizes.get(norm(p), (0, "other"))
        rows[norm(p)] = {
            "current_path": p, "kind": kind, "size": size,
            "category": d["category"],
            "proposed_action": d.get("proposed_action", "move"),
            "target_path": d.get("target_path", f"{d['category']}/{os.path.basename(p)}"),
            "confidence": d.get("confidence", 0.7),
            "note": d.get("note", ""),
        }
    with open(out_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        for r in rows.values():
            w.writerow(r)
    print(f"recorded {len(decisions)} decisions; manifest now {len(rows)} rows")


def write_report(rows, report_path, target):
    from collections import defaultdict
    by_cat = defaultdict(list)
    for r in rows:
        by_cat[r["category"]].append(r)
    L = [f"# Classification report — {target}", "",
         f"Total classified: {len(rows)}", "",
         "## Proposed deletions / quarantine", ""]
    junk = by_cat.get("Junk_Candidate", [])
    L += ([f"- `{r['current_path']}` — {r['note']}" for r in junk] or ["_none_"])
    L += ["", "## Low-confidence — needs review", ""]
    low = [r for r in rows if float(r["confidence"]) < 0.5
           and r["category"] != "Junk_Candidate"]
    L += ([f"- `{r['current_path']}` → **{r['category']}** (conf {r['confidence']})"
           for r in low] or ["_none_"])
    L += [""]
    for cat in sorted(by_cat):
        if cat == "Junk_Candidate":
            continue
        L += [f"## {cat} ({len(by_cat[cat])})", ""]
        L += [f"- `{os.path.basename(r['current_path'])}` → `{r['target_path']}` "
              f"(conf {r['confidence']})" for r in by_cat[cat]]
        L += [""]
    with open(report_path, "w") as fh:
        fh.write("\n".join(L))


def cmd_report(args, tax):
    target = os.path.abspath(args.target)
    out_path = args.out or os.path.join(target, "manifest.csv")
    report_path = args.report or os.path.join(target, "classification_report.md")
    rows = list(done_paths(out_path).values())
    write_report(rows, report_path, target)
    print(f"report -> {report_path} ({len(rows)} rows)")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    common = dict()
    for name in ("emit", "record", "report"):
        p = sub.add_parser(name)
        p.add_argument("target")
        p.add_argument("--out", default=None)
        p.add_argument("--taxonomy", default=os.path.join(HERE, "taxonomy.default.json"))
        if name == "emit":
            p.add_argument("--batch", type=int, default=50)
            p.add_argument("--resume", action="store_true")
            p.add_argument("--manifest", default=None)
        if name == "record":
            p.add_argument("--decisions", required=True)
        if name == "report":
            p.add_argument("--report", default=None)
    args = ap.parse_args()
    tax = load_taxonomy(args.taxonomy)
    {"emit": cmd_emit, "record": cmd_record, "report": cmd_report}[args.cmd](args, tax)


if __name__ == "__main__":
    main()
