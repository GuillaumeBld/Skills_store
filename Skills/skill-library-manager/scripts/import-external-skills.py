#!/usr/bin/env python3
"""
Import external skills from GitHub repositories into the local Skills library.

Security defaults:
- HTTPS GitHub repositories only
- Prompt-injection pattern scan on SKILL.md
- Skips blocked skills by default
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

REPO_NAMES = ("Skills_librairie", "Skills_store")
FALLBACK_ROOTS = [
    os.path.expanduser("~/Skills_librairie"),
    os.path.expanduser("~/Skills_store"),
    os.path.expanduser("~/Documents/Skills/Skills_librairie"),
    os.path.expanduser("~/Documents/Skills/Skills_store"),
]

HIGH_RISK_PATTERNS = [
    re.compile(r"ignore\s+(all|any|previous|prior)\s+(instructions?|prompts?)", re.IGNORECASE),
    re.compile(r"(override|bypass)\s+(the\s+)?(system|developer)\s+prompt", re.IGNORECASE),
    re.compile(r"jailbreak|dan\s+mode|do\s+anything\s+now|ignore\s+safety", re.IGNORECASE),
    re.compile(
        r"(you|assistant|model).{0,60}(reveal|exfiltrate|steal).{0,60}"
        r"(secret|token|credential|api[\s_-]?key|password)",
        re.IGNORECASE,
    ),
    re.compile(r"send.{0,40}(env|secret|token|credential).{0,40}https?://", re.IGNORECASE),
]

LOW_TRUST_PATH_PATTERNS = [
    re.compile(r"/\.git/"),
    re.compile(r"/node_modules/"),
]


def is_library_root(path: str) -> bool:
    if not path or not os.path.isdir(path):
        return False
    return os.path.isdir(os.path.join(path, "Skills")) or os.path.isdir(os.path.join(path, "skills"))


def detect_library_root(start_dir: str) -> str:
    env_root = os.getenv("LIBRARY_ROOT")
    if env_root:
        env_root = os.path.abspath(os.path.expanduser(env_root))
        if is_library_root(env_root):
            return env_root

    current = os.path.abspath(start_dir)
    while current != os.path.dirname(current):
        if is_library_root(current) or os.path.basename(current) in REPO_NAMES:
            return current
        current = os.path.dirname(current)

    for candidate in FALLBACK_ROOTS:
        candidate = os.path.abspath(candidate)
        if is_library_root(candidate):
            return candidate

    return os.path.abspath(os.path.expanduser("~/Skills_librairie"))


def is_allowed_repo_url(url: str) -> bool:
    """Only allow HTTPS github.com repository URLs."""
    try:
        parsed = urlparse(url)
        if parsed.scheme != "https":
            return False
        if parsed.netloc.lower() != "github.com":
            return False
        # /owner/repo or /owner/repo(.git)
        parts = [p for p in parsed.path.split("/") if p]
        return len(parts) >= 2
    except Exception:
        return False


def normalize_skill_name(name: str) -> str:
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9-]+", "-", name.lower())).strip("-")


def detect_injection_markers(text: str) -> List[str]:
    matches = []
    for pattern in HIGH_RISK_PATTERNS:
        if pattern.search(text):
            matches.append(pattern.pattern)
    return matches


def infer_category_and_name(skill_md_path: Path, default_category: str) -> Tuple[str, str]:
    """
    Infer target category/name from source path:
    - Skills/<Category>/<Skill>/SKILL.md
    - skills/<Category>/<Skill>/SKILL.md
    - fallback to default category and parent dir name
    """
    parts = list(skill_md_path.parts)
    lower_parts = [p.lower() for p in parts]
    name = normalize_skill_name(skill_md_path.parent.name)
    category = default_category

    if "skills" in lower_parts:
        idx = lower_parts.index("skills")
        tail_dirs = parts[idx + 1 : -1]  # directories after skills/ and before SKILL.md
        if len(tail_dirs) >= 2:
            category = tail_dirs[0]
            name = normalize_skill_name(tail_dirs[-1])
        elif len(tail_dirs) == 1:
            category = default_category
            name = normalize_skill_name(tail_dirs[0])

    if not name:
        name = "imported-skill"
    return category, name


def clone_repo(repo_url: str, target_dir: Path) -> None:
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(target_dir)],
        capture_output=True,
        text=True,
        check=True,
    )


def should_skip_path(path: Path) -> bool:
    normalized = str(path).replace("\\", "/")
    return any(pattern.search(normalized) for pattern in LOW_TRUST_PATH_PATTERNS)


def find_skill_markdowns(repo_dir: Path) -> List[Path]:
    results = []
    for skill_md in repo_dir.rglob("SKILL.md"):
        if should_skip_path(skill_md):
            continue
        results.append(skill_md)
    return results


def copy_skill_dir(src_dir: Path, dst_dir: Path, overwrite: bool = False) -> None:
    if dst_dir.exists():
        if not overwrite:
            raise FileExistsError(f"destination exists: {dst_dir}")
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns(".git", ".github", "__pycache__"))


def parse_repos_from_file(path: Optional[str]) -> List[str]:
    if not path:
        return []
    content = Path(path).read_text(encoding="utf-8")
    repos = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        repos.append(line)
    return repos


def import_from_repo(
    repo_url: str,
    skills_root: Path,
    default_category: str,
    dry_run: bool,
    overwrite: bool,
    max_skills: int,
) -> Dict:
    summary = {
        "repo": repo_url,
        "discovered": 0,
        "imported": 0,
        "skipped": 0,
        "blocked": 0,
        "errors": [],
        "details": [],
    }

    with tempfile.TemporaryDirectory(prefix="skills-import-") as temp_dir:
        repo_dir = Path(temp_dir) / "repo"
        try:
            clone_repo(repo_url, repo_dir)
        except subprocess.CalledProcessError as exc:
            summary["errors"].append(f"clone_failed: {exc.stderr.strip()}")
            return summary

        skill_markdowns = find_skill_markdowns(repo_dir)
        summary["discovered"] = len(skill_markdowns)

        for skill_md in skill_markdowns[:max_skills]:
            rel = skill_md.relative_to(repo_dir)
            category, name = infer_category_and_name(skill_md, default_category)
            target_dir = skills_root / category / name

            detail = {
                "source": str(rel),
                "category": category,
                "name": name,
                "target": str(target_dir),
                "status": "",
                "reason": "",
            }

            try:
                content = skill_md.read_text(encoding="utf-8", errors="ignore")
                matches = detect_injection_markers(content)
                if matches:
                    detail["status"] = "blocked"
                    detail["reason"] = f"prompt_injection_markers:{len(matches)}"
                    summary["blocked"] += 1
                    summary["details"].append(detail)
                    continue

                if target_dir.exists() and not overwrite:
                    detail["status"] = "skipped"
                    detail["reason"] = "already_exists"
                    summary["skipped"] += 1
                    summary["details"].append(detail)
                    continue

                if not dry_run:
                    target_dir.parent.mkdir(parents=True, exist_ok=True)
                    copy_skill_dir(skill_md.parent, target_dir, overwrite=overwrite)

                detail["status"] = "imported" if not dry_run else "dry-run-importable"
                detail["reason"] = "ok"
                summary["imported"] += 1
                summary["details"].append(detail)
            except Exception as exc:
                detail["status"] = "error"
                detail["reason"] = str(exc)
                summary["errors"].append(f"{rel}: {exc}")
                summary["details"].append(detail)

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Import external skills into local Skills library safely.")
    parser.add_argument("--repo", action="append", default=[], help="GitHub repository URL (repeatable)")
    parser.add_argument("--repos-file", help="File with one repository URL per line")
    parser.add_argument("--default-category", default="Community", help="Fallback category when source path is ambiguous")
    parser.add_argument("--dry-run", action="store_true", help="Analyze only, do not copy files")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing destination skills")
    parser.add_argument("--max-skills", type=int, default=200, help="Max skills to inspect/import per repository")
    parser.add_argument("--report", help="Write JSON report to this path")
    args = parser.parse_args()

    library_root = Path(detect_library_root(os.path.dirname(os.path.abspath(__file__))))
    skills_root = library_root / "Skills"
    if not skills_root.exists():
        print(f"Error: Skills directory not found at {skills_root}", file=sys.stderr)
        return 1

    repos = args.repo + parse_repos_from_file(args.repos_file)
    repos = [r.strip() for r in repos if r.strip()]
    if not repos:
        print("Error: provide at least one --repo or --repos-file entry", file=sys.stderr)
        return 1

    invalid = [r for r in repos if not is_allowed_repo_url(r)]
    if invalid:
        print("Error: only HTTPS github.com repository URLs are allowed:", file=sys.stderr)
        for repo in invalid:
            print(f"  - {repo}", file=sys.stderr)
        return 1

    report = {
        "library_root": str(library_root),
        "skills_root": str(skills_root),
        "dry_run": args.dry_run,
        "results": [],
    }

    for repo in repos:
        print(f"Processing {repo}...")
        result = import_from_repo(
            repo_url=repo,
            skills_root=skills_root,
            default_category=args.default_category,
            dry_run=args.dry_run,
            overwrite=args.overwrite,
            max_skills=max(1, args.max_skills),
        )
        report["results"].append(result)
        print(
            f"  discovered={result['discovered']} imported={result['imported']} "
            f"skipped={result['skipped']} blocked={result['blocked']} errors={len(result['errors'])}"
        )

    totals = {
        "repos": len(report["results"]),
        "discovered": sum(r["discovered"] for r in report["results"]),
        "imported": sum(r["imported"] for r in report["results"]),
        "skipped": sum(r["skipped"] for r in report["results"]),
        "blocked": sum(r["blocked"] for r in report["results"]),
        "errors": sum(len(r["errors"]) for r in report["results"]),
    }
    report["totals"] = totals

    report_path = Path(args.report) if args.report else library_root / "external-skills-import-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Report written to {report_path}")
    print(
        f"Totals: discovered={totals['discovered']} imported={totals['imported']} "
        f"skipped={totals['skipped']} blocked={totals['blocked']} errors={totals['errors']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
