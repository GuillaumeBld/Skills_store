#!/usr/bin/env python3
"""
Platform Detection for Skills Store Access
Detects the current platform (Cursor/Codex, Claude.ai, API) and capabilities
"""

import os
import sys
import subprocess
from pathlib import Path

def detect_platform():
    """Detect which platform we're running on"""
    platform_info = {
        'platform': 'unknown',
        'skills_dir': None,
        'has_skill_installer': False,
        'has_gh_cli': False,
        'has_git': False,
        'can_install_local': False,
        'can_use_api': False,
    }
    
    # Check for Codex/Cursor (most common for development)
    codex_home = os.environ.get('CODEX_HOME', os.path.expanduser('~/.codex'))
    codex_skills = os.path.join(codex_home, 'skills')
    
    if os.path.exists(codex_skills):
        platform_info['platform'] = 'codex'
        platform_info['skills_dir'] = codex_skills
        platform_info['can_install_local'] = True
        
        # Check for skill-installer
        skill_installer = os.path.join(codex_skills, '.system', 'skill-installer', 'scripts', 'install-skill-from-github.py')
        if os.path.exists(skill_installer):
            platform_info['has_skill_installer'] = True
    
    # Check for Claude.ai environment variables (if running in Claude.ai context)
    if os.environ.get('CLAUDE_AI_ENV'):
        platform_info['platform'] = 'claude-ai'
        platform_info['can_use_api'] = True
    
    # Check for API environment
    if os.environ.get('ANTHROPIC_API_KEY'):
        platform_info['can_use_api'] = True
        if platform_info['platform'] == 'unknown':
            platform_info['platform'] = 'api'
    
    # Check for GitHub CLI
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            platform_info['has_gh_cli'] = True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Check for Git
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            platform_info['has_git'] = True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    return platform_info

def get_installation_method(platform_info):
    """Get recommended installation method based on platform"""
    if platform_info['has_skill_installer']:
        return 'skill-installer'
    elif platform_info['can_install_local']:
        return 'manual-local'
    elif platform_info['can_use_api']:
        return 'api'
    else:
        return 'manual-download'

if __name__ == '__main__':
    info = detect_platform()
    
    print("Platform Detection Results:")
    print(f"  Platform: {info['platform']}")
    print(f"  Skills Directory: {info['skills_dir'] or 'N/A'}")
    print(f"  Has Skill Installer: {info['has_skill_installer']}")
    print(f"  Has GitHub CLI: {info['has_gh_cli']}")
    print(f"  Has Git: {info['has_git']}")
    print(f"  Can Install Local: {info['can_install_local']}")
    print(f"  Can Use API: {info['can_use_api']}")
    print(f"  Recommended Method: {get_installation_method(info)}")
    
    sys.exit(0 if info['platform'] != 'unknown' else 1)
