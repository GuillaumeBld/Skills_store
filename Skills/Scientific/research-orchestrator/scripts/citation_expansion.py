#!/usr/bin/env python3
"""
Citation expansion: Follow promising references from read papers.

Implements a two-wave search:
1. Initial search across sources
2. Expansion wave targeting specific cited papers
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Optional


def extract_citations_to_follow(reader_results: list[dict], max_expansions: int = 5) -> list[dict]:
    """
    Extract the most promising citations to follow from reader agent outputs.
    
    Prioritizes based on:
    - Explicit "references_to_follow" from reader
    - Frequency of citation across multiple papers (consensus importance)
    - Recency
    """
    citation_mentions = {}  # title -> {count, contexts, year_hints}
    
    for result in reader_results:
        summary = result.get("summary", {})
        if not summary:
            continue
        
        # Get explicit recommendations
        refs_to_follow = summary.get("references_to_follow", [])
        for ref in refs_to_follow:
            if isinstance(ref, str):
                ref_normalized = normalize_citation(ref)
                if ref_normalized:
                    if ref_normalized not in citation_mentions:
                        citation_mentions[ref_normalized] = {
                            "original": ref,
                            "count": 0,
                            "contexts": [],
                            "explicit_recommend": True
                        }
                    citation_mentions[ref_normalized]["count"] += 1
                    citation_mentions[ref_normalized]["contexts"].append(summary.get("title", "unknown"))
    
    # Score and rank citations
    scored_citations = []
    for normalized, data in citation_mentions.items():
        score = data["count"] * 2  # Frequency weight
        if data.get("explicit_recommend"):
            score += 3  # Bonus for explicit recommendation
        
        scored_citations.append({
            "query": data["original"],
            "normalized": normalized,
            "score": score,
            "mentioned_in": data["contexts"],
            "mention_count": data["count"]
        })
    
    scored_citations.sort(key=lambda x: x["score"], reverse=True)
    return scored_citations[:max_expansions]


def normalize_citation(citation: str) -> Optional[str]:
    """
    Normalize a citation string to a searchable query.
    Handles formats like:
    - "Smith et al. (2020)"
    - "Smith & Jones, 2020"
    - "The Effect of X on Y (Smith, 2020)"
    """
    if not citation or len(citation) < 5:
        return None
    
    # Remove common noise
    citation = re.sub(r'\s+', ' ', citation.strip())
    
    # Extract author-year pattern if present
    author_year = re.search(r'([A-Z][a-z]+(?:\s+(?:et\s+al\.?|&|and)\s+[A-Z][a-z]+)?)[,\s]+\(?(\d{4})\)?', citation)
    if author_year:
        return f"{author_year.group(1)} {author_year.group(2)}"
    
    # If it looks like a title, return cleaned version
    if len(citation) > 20:
        # Remove year in parentheses
        cleaned = re.sub(r'\s*\(\d{4}\)\s*', ' ', citation)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        if len(cleaned) > 15:
            return cleaned[:100]  # Cap length for search
    
    return citation[:100] if len(citation) > 10 else None


async def run_expansion_search(citation: dict, prompt_path: Path) -> dict:
    """
    Search for a specific cited paper.
    Uses targeted search to find the exact paper.
    """
    query = citation["query"]
    
    # Use a more targeted search prompt
    prompt = f"""You are a citation search agent. Find this specific paper:

"{query}"

Search Google Scholar and Semantic Scholar to find this exact paper or the closest match.

Return JSON:
{{
  "query": "{query}",
  "found": true/false,
  "paper": {{
    "title": "...",
    "authors": [...],
    "year": ...,
    "url": "...",
    "pdf_url": "..." or null,
    "abstract": "..."
  }},
  "confidence": "high/medium/low",
  "note": "any relevant notes"
}}

If multiple versions exist (preprint vs published), prefer the published version.
"""
    
    proc = await asyncio.create_subprocess_exec(
        "claude", "-p", prompt, "--output-format", "json",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    
    try:
        result = json.loads(stdout.decode())
        result["_expansion_source"] = citation.get("mentioned_in", [])
        return result
    except json.JSONDecodeError:
        return {
            "query": query,
            "found": False,
            "error": stdout.decode() or stderr.decode(),
            "_expansion_source": citation.get("mentioned_in", [])
        }


async def expand_citations(
    reader_results: list[dict],
    existing_papers: list[dict],
    max_expansions: int = 5,
    prompt_path: Optional[Path] = None
) -> tuple[list[dict], dict]:
    """
    Main citation expansion pipeline.
    
    Args:
        reader_results: Output from reader agents
        existing_papers: Papers already in the pipeline (to avoid duplicates)
        max_expansions: Maximum new papers to add
        prompt_path: Path to prompts directory
    
    Returns:
        (new_papers, expansion_stats)
    """
    # Extract promising citations
    citations_to_follow = extract_citations_to_follow(reader_results, max_expansions * 2)
    
    if not citations_to_follow:
        return [], {"citations_extracted": 0, "searched": 0, "found": 0}
    
    # Filter out citations that match existing papers
    existing_titles = {normalize_citation(p.get("title", "")) for p in existing_papers}
    filtered_citations = [
        c for c in citations_to_follow
        if c["normalized"] not in existing_titles
    ][:max_expansions]
    
    if not filtered_citations:
        return [], {"citations_extracted": len(citations_to_follow), "searched": 0, "found": 0, "filtered_as_duplicates": len(citations_to_follow)}
    
    # Search for each citation in parallel
    search_tasks = [
        run_expansion_search(citation, prompt_path)
        for citation in filtered_citations
    ]
    
    search_results = await asyncio.gather(*search_tasks)
    
    # Collect found papers
    new_papers = []
    for result in search_results:
        if result.get("found") and result.get("paper"):
            paper = result["paper"]
            paper["_from_expansion"] = True
            paper["_cited_by"] = result.get("_expansion_source", [])
            new_papers.append(paper)
    
    stats = {
        "citations_extracted": len(citations_to_follow),
        "searched": len(filtered_citations),
        "found": len(new_papers),
        "expansion_queries": [c["query"] for c in filtered_citations]
    }
    
    return new_papers, stats


def merge_expansion_results(
    original_papers: list[dict],
    expansion_papers: list[dict],
    max_total: int = 15
) -> list[dict]:
    """
    Merge original and expansion papers, respecting total limit.
    
    Strategy:
    - Keep all original papers (up to 70% of limit)
    - Fill remaining slots with expansion papers
    - Expansion papers marked with _from_expansion flag
    """
    original_limit = int(max_total * 0.7)
    expansion_limit = max_total - min(len(original_papers), original_limit)
    
    merged = original_papers[:original_limit]
    merged.extend(expansion_papers[:expansion_limit])
    
    return merged


if __name__ == "__main__":
    # Test citation normalization
    test_citations = [
        "Smith et al. (2020)",
        "Smith & Jones, 2020",
        "The Effect of ESG on Credit Risk (Johnson, 2021)",
        "Fama and French (1993)",
    ]
    
    for c in test_citations:
        print(f"'{c}' -> '{normalize_citation(c)}'")
