#!/usr/bin/env python3
"""
Research Orchestrator - Main entry point for parallel literature research.

Quality-optimized version with:
- Semantic deduplication (embedding-based)
- Citation expansion (follow promising references)
- Two-pass synthesis (draft → verify → revise)

Usage:
    python orchestrate.py "research question" [options]

Example:
    python orchestrate.py "optimal portfolio rebalancing strategies" --depth deep --format structured --expand-citations
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Import quality modules
from semantic_dedupe import dedupe_and_rank, semantic_dedupe
from citation_expansion import expand_citations, extract_citations_to_follow, merge_expansion_results
from two_pass_synthesis import two_pass_synthesis, format_synthesis_report

# Token estimation constants (approximate)
TOKENS_PER_PAGE = 800
AVG_PAPER_PAGES_QUICK = 3
AVG_PAPER_PAGES_DEEP = 25
COST_PER_1K_INPUT = 0.003
COST_PER_1K_OUTPUT = 0.015


def estimate_tokens(num_papers: int, depth: str, with_expansion: bool = False, with_two_pass: bool = False) -> dict:
    """Estimate token usage and cost for the research task."""
    pages = AVG_PAPER_PAGES_QUICK if depth == "quick" else AVG_PAPER_PAGES_DEEP
    input_tokens = num_papers * pages * TOKENS_PER_PAGE
    output_tokens = num_papers * 500 + 2000
    
    # Expansion adds ~30% more reading
    if with_expansion:
        expansion_papers = max(3, num_papers // 3)
        input_tokens += expansion_papers * pages * TOKENS_PER_PAGE
        output_tokens += expansion_papers * 500
    
    # Two-pass synthesis doubles synthesis cost
    if with_two_pass:
        output_tokens += 3000  # Verification + revision
    
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "estimated_cost_usd": round(
            (input_tokens / 1000 * COST_PER_1K_INPUT) + 
            (output_tokens / 1000 * COST_PER_1K_OUTPUT), 2
        )
    }


def determine_sources(query: str) -> list[str]:
    """Determine which sources to search based on query domain."""
    query_lower = query.lower()
    sources = ["google_scholar", "semantic_scholar"]
    
    if any(term in query_lower for term in ["finance", "banking", "credit", "esg", "investment", "portfolio", "risk"]):
        sources.extend(["ssrn", "nber", "fed", "bis"])
    if any(term in query_lower for term in ["economics", "labor", "employment", "wage", "market"]):
        sources.extend(["ssrn", "nber"])
    if any(term in query_lower for term in ["machine learning", "ai", "neural", "algorithm", "computer"]):
        sources.extend(["arxiv", "acm"])
    if any(term in query_lower for term in ["medical", "health", "clinical", "disease", "treatment"]):
        sources.extend(["pubmed", "cochrane"])
    if any(term in query_lower for term in ["physics", "math", "quantum", "statistical"]):
        sources.append("arxiv")
    
    seen = set()
    return [s for s in sources if not (s in seen or seen.add(s))]


async def run_search_agent(source: str, query: str, prompt_path: Path) -> dict:
    """Spawn a search agent for a specific source."""
    prompt = prompt_path.read_text().format(source=source, query=query)
    
    proc = await asyncio.create_subprocess_exec(
        "claude", "-p", prompt, "--output-format", "json",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    
    try:
        result = json.loads(stdout.decode())
        return {"source": source, "papers": result.get("papers", []), "error": None}
    except json.JSONDecodeError:
        return {"source": source, "papers": [], "error": stdout.decode() or stderr.decode()}


async def run_reader_agent(paper: dict, depth: str, prompt_path: Path) -> dict:
    """Spawn a reader agent for a specific paper."""
    prompt = prompt_path.read_text().format(
        paper_url=paper.get("url", ""),
        paper_title=paper.get("title", "Unknown"),
        depth=depth
    )
    
    proc = await asyncio.create_subprocess_exec(
        "claude", "-p", prompt, "--output-format", "json",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    
    try:
        result = json.loads(stdout.decode())
        return {"paper": paper.get("title"), "summary": result, "error": None}
    except json.JSONDecodeError:
        return {"paper": paper.get("title"), "summary": None, "error": stdout.decode() or stderr.decode()}


async def main():
    parser = argparse.ArgumentParser(description="Orchestrate parallel literature research (quality-optimized)")
    parser.add_argument("query", help="Research question or topic")
    parser.add_argument("--depth", choices=["quick", "deep"], default="quick",
                        help="Reading depth: quick (abstract+intro) or deep (full paper)")
    parser.add_argument("--format", choices=["prose", "structured", "both"], default="both",
                        help="Output format for synthesis")
    parser.add_argument("--max-papers", type=int, default=None,
                        help="Maximum papers to read (default: agent-determined)")
    parser.add_argument("--confirm", action="store_true",
                        help="Skip cost confirmation prompt")
    
    # Quality options
    parser.add_argument("--expand-citations", action="store_true", default=True,
                        help="Follow promising citations from initial papers (default: on)")
    parser.add_argument("--no-expand-citations", action="store_false", dest="expand_citations",
                        help="Disable citation expansion")
    parser.add_argument("--max-expansions", type=int, default=5,
                        help="Maximum papers to add via citation expansion")
    parser.add_argument("--two-pass", action="store_true", default=True,
                        help="Use two-pass synthesis with verification (default: on)")
    parser.add_argument("--no-two-pass", action="store_false", dest="two_pass",
                        help="Disable two-pass synthesis")
    parser.add_argument("--similarity-threshold", type=float, default=0.85,
                        help="Semantic similarity threshold for deduplication (0.0-1.0)")
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent.parent
    prompts_dir = script_dir / "references" / "prompts"
    
    print(f"\n{'='*70}")
    print(f"RESEARCH ORCHESTRATOR (Quality-Optimized)")
    print(f"{'='*70}")
    print(f"Query: {args.query}")
    print(f"Depth: {args.depth}")
    print(f"Format: {args.format}")
    print(f"Citation Expansion: {'ON' if args.expand_citations else 'OFF'}")
    print(f"Two-Pass Synthesis: {'ON' if args.two_pass else 'OFF'}")
    print(f"Semantic Dedup Threshold: {args.similarity_threshold}")
    print(f"{'='*70}\n")
    
    # Step 1: Determine sources
    sources = determine_sources(args.query)
    print(f"[1/7] Sources selected: {', '.join(sources)}")
    
    # Step 2: Parallel search
    print(f"[2/7] Spawning {len(sources)} search agents in parallel...")
    search_tasks = [
        run_search_agent(source, args.query, prompts_dir / "search_agent.md")
        for source in sources
    ]
    search_results = await asyncio.gather(*search_tasks)
    
    total_found = sum(len(r.get("papers", [])) for r in search_results)
    print(f"      Found {total_found} papers across all sources")
    
    # Step 3: Semantic deduplication
    print(f"[3/7] Semantic deduplication (threshold={args.similarity_threshold})...")
    max_papers = args.max_papers or min(10, max(5, total_found // 3))
    papers, dedupe_stats = dedupe_and_rank(search_results, max_papers)
    print(f"      Method: {dedupe_stats['method']}")
    print(f"      {dedupe_stats['initial_count']} → {dedupe_stats['after_dedupe']} papers ({dedupe_stats['duplicates_removed']} duplicates removed)")
    print(f"      Selected top {len(papers)} for reading")
    
    # Step 4: Cost estimation and confirmation
    estimate = estimate_tokens(
        len(papers), args.depth, 
        with_expansion=args.expand_citations,
        with_two_pass=args.two_pass
    )
    print(f"\n[4/7] Cost Estimation")
    print(f"      Token estimate: ~{estimate['total_tokens']:,} tokens")
    print(f"      Estimated cost: ~${estimate['estimated_cost_usd']}")
    
    if not args.confirm:
        response = input("\n      Proceed? [y/N]: ").strip().lower()
        if response != 'y':
            print("      Aborted by user.")
            sys.exit(0)
    
    # Step 5: Parallel reading (wave 1)
    print(f"\n[5/7] Reading papers (wave 1: {len(papers)} papers)...")
    read_tasks = [
        run_reader_agent(paper, args.depth, prompts_dir / "reader_agent.md")
        for paper in papers
    ]
    read_results = await asyncio.gather(*read_tasks)
    
    successful_reads = [r for r in read_results if r.get("summary")]
    print(f"      Successfully read {len(successful_reads)}/{len(papers)} papers")
    
    # Step 6: Citation expansion (wave 2)
    expansion_stats = {"enabled": False}
    if args.expand_citations and successful_reads:
        print(f"\n[6/7] Citation expansion (max {args.max_expansions} papers)...")
        
        expansion_papers, expansion_stats = await expand_citations(
            successful_reads,
            papers,
            max_expansions=args.max_expansions,
            prompt_path=prompts_dir
        )
        expansion_stats["enabled"] = True
        
        print(f"      Citations extracted: {expansion_stats.get('citations_extracted', 0)}")
        print(f"      Searched: {expansion_stats.get('searched', 0)}")
        print(f"      New papers found: {expansion_stats.get('found', 0)}")
        
        if expansion_papers:
            # Read expansion papers
            print(f"      Reading {len(expansion_papers)} expansion papers...")
            expansion_read_tasks = [
                run_reader_agent(paper, args.depth, prompts_dir / "reader_agent.md")
                for paper in expansion_papers
            ]
            expansion_read_results = await asyncio.gather(*expansion_read_tasks)
            
            expansion_successful = [r for r in expansion_read_results if r.get("summary")]
            print(f"      Successfully read {len(expansion_successful)}/{len(expansion_papers)} expansion papers")
            
            # Merge results
            successful_reads.extend(expansion_successful)
            papers = merge_expansion_results(papers, expansion_papers)
    else:
        print(f"\n[6/7] Citation expansion: SKIPPED")
    
    # Step 7: Synthesis
    print(f"\n[7/7] Synthesizing findings...")
    summaries = [r["summary"] for r in successful_reads if r.get("summary")]
    
    if args.two_pass:
        print(f"      Using two-pass synthesis (draft → verify → revise)...")
        synthesis_result = await two_pass_synthesis(
            query=args.query,
            summaries=summaries,
            output_format=args.format,
            synthesis_prompt_path=prompts_dir / "synthesis_agent.md"
        )
        final_output = format_synthesis_report(synthesis_result)
        synthesis_metadata = {
            "method": "two-pass",
            "was_revised": synthesis_result.get("was_revised"),
            "accuracy_score": synthesis_result.get("accuracy_score"),
            "verification": synthesis_result.get("verification", {}).get("overall_assessment", {})
        }
    else:
        # Single-pass (original behavior)
        synthesis_prompt = (prompts_dir / "synthesis_agent.md").read_text().format(
            query=args.query,
            summaries=json.dumps(summaries, indent=2),
            output_format=args.format
        )
        proc = await asyncio.create_subprocess_exec(
            "claude", "-p", synthesis_prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        final_output = stdout.decode()
        synthesis_metadata = {"method": "single-pass"}
    
    # Output
    print(f"\n{'='*70}")
    print("SYNTHESIS RESULTS")
    print(f"{'='*70}\n")
    print(final_output)
    
    # Save results
    output_dir = Path("/home/claude/research_outputs")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"research_{timestamp}.json"
    
    with open(output_file, "w") as f:
        json.dump({
            "query": args.query,
            "depth": args.depth,
            "format": args.format,
            "sources": sources,
            "quality_settings": {
                "semantic_dedupe_threshold": args.similarity_threshold,
                "citation_expansion": args.expand_citations,
                "two_pass_synthesis": args.two_pass
            },
            "stats": {
                "papers_found": total_found,
                "dedupe": dedupe_stats,
                "expansion": expansion_stats,
                "papers_read": len(successful_reads),
                "synthesis": synthesis_metadata
            },
            "token_estimate": estimate,
            "papers": [{"title": p.get("title"), "url": p.get("url"), "from_expansion": p.get("_from_expansion", False)} for p in papers],
            "summaries": summaries,
            "synthesis": final_output
        }, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())
