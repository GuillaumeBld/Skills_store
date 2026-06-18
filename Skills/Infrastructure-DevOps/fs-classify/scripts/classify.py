#!/usr/bin/env python3
"""fs-classify — dynamic-depth classification of a directory's units into a
taxonomy, producing a reviewable manifest.csv + classification_report.md.

Read-only on the target (samples file contents, never modifies). Resumable and
batchable so it can run under /loop until coverage is complete.

Exit codes:
  0  — classified one or more new units this run (work may remain)
  42 — coverage complete: no unclassified in-scope units remain (loop stop signal)
  1  — error

Usage:
  classify.py TARGET [--out manifest.csv] [--report report.md]
              [--taxonomy taxonomy.default.json] [--batch N] [--resume]
"""
import argparse, csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))

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
RESERVED = {"survey.json", "manifest.csv", "report.md",
            "classification_report.md", "FILESYSTEM_MAP.md", "AGENTS.md",
            "INDEX.md"}


def is_junk_name(name):
    if name in JUNK_NAMES:
        return True
    low = name.lower()
    return any(low.startswith(p) for p in JUNK_PREFIXES)


def dir_empty(path):
    try:
        return not any(os.scandir(path))
    except OSError:
        return False


def is_code_unit(path):
    try:
        return bool({e.name for e in os.scandir(path)} & CODE_MARKERS)
    except OSError:
        return False


def kind_of(entry):
    name = entry.name
    if entry.is_dir(follow_symlinks=False):
        if dir_empty(entry.path) or is_junk_name(name):
            return "junk_candidate"
        if is_code_unit(entry.path):
            return "code_unit"
        return "dir"
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
    """Top-level units, mirroring fs-survey (code projects = one unit)."""
    out = []
    try:
        entries = sorted(os.scandir(target), key=lambda e: e.name)
    except OSError as e:
        sys.exit(f"error: cannot read {target}: {e}")
    for e in entries:
        if e.name in RESERVED or e.name in SKIP_DIRS or e.name.startswith(".filesystem-index"):
            continue
        if not (e.is_dir(follow_symlinks=False) or e.is_file(follow_symlinks=False)):
            continue
        try:
            size = e.stat(follow_symlinks=False).st_size
        except OSError:
            size = 0
        out.append({"path": e.path, "name": e.name, "kind": kind_of(e), "size": size})
    return out


def sample_text(unit):
    """Dynamic depth: read content only where it sharpens the label."""
    name, kind, path = unit["name"], unit["kind"], unit["path"]
    text = name.replace("_", " ").replace("-", " ")
    if kind == "code_unit":
        for readme in ("README.md", "README", "README.txt", "package.json",
                       "pyproject.toml"):
            rp = os.path.join(path, readme)
            if os.path.isfile(rp):
                try:
                    with open(rp, "r", errors="ignore") as fh:
                        text += " " + fh.read(2000)
                except OSError:
                    pass
                break
    elif kind == "document":
        ext = os.path.splitext(name)[1].lower()
        if ext in SAMPLEABLE:
            try:
                with open(path, "r", errors="ignore") as fh:
                    text += " " + fh.read(4000)
            except OSError:
                pass
    # media / archive / junk: filename only (no read)
    return text.lower()


def score_categories(text, ext, tax):
    best, best_score = tax.get("fallback", "Media_Documents"), 0
    for cat, spec in tax["categories"].items():
        if cat == "Junk_Candidate":
            continue
        score = sum(1 for kw in spec.get("keywords", []) if kw in text)
        if ext in set(spec.get("ext", [])):
            score += 1
        if score > best_score:
            best, best_score = cat, score
    # Confidence: 0.4 baseline (ext/fallback) → up toward 0.95 with keyword hits.
    confidence = min(0.95, 0.4 + 0.18 * best_score) if best_score else 0.4
    return best, round(confidence, 2)


def classify_unit(unit, tax):
    if unit["kind"] == "junk_candidate":
        return {"category": "Junk_Candidate", "action": "quarantine",
                "target": "", "confidence": 0.5,
                "note": "empty/scratch — review before deleting"}
    ext = os.path.splitext(unit["name"])[1].lower()
    text = sample_text(unit)
    cat, conf = score_categories(text, ext, tax)
    return {"category": cat, "action": "move",
            "target": f"{cat}/{unit['name']}", "confidence": conf, "note": ""}


def load_done(out_path):
    done = set()
    if os.path.isfile(out_path):
        with open(out_path, newline="") as fh:
            for row in csv.DictReader(fh):
                done.add(row["current_path"])
    return done


HEADER = ["current_path", "kind", "size", "category", "proposed_action",
          "target_path", "confidence", "note"]


def write_report(rows, report_path, target):
    from collections import defaultdict
    by_cat = defaultdict(list)
    for r in rows:
        by_cat[r["category"]].append(r)
    lines = [f"# Classification report — {target}", "",
             f"Total classified: {len(rows)}", ""]
    # Proposed deletions section first (most important to review).
    junk = by_cat.get("Junk_Candidate", [])
    lines += ["## Proposed deletions / quarantine", ""]
    if junk:
        for r in junk:
            lines.append(f"- `{r['current_path']}` — {r['note']}")
    else:
        lines.append("_none_")
    lines += [""]
    low = [r for r in rows if float(r["confidence"]) < 0.5 and r["category"] != "Junk_Candidate"]
    lines += ["## Low-confidence — needs review", ""]
    if low:
        for r in low:
            lines.append(f"- `{r['current_path']}` → **{r['category']}** "
                         f"(conf {r['confidence']})")
    else:
        lines.append("_none_")
    lines += [""]
    for cat in sorted(by_cat):
        if cat == "Junk_Candidate":
            continue
        lines += [f"## {cat} ({len(by_cat[cat])})", ""]
        for r in by_cat[cat]:
            lines.append(f"- `{os.path.basename(r['current_path'])}` "
                         f"→ `{r['target_path']}` (conf {r['confidence']})")
        lines += [""]
    with open(report_path, "w") as fh:
        fh.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--out", default=None)
    ap.add_argument("--report", default=None)
    ap.add_argument("--taxonomy", default=os.path.join(HERE, "taxonomy.default.json"))
    ap.add_argument("--batch", type=int, default=50)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    target = os.path.abspath(args.target)
    out_path = args.out or os.path.join(target, "manifest.csv")
    report_path = args.report or os.path.join(target, "classification_report.md")
    with open(args.taxonomy) as fh:
        tax = json.load(fh)

    units = list_units(target)
    done = load_done(out_path) if args.resume else set()
    remaining = [u for u in units if u["path"] not in done]

    if not remaining:
        # Coverage complete — refresh report from existing manifest and signal stop.
        all_rows = []
        if os.path.isfile(out_path):
            with open(out_path, newline="") as fh:
                all_rows = list(csv.DictReader(fh))
        write_report(all_rows, report_path, target)
        print(f"coverage complete: {len(done)} units classified, 0 remaining")
        sys.exit(42)

    batch = remaining[: args.batch]
    new_exists = os.path.isfile(out_path)
    with open(out_path, "a", newline="") as fh:
        w = csv.writer(fh)
        if not new_exists:
            w.writerow(HEADER)
        for u in batch:
            c = classify_unit(u, tax)
            w.writerow([u["path"], u["kind"], u["size"], c["category"],
                        c["action"], c["target"], c["confidence"], c["note"]])

    # Rebuild report from the full manifest.
    with open(out_path, newline="") as fh:
        all_rows = list(csv.DictReader(fh))
    write_report(all_rows, report_path, target)

    left = len(remaining) - len(batch)
    print(f"classified {len(batch)} units this batch; {left} remaining")
    sys.exit(0)


if __name__ == "__main__":
    main()
