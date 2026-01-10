#!/usr/bin/env python3
"""
Catalog Builder for Skills Library
Scans skills/ directory and generates catalog.json with metadata
"""

import os
import json
import yaml
import re
from pathlib import Path
from datetime import datetime

LIBRARY_ROOT = os.getenv('LIBRARY_ROOT', os.path.expanduser('~/Skills_librairie'))
SKILLS_DIR = os.path.join(LIBRARY_ROOT, 'skills')
PACKAGED_DIR = os.path.join(LIBRARY_ROOT, 'packaged')
CATALOG_FILE = os.path.join(LIBRARY_ROOT, 'catalog.json')

def extract_frontmatter(skill_md_path):
    """Extract YAML frontmatter from SKILL.md"""
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match frontmatter between --- delimiters
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if match:
            frontmatter = yaml.safe_load(match.group(1))
            return frontmatter
        return {}
    except Exception as e:
        print(f"Warning: Could not parse {skill_md_path}: {e}")
        return {}

def get_file_size(filepath):
    """Get human-readable file size"""
    if not os.path.exists(filepath):
        return "N/A"
    
    size_bytes = os.path.getsize(filepath)
    
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f}MB"

def scan_skills():
    """Scan skills directory and extract metadata"""
    skills = []
    
    if not os.path.exists(SKILLS_DIR):
        print(f"Skills directory not found: {SKILLS_DIR}")
        return skills
    
    for skill_name in os.listdir(SKILLS_DIR):
        skill_path = os.path.join(SKILLS_DIR, skill_name)
        
        # Skip if not a directory
        if not os.path.isdir(skill_path):
            continue
        
        # Look for SKILL.md
        skill_md = os.path.join(skill_path, 'SKILL.md')
        if not os.path.exists(skill_md):
            print(f"Warning: {skill_name} has no SKILL.md, skipping")
            continue
        
        # Extract metadata
        metadata = extract_frontmatter(skill_md)
        
        # Build skill entry
        skill_entry = {
            "name": metadata.get('name', skill_name),
            "version": metadata.get('version', '1.0.0'),
            "description": metadata.get('description', 'No description available'),
            "author": metadata.get('author', 'Unknown'),
            "created": metadata.get('created', datetime.now().strftime('%Y-%m-%d')),
            "updated": metadata.get('updated', datetime.now().strftime('%Y-%m-%d')),
            "tags": metadata.get('tags', []),
            "dependencies": metadata.get('dependencies', []),
            "compatibility": metadata.get('compatibility', ['claude.ai']),
            "license": metadata.get('license', 'MIT'),
            "location": f"skills/{skill_name}/",
            "package": f"packaged/{skill_name}.skill",
            "size": get_file_size(os.path.join(PACKAGED_DIR, f"{skill_name}.skill"))
        }
        
        skills.append(skill_entry)
    
    # Sort by name
    skills.sort(key=lambda x: x['name'])
    
    return skills

def build_categories(skills):
    """Build category index from skills tags"""
    categories = {}
    
    for skill in skills:
        for tag in skill.get('tags', []):
            if tag not in categories:
                categories[tag] = []
            categories[tag].append(skill['name'])
    
    return categories

def generate_catalog():
    """Generate complete catalog.json"""
    print("Scanning skills directory...")
    skills = scan_skills()
    
    print(f"Found {len(skills)} skills")
    
    categories = build_categories(skills)
    
    catalog = {
        "version": "1.0.0",
        "updated": datetime.now().isoformat(),
        "repository": "https://github.com/GuillaumeBld/Skills_librairie",
        "skills": skills,
        "categories": categories,
        "stats": {
            "total_skills": len(skills),
            "total_categories": len(categories),
            "last_scan": datetime.now().isoformat()
        }
    }
    
    # Write catalog
    with open(CATALOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Catalog written to {CATALOG_FILE}")
    print(f"  Total skills: {len(skills)}")
    print(f"  Categories: {len(categories)}")
    
    return catalog

if __name__ == '__main__':
    try:
        catalog = generate_catalog()
        
        # Print summary
        print("\nSkills by category:")
        for category, skill_names in sorted(catalog['categories'].items()):
            print(f"  {category}: {len(skill_names)} skills")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
