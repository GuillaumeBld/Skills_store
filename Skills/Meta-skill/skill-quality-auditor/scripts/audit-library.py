#!/usr/bin/env python3
"""
Batch audit all skills in library
"""

import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from audit_skill import SkillAuditor

def audit_library(library_path, min_score=0):
    """Audit all skills in library"""
    skills_dir = Path(library_path) / "skills"
    
    if not skills_dir.exists():
        print(f"Skills directory not found: {skills_dir}")
        return
    
    results = []
    
    print(f"\n{'='*60}")
    print("Library Quality Audit")
    print(f"{'='*60}\n")
    
    # Audit each skill
    for skill_path in sorted(skills_dir.iterdir()):
        if not skill_path.is_dir():
            continue
        
        if not (skill_path / "SKILL.md").exists():
            continue
        
        auditor = SkillAuditor(skill_path)
        result = auditor.audit()
        result['name'] = skill_path.name
        results.append(result)
        
        print(f"{skill_path.name}: {result['score']}/100 ({result['grade']})")
    
    if not results:
        print("No skills found to audit")
        return
    
    # Summary statistics
    avg_score = sum(r['score'] for r in results) / len(results)
    
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}\n")
    print(f"Total skills: {len(results)}")
    print(f"Average score: {avg_score:.1f}/100\n")
    
    # Grade distribution
    grades = {
        'Excellent (90+)': sum(1 for r in results if r['score'] >= 90),
        'Good (75-89)': sum(1 for r in results if 75 <= r['score'] < 90),
        'Fair (60-74)': sum(1 for r in results if 60 <= r['score'] < 75),
        'Poor (<60)': sum(1 for r in results if r['score'] < 60)
    }
    
    for grade, count in grades.items():
        if count > 0:
            print(f"{grade}: {count} skill(s)")
    
    # Top issues across all skills
    all_issues = []
    for result in results:
        all_issues.extend(result['issues'])
    
    if all_issues:
        issue_counts = {}
        for issue in all_issues:
            msg = issue['message'].split(':')[0]  # Get issue type
            issue_counts[msg] = issue_counts.get(msg, 0) + 1
        
        print(f"\nTop Issues Across Library:")
        for i, (issue, count) in enumerate(sorted(issue_counts.items(), key=lambda x: -x[1])[:5], 1):
            print(f"{i}. {issue} ({count} skills)")
    
    # Failed skills
    failed = [r for r in results if r['score'] < min_score]
    if failed:
        print(f"\n{'='*60}")
        print(f"Skills Below Minimum Score ({min_score})")
        print(f"{'='*60}\n")
        for result in failed:
            print(f"- {result['name']}: {result['score']}/100")
        return 1
    
    return 0

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Audit all skills in library')
    parser.add_argument('library_path', nargs='?', default='.', help='Path to library root')
    parser.add_argument('--min-score', type=int, default=0, help='Minimum required score')
    
    args = parser.parse_args()
    
    exit_code = audit_library(args.library_path, args.min_score)
    sys.exit(exit_code or 0)
