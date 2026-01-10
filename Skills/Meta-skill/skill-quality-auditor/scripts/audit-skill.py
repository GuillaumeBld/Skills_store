#!/usr/bin/env python3
"""
Skill Quality Auditor
Analyzes a single skill and generates quality score with recommendations
"""

import os
import re
import sys
import yaml
from pathlib import Path
from datetime import datetime

class SkillAuditor:
    def __init__(self, skill_path):
        self.skill_path = Path(skill_path)
        self.skill_md = self.skill_path / "SKILL.md"
        self.scores = {}
        self.issues = []
        
    def audit(self):
        """Run complete audit and return score"""
        if not self.skill_md.exists():
            return {"score": 0, "error": "SKILL.md not found"}
        
        with open(self.skill_md, 'r', encoding='utf-8') as f:
            self.content = f.read()
        
        # Extract frontmatter
        self.frontmatter = self.extract_frontmatter()
        
        # Run all checks
        self.check_structure()
        self.check_completeness()
        self.check_executability()
        self.check_readability()
        self.check_links()
        
        # Calculate total score
        total = sum(self.scores.values())
        
        return {
            "score": total,
            "breakdown": self.scores,
            "issues": self.issues,
            "grade": self.get_grade(total)
        }
    
    def extract_frontmatter(self):
        """Extract YAML frontmatter"""
        match = re.match(r'^---\n(.*?)\n---', self.content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except:
                return {}
        return {}
    
    def check_structure(self):
        """Check file structure (25 points)"""
        score = 0
        
        # Has SKILL.md (5 pts)
        if self.skill_md.exists():
            score += 5
        else:
            self.issues.append({
                "priority": "high",
                "category": "structure",
                "message": "Missing SKILL.md",
                "fix": "Create SKILL.md file"
            })
        
        # Valid YAML frontmatter (5 pts)
        if self.frontmatter:
            score += 5
        else:
            self.issues.append({
                "priority": "high",
                "category": "structure",
                "message": "Invalid or missing YAML frontmatter",
                "fix": "Add frontmatter between --- delimiters"
            })
        
        # Standard section order (5 pts)
        sections = self.get_sections()
        expected_order = ["Prerequisites", "Quick Start"]
        if all(s in sections for s in expected_order):
            if sections.index("Prerequisites") < sections.index("Quick Start"):
                score += 5
            else:
                self.issues.append({
                    "priority": "low",
                    "category": "structure",
                    "message": "Section order: Prerequisites should come before Quick Start"
                })
        
        # Proper heading hierarchy (5 pts)
        if self.check_heading_hierarchy():
            score += 5
        else:
            self.issues.append({
                "priority": "medium",
                "category": "structure",
                "message": "Improper heading hierarchy (H1 → H2 → H3)",
                "fix": "Ensure headings don't skip levels"
            })
        
        # Has CHANGELOG.md (5 pts)
        if (self.skill_path / "CHANGELOG.md").exists():
            score += 5
        else:
            self.issues.append({
                "priority": "medium",
                "category": "structure",
                "message": "Missing CHANGELOG.md",
                "fix": "Create CHANGELOG.md to track version history"
            })
        
        self.scores['structure'] = score
    
    def check_completeness(self):
        """Check for required sections (25 points)"""
        score = 0
        sections = self.get_sections()
        
        required = {
            "Prerequisites": 5,
            "Quick Start": 5,
            "Validation": 5,
            "Troubleshooting": 5,
            "Reference Files": 5
        }
        
        for section, points in required.items():
            # Also accept variations
            variations = {
                "Validation": ["Validation", "Verification", "Health Checks"],
                "Quick Start": ["Quick Start", "Getting Started", "Usage"],
                "Troubleshooting": ["Troubleshooting", "Common Issues", "FAQ"]
            }
            
            matches = variations.get(section, [section])
            if any(m in sections for m in matches):
                score += points
            else:
                self.issues.append({
                    "priority": "high",
                    "category": "completeness",
                    "message": f"Missing {section} section",
                    "fix": f"Add ## {section} section"
                })
        
        self.scores['completeness'] = score
    
    def check_executability(self):
        """Check commands are executable (20 points)"""
        score = 0
        
        # Find code blocks
        code_blocks = re.findall(r'```(?:bash|sh)?\n(.*?)\n```', self.content, re.DOTALL)
        
        if not code_blocks:
            self.issues.append({
                "priority": "medium",
                "category": "executability",
                "message": "No code blocks found",
                "fix": "Add executable examples"
            })
            self.scores['executability'] = 0
            return
        
        # Check for pseudo-code
        pseudo_patterns = [
            r'^Install ',
            r'^Configure ',
            r'^Set up ',
            r'^Run ',
            r'^Execute '
        ]
        
        has_pseudo = False
        for block in code_blocks:
            for pattern in pseudo_patterns:
                if re.search(pattern, block, re.MULTILINE | re.IGNORECASE):
                    has_pseudo = True
                    break
        
        if not has_pseudo:
            score += 10
        else:
            self.issues.append({
                "priority": "high",
                "category": "executability",
                "message": "Pseudo-code detected (imperative instructions without commands)",
                "fix": "Replace 'Install X' with actual command: 'sudo apt install X'"
            })
        
        # Check for expected outputs
        has_expected = bool(re.search(r'(?:Expected|Output):', self.content, re.IGNORECASE))
        if has_expected:
            score += 5
        else:
            self.issues.append({
                "priority": "medium",
                "category": "executability",
                "message": "No expected outputs shown",
                "fix": "Add '# Expected: ...' comments after commands"
            })
        
        # Check for comments in code blocks
        commented_blocks = sum(1 for b in code_blocks if '#' in b)
        if commented_blocks >= len(code_blocks) * 0.5:
            score += 5
        
        self.scores['executability'] = score
    
    def check_readability(self):
        """Check readability metrics (20 points)"""
        score = 0
        
        # Remove code blocks for text analysis
        text = re.sub(r'```.*?```', '', self.content, flags=re.DOTALL)
        
        # Average sentence length
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_words < 25:
                score += 5
            else:
                self.issues.append({
                    "priority": "medium",
                    "category": "readability",
                    "message": f"Average sentence length: {avg_words:.1f} words (target: <25)",
                    "fix": "Split long sentences"
                })
        
        # Time estimates
        has_time_estimates = bool(re.search(r'\d+\s*(min|minutes|hour|hours)', self.content))
        if has_time_estimates:
            score += 5
        else:
            self.issues.append({
                "priority": "medium",
                "category": "readability",
                "message": "No time estimates provided",
                "fix": "Add estimates: ### 1. Step Name (5 min)"
            })
        
        # Step numbering
        has_numbered_steps = bool(re.search(r'###\s*\d+\.', self.content))
        if has_numbered_steps:
            score += 5
        
        # Code blocks with language tags
        total_blocks = len(re.findall(r'```', self.content)) // 2
        tagged_blocks = len(re.findall(r'```(?:bash|python|yaml|json|javascript)', self.content))
        
        if total_blocks > 0 and tagged_blocks >= total_blocks * 0.8:
            score += 5
        else:
            self.issues.append({
                "priority": "low",
                "category": "readability",
                "message": "Some code blocks missing language tags",
                "fix": "Use ```bash instead of just ```"
            })
        
        self.scores['readability'] = score
    
    def check_links(self):
        """Check for broken links (10 points)"""
        score = 0
        
        # Internal links
        internal_links = re.findall(r'\[.*?\]\(((?:\.\.|/)[^\)]+)\)', self.content)
        broken_internal = []
        
        for link in internal_links:
            # Resolve relative to skill directory
            target = (self.skill_path / link).resolve()
            if not target.exists():
                broken_internal.append(link)
        
        if not broken_internal:
            score += 5
        else:
            for link in broken_internal:
                self.issues.append({
                    "priority": "high",
                    "category": "links",
                    "message": f"Broken internal link: {link}",
                    "fix": "Create file or remove reference"
                })
        
        # External links (simplified check - just presence)
        external_links = re.findall(r'\[.*?\]\((https?://[^\)]+)\)', self.content)
        if external_links:
            score += 5  # Assume valid for now (full check would need HTTP requests)
        
        self.scores['links'] = score
    
    def get_sections(self):
        """Extract section headings"""
        return re.findall(r'^##\s+(.+)$', self.content, re.MULTILINE)
    
    def check_heading_hierarchy(self):
        """Check H1 → H2 → H3 hierarchy"""
        headings = re.findall(r'^(#{1,6})\s', self.content, re.MULTILINE)
        if not headings:
            return True
        
        levels = [len(h) for h in headings]
        for i in range(1, len(levels)):
            if levels[i] > levels[i-1] + 1:
                return False
        return True
    
    def get_grade(self, score):
        """Convert score to grade"""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Fair"
        else:
            return "Poor"

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Audit skill quality')
    parser.add_argument('skill_path', help='Path to skill directory')
    parser.add_argument('--detailed', action='store_true', help='Generate detailed report')
    parser.add_argument('--min-score', type=int, default=0, help='Minimum required score')
    
    args = parser.parse_args()
    
    auditor = SkillAuditor(args.skill_path)
    result = auditor.audit()
    
    # Print results
    print(f"\n{'='*60}")
    print(f"Quality Audit: {Path(args.skill_path).name}")
    print(f"{'='*60}\n")
    
    print(f"Overall Score: {result['score']}/100 ({result['grade']})\n")
    
    # Breakdown
    for category, score in result['breakdown'].items():
        max_scores = {
            'structure': 25,
            'completeness': 25,
            'executability': 20,
            'readability': 20,
            'links': 10
        }
        max_score = max_scores.get(category, 25)
        status = "✓" if score == max_score else "⚠" if score >= max_score * 0.7 else "✗"
        print(f"{status} {category.capitalize()}: {score}/{max_score}")
    
    # Issues
    if result['issues']:
        print(f"\n{'='*60}")
        print("Issues Found")
        print(f"{'='*60}\n")
        
        by_priority = {'high': [], 'medium': [], 'low': []}
        for issue in result['issues']:
            by_priority[issue['priority']].append(issue)
        
        for priority in ['high', 'medium', 'low']:
            if by_priority[priority]:
                print(f"\n{priority.upper()} Priority ({len(by_priority[priority])}):")
                for i, issue in enumerate(by_priority[priority], 1):
                    print(f"{i}. {issue['message']}")
                    if 'fix' in issue:
                        print(f"   Fix: {issue['fix']}")
    
    # Exit code
    if result['score'] < args.min_score:
        print(f"\n✗ Score {result['score']} below minimum {args.min_score}")
        sys.exit(1)
    else:
        print(f"\n✓ Quality check passed")
        sys.exit(0)

if __name__ == '__main__':
    main()
