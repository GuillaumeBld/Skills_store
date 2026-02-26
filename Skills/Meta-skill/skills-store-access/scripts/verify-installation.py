#!/usr/bin/env python3
"""
Verification Script for Skills Store Access
Verifies that skill-library-manager is properly installed and accessible
"""

import os
import sys
from pathlib import Path

REPO_CANDIDATES = [
    os.getenv('LIBRARY_ROOT', ''),
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')),
    os.path.expanduser('~/Skills_librairie'),
    os.path.expanduser('~/Skills_store'),
    os.path.expanduser('~/Documents/Skills/Skills_librairie'),
    os.path.expanduser('~/Documents/Skills/Skills_store'),
]


def is_library_root(path: str) -> bool:
    """Detect if path looks like a Skills library repository root."""
    if not path:
        return False
    return (
        os.path.isdir(path)
        and (
            os.path.isdir(os.path.join(path, 'Skills'))
            or os.path.isdir(os.path.join(path, 'skills'))
        )
    )


def discover_repository_root() -> str:
    """Find a repository root from known candidates."""
    for candidate in REPO_CANDIDATES:
        if not candidate:
            continue
        candidate = os.path.abspath(os.path.expanduser(candidate))
        if is_library_root(candidate):
            return candidate
    return ""


def verify_skill_library_manager():
    """Verify skill-library-manager installation"""
    issues = []
    warnings = []
    success = []
    
    # Check for Codex skills directory
    codex_home = os.environ.get('CODEX_HOME', os.path.expanduser('~/.codex'))
    skills_dir = os.path.join(codex_home, 'skills')
    
    if not os.path.exists(skills_dir):
        issues.append(f"Skills directory not found: {skills_dir}")
        return issues, warnings, success
    
    success.append(f"✓ Skills directory exists: {skills_dir}")
    
    # Check for skill-library-manager
    skill_path = os.path.join(skills_dir, 'skill-library-manager')
    if not os.path.exists(skill_path):
        issues.append(f"skill-library-manager not installed at: {skill_path}")
        return issues, warnings, success
    
    success.append(f"✓ skill-library-manager found at: {skill_path}")
    
    # Check for SKILL.md
    skill_md = os.path.join(skill_path, 'SKILL.md')
    if not os.path.exists(skill_md):
        issues.append(f"SKILL.md not found in skill-library-manager")
    else:
        success.append("✓ SKILL.md exists")
    
    # Check for scripts directory
    scripts_dir = os.path.join(skill_path, 'scripts')
    if not os.path.exists(scripts_dir):
        warnings.append("scripts/ directory not found (may be optional)")
    else:
        success.append("✓ scripts/ directory exists")
        
        # Check for key scripts
        key_scripts = ['create-skill.sh', 'search-skills.py', 'catalog-builder.py', 'sync-library.sh']
        for script in key_scripts:
            script_path = os.path.join(scripts_dir, script)
            if os.path.exists(script_path):
                success.append(f"  ✓ {script} exists")
            else:
                warnings.append(f"  ⚠ {script} not found")
    
    # Check repository access
    repo_path = discover_repository_root()
    if repo_path:
        success.append(f"✓ Repository found at: {repo_path}")
        
        # Check catalog.json
        catalog_path = os.path.join(repo_path, 'catalog.json')
        if os.path.exists(catalog_path):
            success.append("✓ catalog.json exists")
        else:
            warnings.append("⚠ catalog.json not found (run catalog-builder.py to generate)")
    else:
        warnings.append("⚠ Repository not found (set LIBRARY_ROOT if using a custom location)")
    
    return issues, warnings, success

def main():
    """Main verification function"""
    print("Verifying Skills Store Access Installation...\n")
    
    issues, warnings, success = verify_skill_library_manager()
    
    # Print results
    if success:
        print("Success:")
        for msg in success:
            print(f"  {msg}")
        print()
    
    if warnings:
        print("Warnings:")
        for msg in warnings:
            print(f"  {msg}")
        print()
    
    if issues:
        print("Issues (must be fixed):")
        for msg in issues:
            print(f"  ✗ {msg}")
        print()
        return 1
    
    print("✓ All checks passed! Skills Store Access is ready to use.\n")
    return 0

if __name__ == '__main__':
    sys.exit(main())
