#!/usr/bin/env python3
"""
Catalog Builder for Skills Library
Scans Skills/ directory recursively (with categories) and generates catalog.json with metadata.
Auto-detects LIBRARY_ROOT by walking up from script location or uses LIBRARY_ROOT env var.
Supports both Skills/ (capital) and skills/ (lowercase) directory structures.
"""

import os
import json
import yaml
import re
from pathlib import Path
from datetime import datetime

# Get script directory and find library root dynamically
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Try to find library root: up from script to Skills_librairie root
LIBRARY_ROOT = os.getenv('LIBRARY_ROOT')
if not LIBRARY_ROOT:
    # Walk up from script location to find repository root
    current = SCRIPT_DIR
    while current != os.path.dirname(current):  # Stop at filesystem root
        if os.path.basename(current) == 'Skills_librairie' or os.path.basename(current) == 'Skills_store':
            LIBRARY_ROOT = current
            break
        # Check if we're in a repo by looking for Skills/ directory
        skills_candidate = os.path.join(current, 'Skills')
        if os.path.exists(skills_candidate) and os.path.isdir(skills_candidate):
            LIBRARY_ROOT = current
            break
        current = os.path.dirname(current)
    else:
        # Fallback to default
        LIBRARY_ROOT = os.path.expanduser('~/Skills_librairie')

# Try Skills (capital) first, then skills (lowercase) for compatibility
SKILLS_DIR_CAPITAL = os.path.join(LIBRARY_ROOT, 'Skills')
SKILLS_DIR_LOWERCASE = os.path.join(LIBRARY_ROOT, 'skills')
if os.path.exists(SKILLS_DIR_CAPITAL) and os.path.isdir(SKILLS_DIR_CAPITAL):
    SKILLS_DIR = SKILLS_DIR_CAPITAL
elif os.path.exists(SKILLS_DIR_LOWERCASE) and os.path.isdir(SKILLS_DIR_LOWERCASE):
    SKILLS_DIR = SKILLS_DIR_LOWERCASE
else:
    SKILLS_DIR = SKILLS_DIR_CAPITAL  # Default to capital for error message

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
            if frontmatter:
                # Convert date/datetime objects to strings for JSON serialization
                for key in ['created', 'updated', 'date']:
                    if key in frontmatter and frontmatter[key]:
                        if isinstance(frontmatter[key], (datetime,)):
                            frontmatter[key] = frontmatter[key].strftime('%Y-%m-%d')
                        elif hasattr(frontmatter[key], 'strftime'):  # date object
                            frontmatter[key] = frontmatter[key].strftime('%Y-%m-%d')
            return frontmatter or {}
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
    """Scan skills directory recursively and extract metadata from categorized structure"""
    skills = []
    
    if not os.path.exists(SKILLS_DIR):
        print(f"Skills directory not found: {SKILLS_DIR}")
        print(f"  Checked: {SKILLS_DIR_CAPITAL}")
        print(f"  Checked: {SKILLS_DIR_LOWERCASE}")
        print(f"  LIBRARY_ROOT: {LIBRARY_ROOT}")
        return skills
    
    print(f"Scanning skills directory: {SKILLS_DIR}")
    
    # Walk recursively through Skills directory to find all SKILL.md files
    for root, dirs, files in os.walk(SKILLS_DIR):
        # Skip hidden directories and special directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        # Look for SKILL.md in current directory
        skill_md = os.path.join(root, 'SKILL.md')
        if not os.path.exists(skill_md):
            continue
        
        # Extract relative path from Skills directory to determine category and skill name
        rel_path = os.path.relpath(root, SKILLS_DIR)
        path_parts = rel_path.split(os.sep)
        
        # Determine category and skill name from path structure
        # Examples:
        # - Skills/Meta-skill/superpowers -> category: Meta-skill, name: superpowers
        # - Skills/Development/ios-simulator-skill -> category: Development, name: ios-simulator-skill
        # - Skills/skill-library-manager -> category: (top-level), name: skill-library-manager
        if len(path_parts) == 1:
            # Top-level skill (legacy structure)
            category = 'Uncategorized'
            skill_name = path_parts[0]
        elif len(path_parts) >= 2:
            # Categorized structure: Skills/Category/SkillName
            category = path_parts[0]
            skill_name = path_parts[-1]
        else:
            category = 'Uncategorized'
            skill_name = os.path.basename(root)
        
        # Extract metadata
        metadata = extract_frontmatter(skill_md)
        
        # Use category from metadata if provided, otherwise use path-based category
        category = metadata.get('category', category)
        
        # Build relative location path (use Skills with capital S in output)
        location_parts = ['Skills'] + path_parts
        location = '/'.join(location_parts) + '/'
        
        # Build skill entry
        skill_entry = {
            "name": metadata.get('name', skill_name),
            "category": category,
            "version": metadata.get('version', '1.0.0'),
            "description": metadata.get('description', 'No description available'),
            "author": metadata.get('author', 'Unknown'),
            "created": metadata.get('created', datetime.now().strftime('%Y-%m-%d')),
            "updated": metadata.get('updated', datetime.now().strftime('%Y-%m-%d')),
            "tags": metadata.get('tags', []),
            "dependencies": metadata.get('dependencies', []),
            "compatibility": metadata.get('compatibility', ['claude.ai', 'claude-code']),
            "license": metadata.get('license', 'MIT'),
            "location": location,
            "absolute_path": root,
            "package": f"packaged/{skill_name}.skill",
            "size": get_file_size(os.path.join(PACKAGED_DIR, f"{skill_name}.skill")) if PACKAGED_DIR and os.path.exists(PACKAGED_DIR) else "N/A"
        }
        
        skills.append(skill_entry)
    
    # Sort by category, then name
    skills.sort(key=lambda x: (x.get('category', 'Uncategorized'), x['name']))
    
    return skills

def build_categories(skills):
    """Build category index from skills category field (from directory structure)"""
    categories = {}
    
    for skill in skills:
        category = skill.get('category', 'Uncategorized')
        if category not in categories:
            categories[category] = []
        categories[category].append(skill['name'])
    
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
