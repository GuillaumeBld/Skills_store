#!/usr/bin/env python3
"""
Generate Lightweight Skills Index
Creates a minimal index of skills for efficient discovery without loading full catalog into context.
Only includes: name, description (max 50 words), tags, category, keywords
"""

import os
import json
import re
import sys
from pathlib import Path
from datetime import datetime

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
        # Fallback to default or try common locations
        for path in [os.path.expanduser('~/Skills_librairie'),
                     os.path.expanduser('~/Documents/Skills/Skills_librairie')]:
            if os.path.exists(path):
                LIBRARY_ROOT = path
                break
        else:
            LIBRARY_ROOT = os.path.expanduser('~/Documents/Skills/Skills_librairie')  # Final fallback

CATALOG_FILE = os.path.join(LIBRARY_ROOT, 'catalog.json')
INDEX_FILE = os.path.join(LIBRARY_ROOT, 'skills-index.json')

def extract_keywords(description, tags, name):
    """Extract keywords from description, tags, and name for better matching"""
    keywords = set()
    
    # Add tags as keywords
    keywords.update(tag.lower() for tag in tags)
    
    # Add name parts (kebab-case or camelCase)
    name_parts = re.split(r'[-_]|[A-Z]', name.lower())
    keywords.update(part for part in name_parts if len(part) > 2)
    
    # Extract significant words from description (3+ chars, not stop words)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can'}
    words = re.findall(r'\b[a-z]{3,}\b', description.lower())
    keywords.update(word for word in words if word not in stop_words)
    
    # Limit to top 10 keywords
    return sorted(list(keywords))[:10]

def truncate_description(description, max_words=50):
    """Truncate description to max_words for lightweight index"""
    words = description.split()
    if len(words) <= max_words:
        return description
    return ' '.join(words[:max_words]) + '...'

def build_lightweight_index(catalog):
    """Build lightweight index from full catalog"""
    skills_index = []
    
    for skill in catalog.get('skills', []):
        # Extract minimal metadata
        description = skill.get('description', '')
        
        # Get category from catalog field (should be set by catalog-builder.py from path structure)
        category = skill.get('category', 'Uncategorized')
        
        # If category is still missing or Uncategorized, try to infer from location path as fallback
        if not category or category == 'Uncategorized' or category == 'uncategorized':
            location = skill.get('location', '')
            # Extract category from path like Skills/Meta-skill/superpowers/
            path_parts = location.strip('/').split('/')
            if len(path_parts) >= 2:
                inferred_category = path_parts[1]  # Skills/Category/Skill -> Category
                if inferred_category and inferred_category != 'Skills':
                    category = inferred_category
            # Legacy fallback: check location string
            if category == 'Uncategorized' or category == 'uncategorized':
                location_lower = location.lower()
                if 'meta-skill' in location_lower:
                    category = 'Meta-skill'
                elif 'automation' in location_lower:
                    category = 'Automation'
                elif 'infrastructure-devops' in location_lower or 'infrastructure' in location_lower:
                    category = 'Infrastructure-DevOps'
                elif 'development' in location_lower:
                    category = 'Development'
                elif 'design-creative' in location_lower or 'design' in location_lower:
                    category = 'Design-Creative'
                elif 'communication' in location_lower:
                    category = 'Communication'
                elif 'document-generation' in location_lower or 'document' in location_lower:
                    category = 'Document-Generation'
                elif 'ai-agents' in location_lower or 'ai' in location_lower:
                    category = 'AI-Agents'
                elif 'security' in location_lower:
                    category = 'Security'
                elif 'scientific' in location_lower:
                    category = 'Scientific'
        
        # Build lightweight entry
        entry = {
            "name": skill.get('name', ''),
            "description": truncate_description(description, max_words=50),
            "tags": skill.get('tags', [])[:5],  # Max 5 tags
            "category": category,
            "keywords": extract_keywords(
                description,
                skill.get('tags', []),
                skill.get('name', '')
            )
        }
        
        skills_index.append(entry)
    
    # Sort by category, then name for consistent ordering
    skills_index.sort(key=lambda x: (x.get('category', 'Uncategorized'), x['name']))
    
    return {
        "version": "1.0.0",
        "updated": datetime.now().isoformat(),
        "total_skills": len(skills_index),
        "skills": skills_index
    }

def main():
    """Generate lightweight skills index"""
    print("Generating lightweight skills index...")
    
    # Load full catalog
    if not os.path.exists(CATALOG_FILE):
        print(f"Error: Catalog not found at {CATALOG_FILE}")
        print("Run: python3 Skills/skill-library-manager/scripts/catalog-builder.py")
        sys.exit(1)
    
    with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    # Build lightweight index
    index = build_lightweight_index(catalog)
    
    # Write index file
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    # Calculate size reduction
    catalog_size = os.path.getsize(CATALOG_FILE)
    index_size = os.path.getsize(INDEX_FILE)
    reduction = (1 - index_size / catalog_size) * 100 if catalog_size > 0 else 0
    
    print(f"✓ Lightweight index generated: {INDEX_FILE}")
    print(f"  Total skills: {index['total_skills']}")
    print(f"  Index size: {index_size:,} bytes ({index_size/1024:.1f} KB)")
    print(f"  Catalog size: {catalog_size:,} bytes ({catalog_size/1024:.1f} KB)")
    print(f"  Size reduction: {reduction:.1f}%")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
