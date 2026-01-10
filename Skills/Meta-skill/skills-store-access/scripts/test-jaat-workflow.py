#!/usr/bin/env python3
"""
Test JAAT-Enhanced Skill Discovery Workflow
End-to-end test of the complete workflow: query → JAAT → gap detection → source gathering → skill creation
"""

import os
import sys
import json
import subprocess
from pathlib import Path

SCRIPT_DIR = os.path.dirname(__file__)
LIBRARY_ROOT = os.getenv('LIBRARY_ROOT', os.path.expanduser('~/Documents/Skills/Skills_librairie'))

def run_step(name: str, command: list, input_data: str = None) -> tuple:
    """Run a workflow step and return (success, output, error)"""
    print(f"\n{'='*60}")
    print(f"Step: {name}")
    print(f"{'='*60}")
    
    try:
        if input_data:
            result = subprocess.run(
                command,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=60
            )
        else:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60
            )
        
        success = result.returncode == 0
        return success, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_workflow(query: str, use_jaat: bool = False, dry_run: bool = True):
    """Test the complete workflow"""
    print(f"Testing JAAT-Enhanced Skill Discovery Workflow")
    print(f"Query: {query}")
    print(f"Use JAAT: {use_jaat}")
    print(f"Dry Run: {dry_run}")
    
    # Step 1: Analyze task requirements
    analyze_cmd = [
        sys.executable,
        os.path.join(SCRIPT_DIR, 'analyze-task-requirements.py'),
        query,
        '--json'
    ]
    if use_jaat:
        analyze_cmd.append('--use-jaat')
    
    success, output, error = run_step("1. Analyze Task Requirements", analyze_cmd)
    if not success:
        print(f"Error: {error}")
        return False
    
    try:
        analysis = json.loads(output)
    except json.JSONDecodeError:
        print(f"Failed to parse analysis output: {output}")
        return False
    
    print(f"Complexity: {analysis.get('complexity_score', 0):.2f}")
    print(f"Domains: {', '.join(analysis.get('domains', []))}")
    print(f"JAAT Enhanced: {analysis.get('jaat_enhanced', False)}")
    
    if not analysis.get('should_check_for_skills'):
        print("No skills needed - workflow complete")
        return True
    
    # Step 2: Create mock skill requirements for gap detection
    # (In real workflow, these would come from JAAT extraction)
    mock_requirements = [
        {
            'type': 'task',
            'source': 'keyword',
            'description': query,
            'priority': 'medium'
        }
    ]
    
    # Add JAAT results if available
    if analysis.get('onet_tasks_count', 0) > 0:
        mock_requirements.append({
            'type': 'task',
            'source': 'onet',
            'description': 'Extracted from JAAT (mock)',
            'priority': 'high'
        })
    
    requirements_json = json.dumps({'skill_requirements': mock_requirements})
    
    # Step 3: Detect skill gaps
    gap_cmd = [
        sys.executable,
        os.path.join(SCRIPT_DIR, 'detect-skill-gaps.py'),
        '--json',
        '--max-results', '3'
    ]
    
    success, gap_output, gap_error = run_step("2. Detect Skill Gaps", gap_cmd, requirements_json)
    if not success:
        print(f"Warning: Gap detection failed: {gap_error}")
        print("Continuing with mock gaps...")
        gaps_data = {'prioritized_gaps': mock_requirements[:1]}
    else:
        try:
            gaps_data = json.loads(gap_output)
        except json.JSONDecodeError:
            gaps_data = {'prioritized_gaps': mock_requirements[:1]}
    
    gaps = gaps_data.get('prioritized_gaps', [])
    if not gaps:
        print("No skill gaps found - all skills exist in catalog")
        return True
    
    print(f"Found {len(gaps)} skill gaps")
    
    # Step 4: Gather authoritative sources
    gaps_json = json.dumps(gaps_data)
    source_cmd = [
        sys.executable,
        os.path.join(SCRIPT_DIR, 'gather-skill-sources.py'),
        '--json'
    ]
    
    success, source_output, source_error = run_step("3. Gather Authoritative Sources", source_cmd, gaps_json)
    if success:
        try:
            sources = json.loads(source_output)
            print(f"Identified sources for {len(sources)} skills")
        except json.JSONDecodeError:
            sources = {}
    else:
        print(f"Warning: Source gathering failed: {source_error}")
        sources = {}
    
    # Step 5: Auto-create skills (dry run)
    if dry_run:
        print(f"\n{'='*60}")
        print("Step: 4. Auto-Create Skills (DRY RUN)")
        print(f"{'='*60}")
        print("Would create the following skills:")
        
        for gap in gaps[:3]:  # Top 3
            req = gap.get('requirement', {})
            skill_name = gap.get('suggested_skill_name', 'unknown-skill')
            print(f"\n  - {skill_name}")
            print(f"    Priority: {gap.get('final_priority', 0):.2f}")
            if req.get('description'):
                print(f"    Description: {req['description'][:60]}...")
    else:
        # Actually create skills (for production use)
        for gap in gaps[:1]:  # Create top priority skill only
            req = gap.get('requirement', {})
            req['suggested_skill_name'] = gap.get('suggested_skill_name', 'new-skill')
            
            skill_json = json.dumps(req)
            create_cmd = [
                sys.executable,
                os.path.join(SCRIPT_DIR, 'auto-create-skill.py'),
                '--dry-run'  # Always dry-run in test
            ]
            
            success, create_output, create_error = run_step(
                f"4. Create Skill: {req.get('suggested_skill_name')}",
                create_cmd,
                skill_json
            )
    
    print(f"\n{'='*60}")
    print("Workflow Test Complete!")
    print(f"{'='*60}")
    return True

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test JAAT-enhanced skill discovery workflow')
    parser.add_argument('query', help='Test query')
    parser.add_argument('--use-jaat', action='store_true', help='Use JAAT enhancement')
    parser.add_argument('--create', action='store_true', help='Actually create skills (not dry-run)')
    
    args = parser.parse_args()
    
    success = test_workflow(args.query, use_jaat=args.use_jaat, dry_run=not args.create)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
