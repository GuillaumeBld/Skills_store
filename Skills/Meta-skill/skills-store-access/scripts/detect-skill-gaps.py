#!/usr/bin/env python3
"""
Detect Skill Gaps
Compare identified skill requirements against catalog to find missing skills.
Prioritizes which missing skills should be created based on relevance.
"""

import os
import sys
import json
from typing import List, Dict, Tuple
from pathlib import Path

LIBRARY_ROOT = os.getenv('LIBRARY_ROOT', os.path.expanduser('~/Documents/Skills/Skills_librairie'))
CATALOG_FILE = os.path.join(LIBRARY_ROOT, 'catalog.json')
INDEX_FILE = os.path.join(LIBRARY_ROOT, 'skills-index.json')

def load_catalog():
    """Load skills catalog"""
    if not os.path.exists(CATALOG_FILE):
        print(f"Error: Catalog not found at {CATALOG_FILE}", file=sys.stderr)
        print("Run: python3 Skills/skill-library-manager/scripts/catalog-builder.py", file=sys.stderr)
        return None
    
    with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_index():
    """Load lightweight skills index"""
    if not os.path.exists(INDEX_FILE):
        return None
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_catalog_for_skill(requirement: Dict, catalog: Dict, index: Dict = None) -> Tuple[bool, float, str]:
    """
    Search catalog for a skill requirement.
    
    Args:
        requirement: Skill requirement dict (from JAAT or keyword analysis)
        catalog: Full catalog dict
        index: Lightweight index (optional, for faster search)
    
    Returns:
        (found: bool, relevance: float, skill_name: str)
    """
    # Extract search terms from requirement
    search_terms = []
    
    if requirement.get('type') == 'task' and requirement.get('description'):
        # Extract keywords from task description
        desc = requirement['description'].lower()
        words = [w for w in desc.split() if len(w) > 4][:5]
        search_terms.extend(words)
    
    if requirement.get('type') == 'skill' and requirement.get('label'):
        search_terms.append(requirement['label'].lower())
    
    if not search_terms:
        return False, 0.0, ""
    
    # Search in catalog
    skills = catalog.get('skills', [])
    best_match = None
    best_score = 0.0
    
    for skill in skills:
        score = 0.0
        skill_name_lower = skill.get('name', '').lower()
        skill_desc_lower = skill.get('description', '').lower()
        
        # Check name match
        for term in search_terms:
            if term in skill_name_lower:
                score += 0.5
            if term in skill_desc_lower:
                score += 0.3
        
        # Check tags/keywords
        tags = [t.lower() for t in skill.get('tags', [])]
        for term in search_terms:
            if term in tags:
                score += 0.2
        
        if score > best_score:
            best_score = score
            best_match = skill.get('name')
    
    found = best_score > 0.4  # Threshold for "found"
    return found, best_score, best_match or ""

def find_gaps(required_skills: List[Dict], catalog: Dict, index: Dict = None) -> List[Dict]:
    """
    Find skills that don't exist in catalog.
    
    Args:
        required_skills: List of skill requirement dicts
        catalog: Catalog dict
        index: Lightweight index (optional)
    
    Returns:
        List of missing skill requirements with priority scores
    """
    gaps = []
    
    for req in required_skills:
        found, relevance, matched_skill = search_catalog_for_skill(req, catalog, index)
        
        if not found:
            # Calculate priority score
            priority = req.get('priority', 'medium')
            priority_score = {'high': 0.9, 'medium': 0.6, 'low': 0.3}.get(priority, 0.6)
            
            gaps.append({
                'requirement': req,
                'priority_score': priority_score,
                'matched_skill': matched_skill if matched_skill else None,
                'match_relevance': relevance
            })
    
    return gaps

def prioritize_creation(gaps: List[Dict]) -> List[Dict]:
    """
    Prioritize which missing skills to create.
    
    Args:
        gaps: List of gap dicts from find_gaps()
    
    Returns:
        Sorted list of gaps by creation priority
    """
    # Sort by priority score (highest first)
    gaps.sort(key=lambda x: x['priority_score'], reverse=True)
    
    # Further prioritize by match relevance (lower relevance = more unique skill needed)
    # Skills with low match relevance but high priority are most important
    for gap in gaps:
        # Inverse match relevance: lower match = higher need to create
        uniqueness_bonus = (1.0 - gap['match_relevance']) * 0.3
        gap['final_priority'] = gap['priority_score'] + uniqueness_bonus
    
    gaps.sort(key=lambda x: x['final_priority'], reverse=True)
    return gaps

def generate_skill_name_from_requirement(requirement: Dict) -> str:
    """Generate a suggested skill name from requirement"""
    if requirement.get('type') == 'skill' and requirement.get('label'):
        # Use skill label, convert to kebab-case
        label = requirement['label'].lower()
        name = label.replace(' ', '-').replace('_', '-')
        # Remove special chars
        name = ''.join(c if c.isalnum() or c == '-' else '' for c in name)
        return name
    
    if requirement.get('type') == 'task' and requirement.get('description'):
        # Extract key words from description
        desc = requirement['description'].lower()
        words = [w for w in desc.split() if len(w) > 4][:2]
        if words:
            return '-'.join(words)
    
    return 'new-skill'

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Detect skill gaps in catalog',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('requirements_file', nargs='?',
                        help='JSON file with skill requirements (stdin if not provided)')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    parser.add_argument('--max-results', type=int, default=10,
                        help='Maximum gaps to return (default: 10)')
    
    args = parser.parse_args()
    
    # Load requirements
    if args.requirements_file:
        with open(args.requirements_file, 'r') as f:
            requirements = json.load(f)
    else:
        # Read from stdin
        requirements = json.load(sys.stdin)
    
    # Ensure requirements is a list
    if isinstance(requirements, dict) and 'skill_requirements' in requirements:
        requirements = requirements['skill_requirements']
    elif not isinstance(requirements, list):
        requirements = [requirements]
    
    # Load catalog
    catalog = load_catalog()
    if not catalog:
        sys.exit(1)
    
    index = load_index()  # Optional
    
    # Find gaps
    gaps = find_gaps(requirements, catalog, index)
    
    # Prioritize
    prioritized = prioritize_creation(gaps)
    
    # Limit results
    prioritized = prioritized[:args.max_results]
    
    # Generate skill name suggestions
    for gap in prioritized:
        gap['suggested_skill_name'] = generate_skill_name_from_requirement(gap['requirement'])
    
    if args.json:
        print(json.dumps({
            'total_gaps': len(gaps),
            'prioritized_gaps': prioritized
        }, indent=2))
    else:
        print(f"Found {len(gaps)} skill gaps")
        print(f"\nTop {len(prioritized)} prioritized for creation:\n")
        
        for i, gap in enumerate(prioritized, 1):
            req = gap['requirement']
            print(f"{i}. {gap['suggested_skill_name']} (priority: {gap['final_priority']:.2f})")
            if req.get('description'):
                print(f"   Description: {req['description'][:80]}...")
            if req.get('label'):
                print(f"   Skill: {req['label']}")
            print()
    
    return 0 if prioritized else 1

if __name__ == '__main__':
    sys.exit(main())
