#!/usr/bin/env python3
"""
Scan SKILL.md files for high-risk prompt-injection markers.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List

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


def scan_text(text: str) -> List[str]:
    matches = []
    for pattern in HIGH_RISK_PATTERNS:
        if pattern.search(text):
            matches.append(pattern.pattern)
    return matches


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan SKILL.md files for prompt-injection markers")
    parser.add_argument("--report", help="Write JSON report to this path")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when findings are present")
    args = parser.parse_args()

    library_root = Path(detect_library_root(os.path.dirname(os.path.abspath(__file__))))
    skills_root = library_root / "Skills"
    if not skills_root.exists():
        print(f"Error: Skills directory not found at {skills_root}", file=sys.stderr)
        return 1

    findings: List[Dict] = []
    scanned = 0

    for skill_md in skills_root.rglob("SKILL.md"):
        scanned += 1
        text = skill_md.read_text(encoding="utf-8", errors="ignore")
        matched = scan_text(text)
        if not matched:
            continue
        findings.append(
            {
                "path": str(skill_md),
                "matches": matched,
                "count": len(matched),
            }
        )

    report = {
        "library_root": str(library_root),
        "skills_root": str(skills_root),
        "scanned_files": scanned,
        "findings": findings,
        "findings_count": len(findings),
    }

    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Report written to {args.report}")

    print(f"Scanned SKILL.md files: {scanned}")
    print(f"Findings: {len(findings)}")
    if findings:
        for finding in findings[:10]:
            print(f"- {finding['path']} ({finding['count']} marker(s))")

    if args.strict and findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
