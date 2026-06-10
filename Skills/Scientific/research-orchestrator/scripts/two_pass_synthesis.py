#!/usr/bin/env python3
"""
Two-pass synthesis: Draft → Verify → Revise

Improves synthesis quality by:
1. Generating initial synthesis
2. Generating verification questions
3. Checking claims against source summaries
4. Revising based on verification results
"""

import asyncio
import json
from pathlib import Path
from typing import Optional


VERIFICATION_PROMPT = """You are a research verification agent. Your task is to verify claims in a draft synthesis against source evidence.

## Draft Synthesis
{draft}

## Source Summaries
{summaries}

## Instructions

For each major claim in the draft:
1. Identify the specific claim
2. Find supporting evidence in source summaries
3. Assess accuracy: SUPPORTED / PARTIALLY_SUPPORTED / UNSUPPORTED / OVERSTATED
4. Note any nuances missed or misrepresented

Return JSON:
{{
  "verification_results": [
    {{
      "claim": "The draft claims X",
      "status": "SUPPORTED|PARTIALLY_SUPPORTED|UNSUPPORTED|OVERSTATED",
      "evidence": "Quote or reference from sources",
      "source_paper": "Which paper supports/contradicts",
      "issue": "Description of problem if any",
      "suggested_revision": "How to fix if needed"
    }}
  ],
  "overall_assessment": {{
    "accuracy_score": 1-10,
    "major_issues": ["list of significant problems"],
    "missing_nuances": ["important caveats not captured"],
    "unsupported_claims": ["claims without evidence"],
    "overgeneralizations": ["claims that go beyond evidence"]
  }},
  "revision_priority": ["ordered list of what to fix first"]
}}

Be rigorous. Flag any claim that extrapolates beyond what sources actually say.
"""


REVISION_PROMPT = """You are a research synthesis revision agent. Revise the draft based on verification feedback.

## Original Query
{query}

## Draft Synthesis
{draft}

## Verification Results
{verification}

## Source Summaries (for reference)
{summaries}

## Output Format
{output_format}

## Instructions

1. Address each issue in revision_priority order
2. For UNSUPPORTED claims: remove or add appropriate uncertainty
3. For OVERSTATED claims: add qualifiers and caveats
4. For PARTIALLY_SUPPORTED: add nuance from verification
5. Ensure all claims trace to specific sources
6. Add missing nuances identified by verifier
7. Maintain the requested output format

Produce the revised synthesis. Do not explain what you changed, just output the improved synthesis.
"""


async def generate_draft(
    query: str,
    summaries: list[dict],
    output_format: str,
    synthesis_prompt_path: Path
) -> str:
    """Generate initial synthesis draft."""
    prompt_template = synthesis_prompt_path.read_text()
    prompt = prompt_template.format(
        query=query,
        summaries=json.dumps(summaries, indent=2),
        output_format=output_format
    )
    
    proc = await asyncio.create_subprocess_exec(
        "claude", "-p", prompt,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode()


async def verify_draft(draft: str, summaries: list[dict]) -> dict:
    """Run verification pass on draft."""
    prompt = VERIFICATION_PROMPT.format(
        draft=draft,
        summaries=json.dumps(summaries, indent=2)
    )
    
    proc = await asyncio.create_subprocess_exec(
        "claude", "-p", prompt, "--output-format", "json",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    
    try:
        return json.loads(stdout.decode())
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse verification",
            "raw": stdout.decode(),
            "overall_assessment": {"accuracy_score": 5, "major_issues": ["Verification parsing failed"]}
        }


async def revise_draft(
    query: str,
    draft: str,
    verification: dict,
    summaries: list[dict],
    output_format: str
) -> str:
    """Revise draft based on verification results."""
    prompt = REVISION_PROMPT.format(
        query=query,
        draft=draft,
        verification=json.dumps(verification, indent=2),
        summaries=json.dumps(summaries, indent=2),
        output_format=output_format
    )
    
    proc = await asyncio.create_subprocess_exec(
        "claude", "-p", prompt,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode()


async def two_pass_synthesis(
    query: str,
    summaries: list[dict],
    output_format: str,
    synthesis_prompt_path: Path,
    skip_revision_threshold: int = 8
) -> dict:
    """
    Full two-pass synthesis pipeline.
    
    Args:
        query: Research question
        summaries: Paper summaries from reader agents
        output_format: prose/structured/both
        synthesis_prompt_path: Path to synthesis_agent.md
        skip_revision_threshold: Skip revision if accuracy >= this score
    
    Returns:
        {
            "final_synthesis": str,
            "draft": str,
            "verification": dict,
            "was_revised": bool,
            "accuracy_score": int
        }
    """
    # Pass 1: Draft
    print("      [Synthesis Pass 1/2] Generating draft...")
    draft = await generate_draft(query, summaries, output_format, synthesis_prompt_path)
    
    # Verification
    print("      [Synthesis Verify] Checking claims against sources...")
    verification = await verify_draft(draft, summaries)
    
    accuracy_score = verification.get("overall_assessment", {}).get("accuracy_score", 0)
    major_issues = verification.get("overall_assessment", {}).get("major_issues", [])
    
    # Decide if revision needed
    if accuracy_score >= skip_revision_threshold and not major_issues:
        print(f"      [Synthesis] Draft accuracy {accuracy_score}/10, no major issues. Skipping revision.")
        return {
            "final_synthesis": draft,
            "draft": draft,
            "verification": verification,
            "was_revised": False,
            "accuracy_score": accuracy_score
        }
    
    # Pass 2: Revise
    print(f"      [Synthesis Pass 2/2] Revising (accuracy {accuracy_score}/10, {len(major_issues)} issues)...")
    revised = await revise_draft(query, draft, verification, summaries, output_format)
    
    return {
        "final_synthesis": revised,
        "draft": draft,
        "verification": verification,
        "was_revised": True,
        "accuracy_score": accuracy_score
    }


def format_synthesis_report(synthesis_result: dict) -> str:
    """Format synthesis result with metadata."""
    output = synthesis_result["final_synthesis"]
    
    # Add verification metadata at end
    verification = synthesis_result.get("verification", {})
    assessment = verification.get("overall_assessment", {})
    
    metadata = f"""

---
**Synthesis Quality Metadata**
- Accuracy Score: {assessment.get('accuracy_score', 'N/A')}/10
- Was Revised: {'Yes' if synthesis_result.get('was_revised') else 'No'}
- Issues Addressed: {len(assessment.get('major_issues', []))}
"""
    
    if assessment.get("missing_nuances"):
        metadata += f"- Nuances Added: {len(assessment['missing_nuances'])}\n"
    
    if assessment.get("unsupported_claims"):
        metadata += f"- Unsupported Claims Removed: {len(assessment['unsupported_claims'])}\n"
    
    return output + metadata


async def main():
    """Test the two-pass synthesis."""
    test_summaries = [
        {
            "title": "ESG and Credit Risk",
            "findings": [{"claim": "ESG scores negatively correlate with default probability", "effect_size": "-0.15"}],
            "methodology": {"approach": "Panel regression"},
            "quality_assessment": {"credibility": "high"}
        },
        {
            "title": "Climate Risk in Banking",
            "findings": [{"claim": "Climate disclosure reduces credit spreads", "effect_size": "-12 bps"}],
            "methodology": {"approach": "DID"},
            "quality_assessment": {"credibility": "medium"}
        }
    ]
    
    # Mock test (would need actual prompt file)
    print("Two-pass synthesis module loaded successfully.")
    print("Use two_pass_synthesis() with actual prompt paths.")


if __name__ == "__main__":
    asyncio.run(main())
