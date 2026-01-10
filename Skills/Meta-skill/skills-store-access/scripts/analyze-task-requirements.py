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

# Try to import JAAT enhancement (optional)
JAAT_AVAILABLE = False
JAAT_FUNCTIONS = {}

try:
    # Import JAAT module by file path (handles hyphens in filename)
    import importlib.util
    jaat_module_path = os.path.join(os.path.dirname(__file__), 'jaat-enhanced-discovery.py')
    if os.path.exists(jaat_module_path):
        spec = importlib.util.spec_from_file_location("jaat_enhanced_discovery", jaat_module_path)
        jaat_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(jaat_module)
        JAAT_FUNCTIONS = {
            'extract_standardized_skills': jaat_module.extract_standardized_skills,
            'combine_with_keyword_analysis': jaat_module.combine_with_keyword_analysis,
            'normalize_for_catalog': jaat_module.normalize_for_catalog
        }
        JAAT_AVAILABLE = True
except Exception:
    # JAAT might not be installed or have issues - mark as unavailable
    JAAT_AVAILABLE = False

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

def extract_with_jaat(query):
    """Extract standardized skills using JAAT (optional enhancement)"""
    if not JAAT_AVAILABLE or 'extract_standardized_skills' not in JAAT_FUNCTIONS:
        return None
    
    try:
        # Use JAAT to extract standardized skills
        extract_func = JAAT_FUNCTIONS['extract_standardized_skills']
        jaat_result = extract_func(query, task_threshold=0.85, skill_threshold=0.87)
        if jaat_result.get('success'):
            return jaat_result
        else:
            return None
    except Exception as e:
        # Silently fail - JAAT is optional
        return None

def discover_relevant_skills_for_task(query, jaat_enhanced=False):
    """Discover relevant skills using discover-skills script"""
    script_path = os.path.join(
        os.path.dirname(__file__),
        'discover-skills.py'
    )
    
    search_queries = [query]  # Default to original query
    
    # If JAAT is available and enabled, try to enhance search queries
    if jaat_enhanced and JAAT_AVAILABLE and 'normalize_for_catalog' in JAAT_FUNCTIONS:
        jaat_result = extract_with_jaat(query)
        if jaat_result:
            try:
                normalize_func = JAAT_FUNCTIONS['normalize_for_catalog']
                enhanced_queries = normalize_func(jaat_result)
                if enhanced_queries:
                    # Combine original query with JAAT-extracted queries
                    search_queries = [query] + enhanced_queries[:3]  # Top 3 additional queries
            except Exception:
                pass  # Fall back to original query
    
    # Search using all queries and combine results
    all_discovered = []
    seen_skills = set()
    
    for search_query in search_queries:
        try:
            result = subprocess.run(
                [sys.executable, script_path, search_query, '--json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                discovered = json.loads(result.stdout)
                for skill in discovered:
                    if skill.get('name') not in seen_skills:
                        seen_skills.add(skill['name'])
                        all_discovered.append(skill)
        except Exception:
            continue
    
    # Sort by relevance (if available)
    all_discovered.sort(key=lambda x: x.get('relevance', 0), reverse=True)
    return all_discovered[:10]  # Return top 10

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
    parser.add_argument('--use-jaat', action='store_true',
                        help='Use JAAT for enhanced skill extraction (if available)')
    
    args = parser.parse_args()
    
    # Analyze task
    complexity = analyze_query_complexity(args.query)
    domains = identify_domains(args.query)
    should_check, check_reason = should_check_for_skills(complexity, domains, args.ongoing)
    
    # Try JAAT extraction if enabled and complexity suggests it
    jaat_result = None
    enhanced_analysis = None
    if args.use_jaat and complexity > 0.4 and JAAT_AVAILABLE and 'combine_with_keyword_analysis' in JAAT_FUNCTIONS:
        jaat_result = extract_with_jaat(args.query)
        if jaat_result and jaat_result.get('success'):
            try:
                combine_func = JAAT_FUNCTIONS['combine_with_keyword_analysis']
                enhanced_analysis = combine_func(jaat_result, domains, complexity)
                # Update domains with JAAT-enhanced domains
                if enhanced_analysis:
                    domains = enhanced_analysis.get('domains', domains)
            except Exception:
                pass  # Fall back to keyword analysis
    
    result = {
        'query': args.query,
        'complexity_score': complexity,
        'domains': domains,
        'should_check_for_skills': should_check,
        'check_reason': check_reason,
        'should_discover': False,
        'recommended_skills': [],
        'proactive_installation': [],
        'jaat_enhanced': jaat_result is not None and jaat_result.get('success', False),
        'onet_tasks_count': 0,
        'europacode_skills_count': 0
    }
    
    # Add JAAT results if available
    if jaat_result and jaat_result.get('success'):
        result['onet_tasks_count'] = len(jaat_result.get('tasks', []))
        result['europacode_skills_count'] = len(jaat_result.get('skills', []))
    
    # Discover skills if recommended
    if should_check and not args.no_discovery:
        result['should_discover'] = True
        discovered = discover_relevant_skills_for_task(args.query, jaat_enhanced=args.use_jaat)
        
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
        
        if result.get('jaat_enhanced'):
            print(f"\nJAAT Enhancement: Enabled")
            print(f"  - O*NET Tasks extracted: {result.get('onet_tasks_count', 0)}")
            print(f"  - EuropaCode Skills extracted: {result.get('europacode_skills_count', 0)}")
        
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
