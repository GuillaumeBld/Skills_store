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
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse

ALLOWED_SOURCE_DOMAINS = {
    'docs.docker.com',
    'kubernetes.io',
    'docs.n8n.io',
    'docs.langchain.com',
    'www.pinecone.io',
    'www.postgresql.org',
    'www.mongodb.com',
    'react.dev',
    'nextjs.org',
    'doc.traefik.io',
    'restfulapi.net',
    'www.onetonline.org',
    'github.com',
}

PROMPT_INJECTION_PATTERNS = [
    re.compile(r'ignore\s+(all|any|previous|prior)\s+(instructions?|prompts?)', re.IGNORECASE),
    re.compile(r'(override|bypass)\s+(the\s+)?(system|developer)\s+prompt', re.IGNORECASE),
    re.compile(r'jailbreak|dan\s+mode|do\s+anything\s+now|ignore\s+safety', re.IGNORECASE),
    re.compile(
        r'(you|assistant|model).{0,60}(reveal|exfiltrate|steal).{0,60}'
        r'(secret|token|credential|api[\s_-]?key|password)',
        re.IGNORECASE,
    ),
    re.compile(r'send.{0,40}(env|secret|token|credential).{0,40}https?://', re.IGNORECASE),
]


def is_allowed_source_url(url: str) -> bool:
    """Allow only HTTPS URLs from known documentation domains."""
    try:
        parsed = urlparse(url)
        if parsed.scheme != 'https' or not parsed.netloc:
            return False
        host = parsed.netloc.lower()
        return any(host == domain or host.endswith(f'.{domain}') for domain in ALLOWED_SOURCE_DOMAINS)
    except Exception:
        return False


def has_prompt_injection_signals(text: str) -> Tuple[bool, List[str]]:
    """Detect common prompt-injection markers in fetched content."""
    matches = []
    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(text):
            matches.append(pattern.pattern)
    return bool(matches), matches


def sanitize_preview(text: str, max_chars: int = 1000) -> str:
    """Strip noisy HTML/script content for previews."""
    no_script = re.sub(r'(?is)<script.*?>.*?</script>', ' ', text)
    no_style = re.sub(r'(?is)<style.*?>.*?</style>', ' ', no_script)
    no_tags = re.sub(r'(?is)<[^>]+>', ' ', no_style)
    collapsed = re.sub(r'\s+', ' ', no_tags).strip()
    return collapsed[:max_chars]


def identify_sources(skill_requirement: Dict) -> List[Dict]:
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

def fetch_web_content(url: str, timeout: int = 10) -> Tuple[Optional[str], Optional[str]]:
    """Fetch source content with domain allowlist and injection checks."""
    if not is_allowed_source_url(url):
        return None, "blocked: untrusted domain or non-https URL"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; SkillLibraryBot/1.0)'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            raw = response.text[:50000]  # Limit to first 50KB
            risky, patterns = has_prompt_injection_signals(raw)
            if risky:
                return None, f"blocked: potential prompt injection markers ({len(patterns)} pattern match(es))"
            return sanitize_preview(raw, max_chars=5000), None
        return None, f"http_{response.status_code}"
    except Exception as exc:
        return None, f"request_error: {exc}"

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
                if source.get('url'):
                    content, fetch_status = fetch_web_content(source['url'])
                    source['content_preview'] = content[:1000] if content else None
                    source['fetch_status'] = "ok" if content else fetch_status
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
