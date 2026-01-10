#!/usr/bin/env python3
"""
Search Skills Catalog
Search by keywords, tags, or list all skills
"""

import os
import json
import sys
from pathlib import Path

# Get script directory and find library root dynamically (same logic as catalog-builder.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
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

CATALOG_FILE = os.path.join(LIBRARY_ROOT, 'catalog.json')

def load_catalog():
    """Load catalog.json"""
    if not os.path.exists(CATALOG_FILE):
        print(f"Error: Catalog not found at {CATALOG_FILE}")
        print("Run: python3 scripts/catalog-builder.py")
        sys.exit(1)
    
    with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_by_keyword(catalog, keyword):
    """Search skills by keyword in name/description"""
    keyword_lower = keyword.lower()
    matches = []
    
    for skill in catalog['skills']:
        # Search in name and description
        if (keyword_lower in skill['name'].lower() or 
            keyword_lower in skill['description'].lower()):
            matches.append(skill)
    
    return matches

def search_by_tag(catalog, tag):
    """Search skills by tag"""
    matches = []
    tag_lower = tag.lower()
    
    for skill in catalog['skills']:
        skill_tags = [t.lower() for t in skill.get('tags', [])]
        if tag_lower in skill_tags:
            matches.append(skill)
    
    return matches

def search_by_author(catalog, author):
    """Search skills by author"""
    matches = []
    author_lower = author.lower()
    
    for skill in catalog['skills']:
        if author_lower in skill.get('author', '').lower():
            matches.append(skill)
    
    return matches

def display_skill(skill, index=None):
    """Display skill information"""
    prefix = f"{index}. " if index else ""
    
    print(f"\n{prefix}{skill['name']} (v{skill['version']})")
    print(f"  Description: {skill['description']}")
    print(f"  Author: {skill['author']}")
    print(f"  Tags: {', '.join(skill['tags'])}")
    print(f"  Created: {skill['created']} | Updated: {skill['updated']}")
    print(f"  Location: {skill['location']}")
    print(f"  Package: {skill['package']} ({skill['size']})")
    
    if skill.get('dependencies'):
        print(f"  Dependencies: {', '.join(skill['dependencies'])}")

def display_results(matches, query_type, query):
    """Display search results"""
    if not matches:
        print(f"\nNo skills found {query_type} '{query}'")
        return
    
    print(f"\n{'='*60}")
    print(f"Found {len(matches)} skill(s) {query_type} '{query}':")
    print('='*60)
    
    for i, skill in enumerate(matches, 1):
        display_skill(skill, i)
    
    print(f"\n{'='*60}")

def list_all_skills(catalog):
    """List all skills in catalog"""
    skills = catalog['skills']
    
    print(f"\n{'='*60}")
    print(f"All Skills in Library ({len(skills)} total)")
    print('='*60)
    
    for i, skill in enumerate(skills, 1):
        display_skill(skill, i)
    
    print(f"\n{'='*60}")
    
    # Show category breakdown
    print("\nSkills by Category:")
    for category, skill_names in sorted(catalog['categories'].items()):
        print(f"  {category}: {len(skill_names)} skill(s)")

def list_categories(catalog):
    """List all categories with skill counts"""
    print(f"\n{'='*60}")
    print("Categories")
    print('='*60)
    
    for category, skill_names in sorted(catalog['categories'].items()):
        print(f"\n{category} ({len(skill_names)} skills):")
        for name in sorted(skill_names):
            print(f"  - {name}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Search Skills Library catalog')
    parser.add_argument('query', nargs='?', help='Search keyword')
    parser.add_argument('--tag', '-t', help='Search by tag')
    parser.add_argument('--author', '-a', help='Search by author')
    parser.add_argument('--all', action='store_true', help='List all skills')
    parser.add_argument('--categories', '-c', action='store_true', help='List all categories')
    parser.add_argument('--stats', '-s', action='store_true', help='Show library statistics')
    
    args = parser.parse_args()
    
    # Load catalog
    catalog = load_catalog()
    
    # Handle different search modes
    if args.stats:
        print(f"\n{'='*60}")
        print("Library Statistics")
        print('='*60)
        stats = catalog.get('stats', {})
        print(f"Total skills: {stats.get('total_skills', len(catalog['skills']))}")
        print(f"Total categories: {stats.get('total_categories', len(catalog['categories']))}")
        print(f"Last updated: {catalog.get('updated', 'Unknown')}")
        print(f"Repository: {catalog.get('repository', 'Unknown')}")
        
    elif args.categories:
        list_categories(catalog)
        
    elif args.all:
        list_all_skills(catalog)
        
    elif args.tag:
        matches = search_by_tag(catalog, args.tag)
        display_results(matches, "with tag", args.tag)
        
    elif args.author:
        matches = search_by_author(catalog, args.author)
        display_results(matches, "by author", args.author)
        
    elif args.query:
        matches = search_by_keyword(catalog, args.query)
        display_results(matches, "matching", args.query)
        
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python3 search-skills.py database")
        print("  python3 search-skills.py --tag backup")
        print("  python3 search-skills.py --author Guillaume")
        print("  python3 search-skills.py --all")
        print("  python3 search-skills.py --categories")

if __name__ == '__main__':
    main()
