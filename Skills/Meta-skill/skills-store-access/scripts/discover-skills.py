#!/usr/bin/env python3
"""
Discover Relevant Skills for a Task
Searches lightweight skills index to find skills relevant to a task without loading full catalog.
Returns top matches with relevance scores.
"""

import os
import json
import sys
from pathlib import Path

REPO_NAMES = ('Skills_librairie', 'Skills_store')
FALLBACK_ROOTS = [
    os.path.expanduser('~/Skills_librairie'),
    os.path.expanduser('~/Skills_store'),
    os.path.expanduser('~/Documents/Skills/Skills_librairie'),
    os.path.expanduser('~/Documents/Skills/Skills_store'),
]


def is_library_root(path: str) -> bool:
    if not path or not os.path.isdir(path):
        return False
    return os.path.isdir(os.path.join(path, 'Skills')) or os.path.isdir(os.path.join(path, 'skills'))


def detect_library_root(start_dir: str) -> str:
    env_root = os.getenv('LIBRARY_ROOT')
    if env_root:
        env_root = os.path.abspath(os.path.expanduser(env_root))
        if is_library_root(env_root):
            return env_root

    current = os.path.abspath(start_dir)
    while current != os.path.dirname(current):
        if is_library_root(current) or os.path.basename(current) in REPO_NAMES:
            return current
        current = os.path.dirname(current)

    for candidate in FALLBACK_ROOTS:
        candidate = os.path.abspath(candidate)
        if is_library_root(candidate):
            return candidate

    return os.path.abspath(os.path.expanduser('~/Skills_librairie'))


LIBRARY_ROOT = detect_library_root(os.path.dirname(os.path.abspath(__file__)))
INDEX_FILE = os.path.join(LIBRARY_ROOT, 'skills-index.json')

def load_index():
    """Load lightweight skills index"""
    if not os.path.exists(INDEX_FILE):
        print(f"Error: Skills index not found at {INDEX_FILE}")
        print("Run: python3 Skills/Meta-skill/skills-store-access/scripts/generate-skills-index.py")
        sys.exit(1)
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_relevance(skill, query, query_lower):
    """Calculate relevance score for a skill"""
    score = 0.0
    query_words = set(query_lower.split())
    
    # Name match (highest weight)
    name_lower = skill['name'].lower()
    if query_lower in name_lower:
        score += 0.4
    elif any(word in name_lower for word in query_words if len(word) > 3):
        score += 0.2
    
    # Description match (high weight)
    desc_lower = skill['description'].lower()
    if query_lower in desc_lower:
        score += 0.3
    matching_words = sum(1 for word in query_words if word in desc_lower and len(word) > 3)
    if matching_words > 0:
        score += (matching_words / len(query_words)) * 0.2
    
    # Tag match (medium weight)
    tags_lower = [tag.lower() for tag in skill.get('tags', [])]
    if any(tag in query_lower for tag in tags_lower):
        score += 0.2
    matching_tags = sum(1 for tag in tags_lower if tag in query_words)
    if matching_tags > 0:
        score += (matching_tags / len(tags_lower)) * 0.1 if tags_lower else 0
    
    # Keyword match (lower weight)
    keywords_lower = [kw.lower() for kw in skill.get('keywords', [])]
    matching_keywords = sum(1 for kw in keywords_lower if kw in query_words or kw in query_lower)
    if matching_keywords > 0:
        score += (matching_keywords / len(keywords_lower)) * 0.1 if keywords_lower else 0
    
    return min(score, 1.0)  # Cap at 1.0

def discover_skills(query, min_relevance=0.3, max_results=5):
    """Discover skills relevant to query"""
    index = load_index()
    query_lower = query.lower()
    
    # Score all skills
    scored_skills = []
    for skill in index.get('skills', []):
        relevance = calculate_relevance(skill, query, query_lower)
        if relevance >= min_relevance:
            scored_skills.append({
                **skill,
                'relevance': relevance
            })
    
    # Sort by relevance (descending)
    scored_skills.sort(key=lambda x: x['relevance'], reverse=True)
    
    # Return top results
    return scored_skills[:max_results]

def format_results(results):
    """Format discovery results for output"""
    if not results:
        return "No relevant skills found."
    
    output = []
    output.append(f"Found {len(results)} relevant skill(s):\n")
    
    for i, skill in enumerate(results, 1):
        output.append(f"{i}. {skill['name']} (relevance: {skill['relevance']:.2f})")
        output.append(f"   Description: {skill['description']}")
        if skill.get('tags'):
            output.append(f"   Tags: {', '.join(skill['tags'][:5])}")
        output.append(f"   Category: {skill.get('category', 'uncategorized')}")
        output.append("")
    
    return "\n".join(output)

def main():
    """Main discovery function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Discover skills relevant to a task',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 discover-skills.py "docker deployment traefik"
  python3 discover-skills.py "RAG pipeline vector search" --min-relevance 0.5
  python3 discover-skills.py "database backup" --max-results 3
        """
    )
    
    parser.add_argument('query', nargs='?', help='Task description or keywords')
    parser.add_argument('--min-relevance', type=float, default=0.3,
                        help='Minimum relevance score (0.0-1.0, default: 0.3)')
    parser.add_argument('--max-results', type=int, default=5,
                        help='Maximum number of results (default: 5)')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    
    args = parser.parse_args()
    
    if not args.query:
        parser.print_help()
        sys.exit(1)
    
    # Discover relevant skills
    results = discover_skills(args.query, args.min_relevance, args.max_results)
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_results(results))
    
    return 0 if results else 1

if __name__ == '__main__':
    sys.exit(main())
