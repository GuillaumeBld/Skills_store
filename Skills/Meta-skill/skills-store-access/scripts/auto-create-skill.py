#!/usr/bin/env python3
"""
Auto-Create Skill
Creates a new skill from requirements and authoritative sources using skill-creator workflow.
This is a framework that integrates with the skill-creator to generate skills automatically.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional

LIBRARY_ROOT = os.getenv('LIBRARY_ROOT', os.path.expanduser('~/Documents/Skills/Skills_librairie'))
SKILL_CREATOR_PATH = os.path.join(LIBRARY_ROOT, 'Skills/Meta-skill/skill-creator/scripts/init_skill.py')

def generate_skill_content(skill_name: str, requirement: Dict, sources: List[Dict] = None) -> Dict:
    """
    Generate SKILL.md content from requirement and sources.
    
    Args:
        skill_name: Name of the skill (kebab-case)
        requirement: Skill requirement dict
        sources: List of authoritative sources (optional)
    
    Returns:
        Dict with skill content structure
    """
    # Extract description from requirement
    description = requirement.get('description', '')
    if not description and requirement.get('label'):
        description = requirement.get('label')
    if not description:
        description = f"Skill for {skill_name.replace('-', ' ')}"
    
    # Generate frontmatter description
    frontmatter_desc = f"{description}. Use when working with {skill_name.replace('-', ' ')} or related tasks."
    
    # Generate SKILL.md body
    body = f"""# {skill_name.replace('-', ' ').title()}

## Overview

{description}

## Quick Start

[Content will be generated from authoritative sources]

## Resources

"""
    
    # Add source references if available
    if sources:
        body += "### Authoritative Sources\n\n"
        for source in sources[:5]:  # Limit to top 5
            source_type = source.get('type', 'unknown')
            url = source.get('url', '')
            if url:
                body += f"- [{source_type}]({url})\n"
        body += "\n"
    
    # Add O*NET or EuropaCode reference if available
    if requirement.get('source') == 'onet' and requirement.get('id'):
        body += f"\n### O*NET Reference\n\n"
        body += f"- Task ID: {requirement['id']}\n"
        body += f"- Description: {requirement.get('description', 'N/A')}\n"
    
    if requirement.get('source') == 'europacode' and requirement.get('code'):
        body += f"\n### EuropaCode Reference\n\n"
        body += f"- Code: {requirement['code']}\n"
        body += f"- Label: {requirement.get('label', 'N/A')}\n"
    
    return {
        'name': skill_name,
        'frontmatter': {
            'name': skill_name,
            'description': frontmatter_desc
        },
        'body': body,
        'category': _infer_category(requirement)
    }

def _infer_category(requirement: Dict) -> str:
    """Infer skill category from requirement"""
    desc = (requirement.get('description', '') + ' ' + requirement.get('label', '')).lower()
    
    if any(word in desc for word in ['docker', 'kubernetes', 'deploy', 'infrastructure', 'vps']):
        return 'Infrastructure-DevOps'
    elif any(word in desc for word in ['n8n', 'workflow', 'automation']):
        return 'Automation'
    elif any(word in desc for word in ['rag', 'vector', 'embedding', 'llm']):
        return 'AI-Agents'
    elif any(word in desc for word in ['database', 'sql', 'query']):
        return 'Development'
    else:
        return 'Development'  # Default

def create_skill_structure(skill_content: Dict, output_dir: Optional[str] = None) -> str:
    """
    Create skill directory structure using skill-creator init_skill.py
    
    Args:
        skill_content: Dict from generate_skill_content()
        output_dir: Directory to create skill in (default: Skills/<category>/)
    
    Returns:
        Path to created skill directory
    """
    skill_name = skill_content['name']
    category = skill_content.get('category', 'Development')
    
    if output_dir is None:
        output_dir = os.path.join(LIBRARY_ROOT, 'Skills', category)
    
    skill_path = os.path.join(output_dir, skill_name)
    
    # Check if skill-creator script exists
    if not os.path.exists(SKILL_CREATOR_PATH):
        print(f"Error: skill-creator not found at {SKILL_CREATOR_PATH}", file=sys.stderr)
        return None
    
    try:
        # Use skill-creator to initialize structure
        result = subprocess.run(
            [sys.executable, SKILL_CREATOR_PATH, skill_name, '--path', output_dir],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"Error initializing skill: {result.stderr}", file=sys.stderr)
            return None
        
        # Update SKILL.md with generated content
        skill_md_path = os.path.join(skill_path, 'SKILL.md')
        if os.path.exists(skill_md_path):
            # Read existing, replace with generated
            with open(skill_md_path, 'w', encoding='utf-8') as f:
                # Write frontmatter
                f.write("---\n")
                for key, value in skill_content['frontmatter'].items():
                    f.write(f"{key}: {value}\n")
                f.write("---\n\n")
                # Write body
                f.write(skill_content['body'])
        
        return skill_path
    
    except Exception as e:
        print(f"Error creating skill: {e}", file=sys.stderr)
        return None

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Auto-create skill from requirement and sources'
    )
    
    parser.add_argument('requirement_file', nargs='?',
                        help='JSON file with skill requirement (stdin if not provided)')
    parser.add_argument('--sources-file', 
                        help='JSON file with authoritative sources')
    parser.add_argument('--output-dir',
                        help='Directory to create skill in (default: auto-detect category)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be created without creating')
    
    args = parser.parse_args()
    
    # Load requirement
    if args.requirement_file:
        with open(args.requirement_file, 'r') as f:
            requirement = json.load(f)
    else:
        requirement = json.load(sys.stdin)
    
    # Extract requirement if wrapped
    if isinstance(requirement, dict) and 'requirement' in requirement:
        requirement = requirement['requirement']
    
    # Load sources if provided
    sources = []
    if args.sources_file:
        with open(args.sources_file, 'r') as f:
            sources_data = json.load(f)
            if isinstance(sources_data, dict):
                # Extract sources for this skill
                skill_name = requirement.get('suggested_skill_name', requirement.get('name', 'skill'))
                sources = sources_data.get(skill_name, [])
            elif isinstance(sources_data, list):
                sources = sources_data
    
    # Generate skill name
    skill_name = requirement.get('suggested_skill_name') or requirement.get('name', 'new-skill')
    skill_name = skill_name.lower().replace(' ', '-')
    
    # Generate content
    skill_content = generate_skill_content(skill_name, requirement, sources)
    
    if args.dry_run:
        print("Would create skill:")
        print(f"  Name: {skill_name}")
        print(f"  Category: {skill_content['category']}")
        print(f"\nFrontmatter:")
        print(json.dumps(skill_content['frontmatter'], indent=2))
        print(f"\nSKILL.md preview (first 500 chars):")
        print(skill_content['body'][:500] + "...")
        return 0
    
    # Create skill
    skill_path = create_skill_structure(skill_content, args.output_dir)
    
    if skill_path:
        print(f"Created skill: {skill_path}")
        print(f"\nNext steps:")
        print(f"1. Review and edit: {os.path.join(skill_path, 'SKILL.md')}")
        print(f"2. Add scripts/references/assets as needed")
        print(f"3. Test the skill")
        print(f"4. Run catalog-builder.py to update catalog")
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
