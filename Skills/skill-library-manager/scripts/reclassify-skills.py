#!/usr/bin/env python3
"""
Reclassify imported skills into meaningful top-level categories.

Targets common import buckets:
- Skills/Community
- Skills/debugging
- Skills/document-skills
- Skills/problem-solving
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_NAMES = ("Skills_librairie", "Skills_store")
FALLBACK_ROOTS = [
    os.path.expanduser("~/Skills_librairie"),
    os.path.expanduser("~/Skills_store"),
    os.path.expanduser("~/Documents/Skills/Skills_librairie"),
    os.path.expanduser("~/Documents/Skills/Skills_store"),
]

SOURCE_BUCKETS = ("Community", "debugging", "document-skills", "problem-solving")

MANUAL_OVERRIDES: Dict[str, str] = {
    "aussie-business-english": "Communication",
    "marketing-demand-acquisition": "Business-Operations",
    "seo-local-business": "Business-Operations",
    "project-health": "Business-Operations",
    "cto-advisor": "Business-Operations",
    "senior-pm": "Business-Operations",
    "fda-consultant-specialist": "Compliance-Regulatory",
    "mdr-745-specialist": "Compliance-Regulatory",
    "qms-audit-expert": "Compliance-Regulatory",
    "quality-documentation-manager": "Compliance-Regulatory",
    "quality-manager-qmr": "Compliance-Regulatory",
    "quality-manager-qms-iso13485": "Compliance-Regulatory",
    "regulatory-affairs-head": "Compliance-Regulatory",
    "capa-officer": "Compliance-Regulatory",
    "embedded-systems": "Development",
    "media-processing": "Development",
    "feature-forge": "Development",
    "sample-skill": "Meta-skill",
    "template-skill": "Meta-skill",
}

# Ordered by precedence: first best-scoring category wins ties.
CATEGORY_RULES: List[Tuple[str, List[str]]] = [
    ("Document-Generation", [
        "document-generation", "docx", "pdf", "pptx", "xlsx", "slide", "presentation", "ooxml"
    ]),
    ("Meta-skill", [
        "debug", "problem-solving", "root-cause", "tdd", "code-review", "skill-creator",
        "skill-tester", "verification", "spec-miner", "sequential-thinking", "dev-session"
    ]),
    ("Compliance-Regulatory", [
        "regulatory", "fda", "mdr", "qms", "qmr", "iso13485", "capa", "dsgvo"
    ]),
    ("Security", [
        "security", "secure", "secops", "iso27001", "gdpr", "dsgvo", "risk-management",
        "audit", "compliance", "isms"
    ]),
    ("Infrastructure-DevOps", [
        "devops", "sre", "kubernetes", "terraform", "docker", "cloud", "incident",
        "monitoring", "observability", "release", "chaos", "microservices", "migration"
    ]),
    ("AI-Agents", [
        "agent", "rag", "prompt", "llm", "fine-tuning", "gemini", "mcp", "ml", "ai-",
        "google-adk", "multimodal"
    ]),
    ("Design-Creative", [
        "design", "ux", "ui", "color", "threejs", "favicon", "theme", "styling", "web-design",
        "creative", "brand", "aesthetic"
    ]),
    ("Communication", [
        "content", "social-media", "copy", "communication", "newsletter", "docs-seeker",
        "wording", "story", "shopify-content", "wordpress-content"
    ]),
    ("Automation", [
        "automation", "workflow", "atlassian", "jira", "confluence", "google-apps-script",
        "playwright", "test-master", "web-testing"
    ]),
    ("Scientific", [
        "data-scientist", "data-engineer", "analytics", "pandas", "spark", "computer-vision",
        "financial-analyst", "research"
    ]),
    ("Business-Operations", [
        "product-manager", "product-strategist", "marketing", "sales", "revenue", "ceo",
        "customer-success", "project-health", "scrum-master", "agile", "app-store-optimization"
    ]),
    ("Development", [
        "developer", "architect", "backend", "frontend", "fullstack", "typescript", "javascript",
        "python", "golang", "java", "rust", "csharp", "cpp", "php", "laravel", "rails",
        "nextjs", "react", "vue", "nestjs", "django", "fastapi", "spring-boot", "wordpress",
        "shopify", "graphql", "database", "postgres", "sql", "api", "framework"
    ]),
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


def read_skill_text(skill_dir: Path) -> str:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ""
    return skill_md.read_text(encoding="utf-8", errors="ignore")


def classify_skill(skill_dir: Path, source_bucket: str) -> Tuple[str, Dict[str, int], str]:
    """
    Classify a skill into a category.
    Returns: (target_category, score_by_category, rationale)
    """
    # Strong source-bucket priors.
    if source_bucket == "document-skills":
        return "Document-Generation", {"Document-Generation": 999}, "source_bucket=document-skills"
    if source_bucket in ("debugging", "problem-solving"):
        return "Meta-skill", {"Meta-skill": 999}, f"source_bucket={source_bucket}"

    name = skill_dir.name.lower()
    if name in MANUAL_OVERRIDES:
        override = MANUAL_OVERRIDES[name]
        return override, {override: 1000}, "manual_override"

    text = read_skill_text(skill_dir).lower()
    corpus = f"{name}\n{text}"

    scores: Dict[str, int] = {category: 0 for category, _ in CATEGORY_RULES}
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in corpus:
                # Name hits are weighted higher than body hits.
                if kw in name:
                    scores[category] += 5
                else:
                    scores[category] += 1

    # Pick highest-scoring category with rule-order precedence.
    best_category = "Community"
    best_score = 0
    for category, _ in CATEGORY_RULES:
        score = scores.get(category, 0)
        if score > best_score:
            best_category = category
            best_score = score

    if best_score == 0:
        return "Community", scores, "no_matching_keywords"
    return best_category, scores, f"keyword_score={best_score}"


def move_skill(
    skill_dir: Path,
    skills_root: Path,
    target_category: str,
    apply: bool,
) -> Tuple[str, str]:
    """
    Move a skill directory to target category.
    Returns: (status, message) where status is moved|skipped|error|unchanged.
    """
    source_category = skill_dir.parent.name
    if source_category == target_category:
        return "unchanged", "already_in_target_category"

    target_dir = skills_root / target_category / skill_dir.name
    if target_dir.exists():
        return "skipped", f"target_exists:{target_dir}"

    if not apply:
        return "moved", f"dry_run:{skill_dir} -> {target_dir}"

    try:
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(skill_dir), str(target_dir))
        return "moved", f"{skill_dir} -> {target_dir}"
    except Exception as exc:
        return "error", str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description="Reclassify imported skills into structured categories")
    parser.add_argument("--apply", action="store_true", help="Apply filesystem moves (default: dry-run)")
    parser.add_argument("--report", default="skills-reclassification-report.json", help="Output JSON report path")
    args = parser.parse_args()

    library_root = Path(detect_library_root(os.path.dirname(os.path.abspath(__file__))))
    skills_root = library_root / "Skills"
    if not skills_root.exists():
        raise SystemExit(f"Skills directory not found: {skills_root}")

    report = {
        "library_root": str(library_root),
        "skills_root": str(skills_root),
        "apply": args.apply,
        "source_buckets": list(SOURCE_BUCKETS),
        "items": [],
        "summary": {
            "total_scanned": 0,
            "moved": 0,
            "skipped": 0,
            "unchanged": 0,
            "error": 0,
        },
    }

    for bucket in SOURCE_BUCKETS:
        bucket_dir = skills_root / bucket
        if not bucket_dir.exists():
            continue
        for child in sorted(bucket_dir.iterdir()):
            if not child.is_dir():
                continue
            report["summary"]["total_scanned"] += 1
            target_category, scores, rationale = classify_skill(child, bucket)
            status, message = move_skill(child, skills_root, target_category, args.apply)
            report["summary"][status] += 1
            report["items"].append({
                "skill": child.name,
                "from": bucket,
                "to": target_category,
                "status": status,
                "rationale": rationale,
                "score": scores.get(target_category, 0),
                "detail": message,
            })

    # Remove empty source buckets after apply.
    if args.apply:
        for bucket in SOURCE_BUCKETS:
            bucket_dir = skills_root / bucket
            if bucket_dir.exists() and not any(bucket_dir.iterdir()):
                bucket_dir.rmdir()

    report_path = Path(args.report)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Report written to {report_path}")
    print(
        "Summary: "
        f"scanned={report['summary']['total_scanned']} "
        f"moved={report['summary']['moved']} "
        f"skipped={report['summary']['skipped']} "
        f"unchanged={report['summary']['unchanged']} "
        f"errors={report['summary']['error']}"
    )
    return 0 if report["summary"]["error"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
