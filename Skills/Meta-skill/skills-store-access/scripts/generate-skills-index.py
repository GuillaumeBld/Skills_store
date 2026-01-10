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

LIBRARY_ROOT = os.getenv('LIBRARY_ROOT', os.path.expanduser('~/Skills_librairie'))
if not LIBRARY_ROOT:
    # Try common locations
    for path in ['/Users/guillaumebld/Documents/Skills/Skills_librairie', 
                 os.path.expanduser('~/Documents/Skills/Skills_librairie'),
                 os.path.expanduser('~/Skills_librairie')]:
        if os.path.exists(path):
            LIBRARY_ROOT = path
            break

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
        
        # Determine category from location or catalog field
        category = skill.get('category', 'uncategorized')
        if not category or category == 'uncategorized':
            # Try to infer from location path
            location = skill.get('location', '')
            if 'Meta-skill' in location:
                category = 'Meta-skill'
            elif 'Automation' in location:
                category = 'Automation'
            elif 'Infrastructure-DevOps' in location:
                category = 'Infrastructure-DevOps'
            elif 'Development' in location:
                category = 'Development'
            elif 'Design-Creative' in location:
                category = 'Design-Creative'
            elif 'Communication' in location:
                category = 'Communication'
            elif 'Document-Generation' in location:
                category = 'Document-Generation'
            elif 'AI-Agents' in location:
                category = 'AI-Agents'
        
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
    
    # Sort by name for consistent ordering
    skills_index.sort(key=lambda x: x['name'])
    
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
