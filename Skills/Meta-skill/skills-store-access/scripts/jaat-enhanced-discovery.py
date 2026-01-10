#!/usr/bin/env python3
"""
JAAT-Enhanced Skill Discovery
Extracts standardized tasks and skills from text using JAAT (Job Ad Analysis Toolkit).
Maps O*NET tasks and EuropaCode skills to skill requirements for catalog matching.
"""

import os
import sys
import json
import re
from typing import Dict, List, Tuple, Optional

try:
    from JAAT import JAAT
except ImportError:
    print("Error: JAAT library not installed. Run: pip install JAAT", file=sys.stderr)
    sys.exit(1)

# Cache for JAAT instances (expensive to initialize)
_task_match = None
_skill_match = None

def get_task_matcher(threshold: float = 0.85):
    """Get or create TaskMatch instance (cached)"""
    global _task_match
    if _task_match is None:
        _task_match = JAAT.TaskMatch(threshold=threshold)
    return _task_match

def get_skill_matcher(threshold: float = 0.87):
    """Get or create SkillMatch instance (cached)"""
    global _skill_match
    if _skill_match is None:
        _skill_match = JAAT.SkillMatch(threshold=threshold)
    return _skill_match

def extract_standardized_skills(text: str, task_threshold: float = 0.85, 
                                skill_threshold: float = 0.87) -> Dict:
    """
    Extract O*NET tasks and EuropaCode skills from text using JAAT.
    
    Args:
        text: Input text (query, job posting, project description, etc.)
        task_threshold: Threshold for TaskMatch (0-1, lower = more matches)
        skill_threshold: Threshold for SkillMatch (0-1, lower = more matches)
    
    Returns:
        Dictionary with:
        - 'tasks': List of (task_id, task_description) tuples from O*NET
        - 'skills': List of (skill_label, europa_code) tuples
        - 'success': Boolean indicating if extraction succeeded
    """
    result = {
        'tasks': [],
        'skills': [],
        'success': False,
        'error': None
    }
    
    try:
        # Extract O*NET tasks
        task_matcher = get_task_matcher(threshold=task_threshold)
        tasks = task_matcher.get_tasks(text)
        # Convert to simple list of tuples (avoid pickling issues)
        result['tasks'] = [(str(tid), str(desc)) for tid, desc in (tasks or [])]
        
        # Extract EuropaCode skills  
        skill_matcher = get_skill_matcher(threshold=skill_threshold)
        skills = skill_matcher.get_skills(text)
        # Convert to simple list of tuples (avoid pickling issues)
        result['skills'] = [(str(label), str(code)) for label, code in (skills or [])]
        
        result['success'] = True
        
    except Exception as e:
        result['error'] = str(e)
        result['success'] = False
        # Even on error, return empty lists
        result['tasks'] = []
        result['skills'] = []
    
    return result

def normalize_for_catalog(jaat_output: Dict) -> List[str]:
    """
    Convert O*NET/EuropaCode outputs to searchable skill requirements.
    Creates search queries that can be used with discover-skills.py.
    
    Args:
        jaat_output: Output from extract_standardized_skills()
    
    Returns:
        List of search query strings for catalog lookup
    """
    queries = []
    
    # Extract keywords from task descriptions
    for task_id, task_desc in jaat_output.get('tasks', []):
        # Extract important words from task description
        words = re.findall(r'\b[a-zA-Z]{4,}\b', task_desc.lower())
        # Filter common stop words
        stop_words = {'with', 'from', 'this', 'that', 'these', 'those', 'using', 
                     'according', 'identify', 'prepare', 'assign', 'analyze'}
        keywords = [w for w in words if w not in stop_words][:5]
        if keywords:
            queries.append(' '.join(keywords))
    
    # Extract skill labels (they're already descriptive)
    for skill_label, europa_code in jaat_output.get('skills', []):
        queries.append(skill_label.lower())
    
    # Deduplicate while preserving order
    seen = set()
    unique_queries = []
    for q in queries:
        if q not in seen and len(q) > 3:
            seen.add(q)
            unique_queries.append(q)
    
    return unique_queries[:10]  # Limit to top 10 queries

def map_to_skill_domains(jaat_output: Dict) -> List[str]:
    """
    Map JAAT outputs to skill domain categories.
    Uses O*NET task descriptions and skill labels to infer domains.
    
    Args:
        jaat_output: Output from extract_standardized_skills()
    
    Returns:
        List of domain names that match Skills Library categories
    """
    domains = set()
    
    # Domain mapping keywords
    domain_keywords = {
        'devops': ['deploy', 'infrastructure', 'server', 'docker', 'kubernetes', 
                  'system', 'architecture', 'setup', 'configuration'],
        'database': ['database', 'query', 'data', 'sql', 'storage', 'backup'],
        'automation': ['automation', 'workflow', 'pipeline', 'orchestration', 
                      'process', 'routine'],
        'document': ['document', 'presentation', 'report', 'template', 'format'],
        'ai/rag': ['design', 'concept', 'system', 'requirements', 'analysis',
                  'retrieval', 'embedding', 'vector'],
        'web': ['web', 'api', 'frontend', 'backend', 'interface', 'application'],
        'design': ['design', 'graphic', 'visual', 'ui', 'ux', 'interface'],
        'testing': ['test', 'validation', 'quality', 'debug', 'verify']
    }
    
    # Check task descriptions
    text_to_check = ' '.join([desc for _, desc in jaat_output.get('tasks', [])]).lower()
    text_to_check += ' ' + ' '.join([label for label, _ in jaat_output.get('skills', [])]).lower()
    
    for domain, keywords in domain_keywords.items():
        if any(keyword in text_to_check for keyword in keywords):
            domains.add(domain)
    
    return list(domains)

def combine_with_keyword_analysis(jaat_output: Dict, keyword_domains: List[str], 
                                  complexity: float) -> Dict:
    """
    Combine JAAT extraction results with keyword-based analysis.
    
    Args:
        jaat_output: Output from extract_standardized_skills()
        keyword_domains: Domains identified by keyword matching
        complexity: Complexity score from keyword analysis
    
    Returns:
        Enhanced analysis combining both approaches
    """
    jaat_domains = map_to_skill_domains(jaat_output)
    all_domains = list(set(keyword_domains + jaat_domains))
    
    # Generate search queries from JAAT results
    search_queries = normalize_for_catalog(jaat_output)
    
    # Create skill requirements from JAAT outputs
    skill_requirements = []
    
    for task_id, task_desc in jaat_output.get('tasks', []):
        skill_requirements.append({
            'type': 'task',
            'source': 'onet',
            'id': task_id,
            'description': task_desc,
            'priority': 'medium'
        })
    
    for skill_label, europa_code in jaat_output.get('skills', []):
        skill_requirements.append({
            'type': 'skill',
            'source': 'europacode',
            'code': europa_code,
            'label': skill_label,
            'priority': 'high'  # Skills are more specific than tasks
        })
    
    return {
        'domains': all_domains,
        'search_queries': search_queries,
        'skill_requirements': skill_requirements,
        'onet_tasks_count': len(jaat_output.get('tasks', [])),
        'europacode_skills_count': len(jaat_output.get('skills', [])),
        'jaat_success': jaat_output.get('success', False)
    }

def main():
    """CLI interface for testing JAAT extraction"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extract standardized skills using JAAT',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('text', help='Text to analyze (job posting, query, etc.)')
    parser.add_argument('--task-threshold', type=float, default=0.85,
                        help='TaskMatch threshold (0-1, default: 0.85)')
    parser.add_argument('--skill-threshold', type=float, default=0.87,
                        help='SkillMatch threshold (0-1, default: 0.87)')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    
    args = parser.parse_args()
    
    # Extract skills
    result = extract_standardized_skills(
        args.text, 
        task_threshold=args.task_threshold,
        skill_threshold=args.skill_threshold
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"JAAT Extraction Results:\n")
        print(f"Success: {result['success']}")
        if result.get('error'):
            print(f"Error: {result['error']}")
        
        print(f"\nO*NET Tasks ({len(result['tasks'])}):")
        for task_id, task_desc in result['tasks'][:5]:
            print(f"  - [{task_id}] {task_desc}")
        if len(result['tasks']) > 5:
            print(f"  ... and {len(result['tasks']) - 5} more")
        
        print(f"\nEuropaCode Skills ({len(result['skills'])}):")
        for skill_label, code in result['skills'][:5]:
            print(f"  - [{code}] {skill_label}")
        if len(result['skills']) > 5:
            print(f"  ... and {len(result['skills']) - 5} more")
        
        # Show normalized queries
        queries = normalize_for_catalog(result)
        if queries:
            print(f"\nGenerated Search Queries ({len(queries)}):")
            for query in queries[:5]:
                print(f"  - {query}")
        
        # Show domains
        domains = map_to_skill_domains(result)
        if domains:
            print(f"\nInferred Domains: {', '.join(domains)}")
    
    return 0 if result['success'] else 1

if __name__ == '__main__':
    sys.exit(main())
