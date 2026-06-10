---
name: research-orchestrator
description: Orchestrate parallel literature research to answer "what is the optimal way to do X" questions. Use when the user needs evidence-based recommendations backed by academic research. Triggers include requests for optimal approaches, best practices supported by research, literature reviews, or systematic evidence gathering on any topic. Spawns parallel sub-agents to search multiple academic sources, read papers at configurable depth, and synthesize findings into actionable recommendations with confidence assessments.
---

# Research Orchestrator

Parallel sub-agent orchestration for evidence-based research synthesis.

## When to Use

- User asks "what is the optimal way to do X"
- User needs evidence-based recommendations
- User requests literature review or research synthesis
- User wants to know what research says about a topic
- Any question where academic evidence would inform the answer

## Architecture

```
Orchestrator
    │
    ├─► Search Agents (parallel) ─► [candidate papers]
    │   ├─ Google Scholar
    │   ├─ SSRN
    │   ├─ arXiv
    │   └─ Domain-specific (NBER, Fed, PubMed...)
    │
    ├─► Dedupe & Rank ─► [top N papers]
    │
    ├─► Reader Agents (parallel) ─► [structured summaries]
    │
    └─► Synthesis Agent ─► [recommendation + confidence]
```

## Quick Start

```bash
python scripts/orchestrate.py "research question" --depth quick --format structured
```

### Arguments
- `query`: Research question (required)
- `--depth`: `quick` (abstract+intro) or `deep` (full paper). Default: quick
- `--format`: `prose`, `structured`, or `both`. Default: both
- `--max-papers`: Override agent-determined paper count
- `--confirm`: Skip cost confirmation prompt

### Quality Options (all enabled by default)
- `--expand-citations` / `--no-expand-citations`: Follow promising references from initial papers
- `--max-expansions N`: Maximum papers to add via citation expansion (default: 5)
- `--two-pass` / `--no-two-pass`: Use draft→verify→revise synthesis
- `--similarity-threshold 0.85`: Semantic deduplication threshold (0.0-1.0)

## Quality Optimizations

### 1. Semantic Deduplication

**Problem**: Same paper appears across multiple sources with slightly different titles/metadata.

**Solution**: Embed title+abstract using sentence-transformers, cluster by cosine similarity, keep best from each cluster.

```
"ESG and Credit Risk: A Study" ─┐
"ESG and Credit Risk - A Study" ─┼─► Keep highest-cited version
"ESG & Credit Risk: An Analysis" ┘
```

**Implementation**: `scripts/semantic_dedupe.py`
- Primary: sentence-transformers (all-MiniLM-L6-v2)
- Fallback: TF-IDF if transformers unavailable
- Final fallback: Normalized title matching

**Threshold tuning**:
| Threshold | Behavior |
|-----------|----------|
| 0.95 | Very strict, only near-duplicates |
| 0.85 | Default, catches reformulations |
| 0.70 | Aggressive, may merge related-but-different papers |

### 2. Citation Expansion

**Problem**: Initial search may miss seminal papers that aren't keyword-optimized.

**Solution**: Extract "references to follow" from reader outputs, search for those specific papers, add to reading queue.

```
Wave 1: Search → Read 10 papers → Extract citations
Wave 2: Search for top 5 cited papers → Read → Merge into synthesis
```

**Implementation**: `scripts/citation_expansion.py`
- Extracts citations from `references_to_follow` field in reader output
- Normalizes citation strings ("Smith et al. 2020" → searchable query)
- Deduplicates against already-read papers
- Parallel search for specific papers
- Merges: 70% original, 30% expansion (configurable)

**When it helps most**:
- Niche topics where seminal papers use different terminology
- Cross-disciplinary questions
- Topics with foundational papers everyone cites

### 3. Two-Pass Synthesis

**Problem**: Single-pass synthesis may overstate claims, miss nuances, or hallucinate consensus.

**Solution**: Draft → Verify → Revise

```
Pass 1: Generate synthesis draft
Verify: Check each claim against source summaries
        - SUPPORTED / PARTIALLY_SUPPORTED / UNSUPPORTED / OVERSTATED
Pass 2: Revise based on verification (skip if accuracy ≥ 8/10)
```

**Implementation**: `scripts/two_pass_synthesis.py`
- Verification agent checks every major claim
- Flags: unsupported claims, overgeneralizations, missing nuances
- Revision agent addresses issues in priority order
- Adds quality metadata to output

**Output includes**:
```
---
**Synthesis Quality Metadata**
- Accuracy Score: 8/10
- Was Revised: Yes
- Issues Addressed: 2
```

## Workflow

### 1. Source Selection
Orchestrator determines sources based on query domain:

| Domain Keywords | Sources Added |
|-----------------|---------------|
| finance, banking, credit, ESG | SSRN, NBER, Fed, BIS |
| economics, labor, wage | SSRN, NBER |
| ML, AI, algorithm | arXiv, ACM |
| medical, health, clinical | PubMed, Cochrane |

Base sources (always included): Google Scholar, Semantic Scholar

See `references/sources.md` for full source registry.

### 2. Parallel Search
Each search agent:
- Queries assigned source
- Extracts: title, authors, year, URL, abstract, citations
- Returns max 15 papers per source

### 3. Dedupe & Rank
- Remove duplicates (title matching)
- Score by: citations × 0.3 + recency × 2 × source_weight
- Select top N (default: agent-determined, typically 5-10)

### 4. Cost Estimation
Before reading, display:
- Estimated tokens (based on depth and paper count)
- Estimated cost
- Prompt user to confirm or adjust

### 5. Parallel Reading
Each reader agent extracts:
- Research question, hypothesis
- Data: source, sample, variables
- Methodology: approach, identification strategy
- Findings: claims, effect sizes, significance
- Limitations, quality assessment

See `references/prompts/reader_agent.md` for full extraction schema.

### 6. Synthesis
Synthesis agent:
- Maps evidence landscape
- Identifies consensus and conflicts
- Weighs evidence by quality
- Produces recommendation with confidence level

See `references/prompts/synthesis_agent.md` for synthesis framework.

## Output Formats

### Prose
Natural language synthesis. Good for reports and sharing.

### Structured
Tabular analysis with sections:
- Summary, Evidence Table, Options, Recommendation
- Confidence Assessment, Risks, Knowledge Gaps

See `references/output_formats.md` for full specs.

## Cost Management

Token estimation formula:
- Quick depth: ~2,400 tokens/paper (3 pages × 800 tokens)
- Deep depth: ~20,000 tokens/paper (25 pages × 800 tokens)
- Output: ~500 tokens/summary + 2,000 synthesis

Example: 10 papers, quick depth ≈ 30k tokens ≈ $0.15

## Manual Invocation

If not using `orchestrate.py`, spawn agents with prompts from `references/prompts/`:

```python
# Search agent
prompt = Path("references/prompts/search_agent.md").read_text()
prompt = prompt.format(source="ssrn", query="ESG credit risk")

# Reader agent  
prompt = Path("references/prompts/reader_agent.md").read_text()
prompt = prompt.format(paper_url="...", paper_title="...", depth="deep")

# Synthesis agent
prompt = Path("references/prompts/synthesis_agent.md").read_text()
prompt = prompt.format(query="...", summaries="...", output_format="structured")
```

## Bundled Resources

```
scripts/
  orchestrate.py        # Main parallel orchestration (quality-optimized)
  semantic_dedupe.py    # Embedding-based deduplication
  citation_expansion.py # Follow reference chains
  two_pass_synthesis.py # Draft → verify → revise

references/
  sources.md            # Source registry with URLs, access patterns
  output_formats.md     # Prose/structured format specs
  prompts/
    search_agent.md     # Search agent system prompt
    reader_agent.md     # Reader extraction template
    synthesis_agent.md  # Synthesis framework
```

## Limitations

- Cannot access paywalled content without institutional proxy
- Rate limiting on some sources (Scholar, Semantic Scholar)
- Token costs scale with paper count and depth
- Working papers (SSRN, NBER) not peer-reviewed
- Synthesis quality depends on paper availability and extraction success

### Quality Feature Tradeoffs

| Feature | Benefit | Cost |
|---------|---------|------|
| Semantic dedup | Better duplicate detection | Requires sentence-transformers (falls back gracefully) |
| Citation expansion | Finds seminal papers | +30% token cost, +1 search wave |
| Two-pass synthesis | Higher accuracy, fewer hallucinations | +50% synthesis tokens |

**Disable quality features for speed/cost**:
```bash
python scripts/orchestrate.py "query" --no-expand-citations --no-two-pass
```
