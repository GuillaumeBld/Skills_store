#!/usr/bin/env python3
"""
Analyze Task Requirements for Skill Needs
Determines if a task would benefit from specialized skills and recommends discovery/installation.
"""

import os
import json
import sys
import re
import subprocess
from pathlib import Path

# Domain keywords that suggest specialized skills
DOMAIN_KEYWORDS = {
    'devops': ['docker', 'kubernetes', 'k8s', 'deploy', 'ci/cd', 'infrastructure', 'vps', 'server', 'traefik', 'nginx'],
    'database': ['postgres', 'mysql', 'mongodb', 'sql', 'query', 'backup', 'migration', 'schema'],
    'automation': ['n8n', 'workflow', 'automation', 'pipeline', 'orchestration'],
    'document': ['pdf', 'docx', 'pptx', 'xlsx', 'document', 'template', 'format'],
    'ai/rag': ['rag', 'vector', 'embedding', 'retrieval', 'semantic', 'search', 'llm', 'prompt'],
    'web': ['react', 'next.js', 'frontend', 'backend', 'api', 'rest', 'graphql'],
    'design': ['canvas', 'design', 'ui', 'ux', 'theme', 'brand', 'graphic'],
    'testing': ['test', 'testing', 'qa', 'quality', 'validation', 'unit test', 'integration']
}

COMPLEXITY_INDICATORS = [
    'deploy', 'build', 'create', 'setup', 'configure', 'implement',
    'workflow', 'pipeline', 'system', 'stack', 'architecture',
    'multiple', 'several', 'various', 'complex', 'advanced'
]

def analyze_query_complexity(query):
    """Analyze query complexity score (0-1)"""
    query_lower = query.lower()
    score = 0.0
    
    # Check for complexity indicators
    complexity_count = sum(1 for indicator in COMPLEXITY_INDICATORS if indicator in query_lower)
    score += min(complexity_count * 0.15, 0.5)
    
    # Check for domain keywords (indicates specialized knowledge)
    domain_matches = 0
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(keyword in query_lower for keyword in keywords):
            domain_matches += 1
    score += min(domain_matches * 0.2, 0.4)
    
    # Check query length (longer queries often more complex)
    word_count = len(query.split())
    if word_count > 10:
        score += 0.1
    elif word_count > 5:
        score += 0.05
    
    return min(score, 1.0)

def identify_domains(query):
    """Identify relevant domains from query"""
    query_lower = query.lower()
    domains = []
    
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(keyword in query_lower for keyword in keywords):
            domains.append(domain)
    
    return domains

def should_check_for_skills(complexity, domains, is_ongoing=False):
    """Determine if should check Skills store"""
    # Always check if task is part of ongoing project
    if is_ongoing:
        return True, "Task is part of ongoing project"
    
    # Check if complexity suggests specialized skills
    if complexity > 0.4:
        return True, f"Task complexity score {complexity:.2f} suggests specialized skills"
    
    # Check if domain keywords suggest specialized skills
    if len(domains) >= 2:
        return True, f"Multiple domains detected: {', '.join(domains)}"
    
    if len(domains) == 1 and complexity > 0.2:
        return True, f"Domain-specific task: {domains[0]}"
    
    return False, "Simple task, no specialized skills needed"

def should_install_proactively(complexity, relevance_score, is_ongoing=False):
    """Determine if should install skill proactively"""
    # Install if part of ongoing project and relevant
    if is_ongoing and relevance_score > 0.6:
        return True, "Ongoing project + high relevance"
    
    # Install if very high relevance regardless of context
    if relevance_score > 0.85:
        return True, "Very high relevance score"
    
    # Install if high complexity and good relevance
    if complexity > 0.5 and relevance_score > 0.7:
        return True, "High complexity + good relevance"
    
    return False, "Not needed proactively"

def discover_relevant_skills_for_task(query):
    """Discover relevant skills using discover-skills script"""
    script_path = os.path.join(
        os.path.dirname(__file__),
        'discover-skills.py'
    )
    
    try:
        result = subprocess.run(
            [sys.executable, script_path, query, '--json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return []
    except Exception as e:
        print(f"Warning: Could not discover skills: {e}", file=sys.stderr)
        return []

def main():
    """Main analysis function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze task requirements and recommend skill discovery/installation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 analyze-task-requirements.py "I need to deploy a Docker stack"
  python3 analyze-task-requirements.py "Create a RAG pipeline" --ongoing
  python3 analyze-task-requirements.py "What's the weather?" --no-discovery
        """
    )
    
    parser.add_argument('query', help='Task description or user query')
    parser.add_argument('--ongoing', action='store_true',
                        help='Task is part of ongoing project')
    parser.add_argument('--no-discovery', action='store_true',
                        help='Skip actual skill discovery (analysis only)')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    
    args = parser.parse_args()
    
    # Analyze task
    complexity = analyze_query_complexity(args.query)
    domains = identify_domains(args.query)
    should_check, check_reason = should_check_for_skills(complexity, domains, args.ongoing)
    
    result = {
        'query': args.query,
        'complexity_score': complexity,
        'domains': domains,
        'should_check_for_skills': should_check,
        'check_reason': check_reason,
        'should_discover': False,
        'recommended_skills': [],
        'proactive_installation': []
    }
    
    # Discover skills if recommended
    if should_check and not args.no_discovery:
        result['should_discover'] = True
        discovered = discover_relevant_skills_for_task(args.query)
        
        if discovered:
            result['recommended_skills'] = discovered
            
            # Evaluate proactive installation for top match
            if discovered:
                top_skill = discovered[0]
                should_install, install_reason = should_install_proactively(
                    complexity,
                    top_skill.get('relevance', 0),
                    args.ongoing
                )
                if should_install:
                    result['proactive_installation'] = [{
                        'skill': top_skill['name'],
                        'reason': install_reason,
                        'relevance': top_skill.get('relevance', 0)
                    }]
    
    # Output results
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Task Analysis: {args.query}\n")
        print(f"Complexity Score: {complexity:.2f}")
        print(f"Domains: {', '.join(domains) if domains else 'None'}")
        print(f"\nSkill Discovery: {'YES' if should_check else 'NO'}")
        print(f"Reason: {check_reason}")
        
        if result['recommended_skills']:
            print(f"\nRecommended Skills ({len(result['recommended_skills'])}):")
            for skill in result['recommended_skills']:
                print(f"  - {skill['name']} (relevance: {skill.get('relevance', 0):.2f})")
        
        if result['proactive_installation']:
            print(f"\nProactive Installation Recommended:")
            for item in result['proactive_installation']:
                print(f"  - {item['skill']}: {item['reason']} (relevance: {item['relevance']:.2f})")
    
    return 0 if should_check else 1

if __name__ == '__main__':
    sys.exit(main())
