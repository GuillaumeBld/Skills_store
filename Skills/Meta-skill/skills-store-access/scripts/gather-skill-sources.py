#!/usr/bin/env python3
"""
Gather Authoritative Sources for Skill Creation
Identifies and fetches documentation from authoritative sources to populate skill content.
"""

import os
import sys
import json
import re
import requests
from typing import List, Dict, Optional
from urllib.parse import urlparse

def identify_sources(skill_requirement: Dict) -> List[str]:
    """
    Identify authoritative sources for a skill requirement.
    
    Args:
        skill_requirement: Dict with skill requirement details
    
    Returns:
        List of source URLs/documents
    """
    sources = []
    skill_name = skill_requirement.get('suggested_skill_name', '')
    description = skill_requirement.get('description', '') or skill_requirement.get('label', '')
    
    # Map common technologies to their official docs
    tech_mapping = {
        'docker': 'https://docs.docker.com/',
        'kubernetes': 'https://kubernetes.io/docs/',
        'n8n': 'https://docs.n8n.io/',
        'rag': 'https://docs.langchain.com/docs/use_cases/question_answering/',
        'vector': 'https://www.pinecone.io/learn/vector-database/',
        'postgres': 'https://www.postgresql.org/docs/',
        'mongodb': 'https://www.mongodb.com/docs/',
        'react': 'https://react.dev/',
        'next': 'https://nextjs.org/docs',
        'traefik': 'https://doc.traefik.io/traefik/',
        'api': 'https://restfulapi.net/'
    }
    
    # Check description for technologies
    desc_lower = description.lower()
    for tech, url in tech_mapping.items():
        if tech in desc_lower or tech in skill_name.lower():
            sources.append({
                'type': 'official_docs',
                'url': url,
                'technology': tech,
                'priority': 'high'
            })
    
    # O*NET task sources
    if skill_requirement.get('source') == 'onet' and skill_requirement.get('id'):
        onet_id = skill_requirement.get('id')
        sources.append({
            'type': 'onet',
            'url': f'https://www.onetonline.org/link/summary/{onet_id}',
            'onet_id': onet_id,
            'priority': 'high'
        })
    
    # EuropaCode sources
    if skill_requirement.get('source') == 'europacode' and skill_requirement.get('code'):
        code = skill_requirement.get('code')
        sources.append({
            'type': 'europacode',
            'code': code,
            'priority': 'high',
            'note': 'EuropaCode taxonomy reference'
        })
    
    # GitHub search for related repositories
    if skill_name:
        sources.append({
            'type': 'github_search',
            'url': f'https://github.com/search?q={skill_name.replace("-", "+")}&type=repositories',
            'priority': 'medium'
        })
    
    return sources

def fetch_web_content(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch content from a URL (simplified - in production, use proper HTML parsing)"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; SkillLibraryBot/1.0)'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            return response.text[:50000]  # Limit to first 50KB
        return None
    except Exception:
        return None

def gather_sources(requirements: List[Dict], fetch_content: bool = False) -> Dict:
    """
    Gather authoritative sources for skill requirements.
    
    Args:
        requirements: List of skill requirement dicts
        fetch_content: Whether to fetch actual content (default: False, just identify)
    
    Returns:
        Dict mapping requirement to sources
    """
    results = {}
    
    for req in requirements:
        skill_name = req.get('suggested_skill_name', 'skill')
        sources = identify_sources(req)
        
        if fetch_content:
            # Fetch content for each source
            enriched_sources = []
            for source in sources:
                if source.get('type') == 'official_docs' and source.get('url'):
                    content = fetch_web_content(source['url'])
                    source['content_preview'] = content[:1000] if content else None
                enriched_sources.append(source)
            results[skill_name] = enriched_sources
        else:
            results[skill_name] = sources
    
    return results

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Gather authoritative sources for skill creation'
    )
    
    parser.add_argument('requirements_file', nargs='?',
                        help='JSON file with skill requirements (stdin if not provided)')
    parser.add_argument('--fetch', action='store_true',
                        help='Fetch actual content from sources (slow)')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    
    args = parser.parse_args()
    
    # Load requirements
    if args.requirements_file:
        with open(args.requirements_file, 'r') as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    
    # Extract requirements
    if isinstance(data, dict) and 'prioritized_gaps' in data:
        requirements = [g['requirement'] for g in data['prioritized_gaps']]
    elif isinstance(data, list):
        requirements = data
    else:
        requirements = [data]
    
    # Add suggested names if missing
    for req in requirements:
        if 'suggested_skill_name' not in req:
            req['suggested_skill_name'] = req.get('name', 'skill').lower().replace(' ', '-')
    
    # Gather sources
    sources = gather_sources(requirements, fetch_content=args.fetch)
    
    if args.json:
        print(json.dumps(sources, indent=2))
    else:
        print(f"Identified sources for {len(sources)} skills:\n")
        for skill_name, skill_sources in sources.items():
            print(f"{skill_name}:")
            for source in skill_sources:
                source_type = source.get('type', 'unknown')
                priority = source.get('priority', 'medium')
                url = source.get('url', 'N/A')
                print(f"  - [{priority}] {source_type}: {url}")
            print()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
