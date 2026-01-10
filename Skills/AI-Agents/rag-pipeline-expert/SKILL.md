---
name: rag-pipeline-expert
description: Expert guidance for building complete RAG (Retrieval-Augmented Generation) pipelines with web scraping ingestion, vector databases, chunking strategies, and AI agent-based retrieval. Use when building RAG systems, implementing web scraping for knowledge bases, optimizing retrieval accuracy, choosing vector databases, configuring chunking strategies, or designing agentic retrieval patterns. Covers both pure Python/Docker implementations and n8n workflow integrations with balanced guidance on all major frameworks (LangChain, LlamaIndex, CrewAI, AutoGen, LangGraph).
---

# RAG Pipeline Expert

This skill provides comprehensive guidance for building production-ready RAG systems that combine web scraping, intelligent chunking, vector storage, and agentic retrieval.

## Core RAG Architecture

A complete RAG pipeline consists of four main components:

```
Web Scraping → Chunking → Vector Storage → Agentic Retrieval → LLM Response
```

**Component Selection Framework:**

1. **Web Scraping**: Choose based on target sites (static vs dynamic) and infrastructure (n8n vs code)
2. **Chunking**: Select strategy based on content type and retrieval precision needs
3. **Vector Database**: Balance between features, cost, and deployment requirements
4. **Agent Framework**: Match to workflow complexity (simple chains vs multi-agent systems)

## Quick Decision Guide

**For n8n workflows:**
- Scraping: Use n8n HTTP Request or ScrapeNinja community node
- Agents: CrewAI (YAML configs, structured workflows)
- Vector DB: Qdrant or Supabase pgvector (good n8n integration)

**For Python/Docker deployments:**
- Scraping: Playwright for dynamic sites, httpx/beautifulsoup for static
- Agents: LlamaIndex (RAG-first) or LangChain (versatile)
- Vector DB: ChromaDB (local/dev) or Pinecone (managed production)

**For maximum flexibility:**
- Hybrid approach: n8n for orchestration, Python for processing
- Refer to references/architecture-patterns.md for detailed patterns

## Implementation Workflow

### Phase 1: Data Ingestion (Web Scraping)

**Tool Selection:**
```python
# For static sites - Fast, low resource
if site_is_static and not requires_javascript:
    use_tool = "raw HTTP + BeautifulSoup"
    
# For dynamic sites - Full rendering
elif site_requires_javascript:
    use_tool = "Playwright or Puppeteer"
    
# For n8n workflows
elif using_n8n:
    use_tool = "ScrapeNinja node or HTTP Request node"
```

**Key capabilities to implement:**
- Recursive crawling (follow links to specified depth)
- Robots.txt compliance
- Rate limiting and retry logic
- Format conversion (HTML → Markdown/Text)
- Metadata extraction (title, timestamps, authors)

See references/web-scraping-guide.md for implementation details and code examples.

### Phase 2: Content Chunking

**Critical Performance Factor**: Proper chunking creates up to 9% difference in retrieval recall.

**Strategy Selection Framework:**
```
Content Type Analysis:
├── Structured (code, JSON, docs) → Document Structure chunking
├── Narrative (articles, blogs) → Recursive Character with overlap
├── Technical (APIs, specs) → Semantic Splitting
└── Mixed/Unknown → Start with Recursive Character (300 tokens, 50 overlap)
```

**Optimal Starting Parameters:**
- Chunk size: 250-300 tokens (~1000-1200 characters)
- Overlap: 10-20% (50-60 tokens)
- Max chunk size: Never exceed embedding model limit (typically 8K tokens)

**Quality Validation:**
- Check that sentences aren't split mid-word
- Verify context preservation at chunk boundaries
- Test retrieval with sample queries

See references/chunking-strategies.md for detailed implementation patterns.

### Phase 3: Vector Storage & Indexing

**Database Selection Matrix:**

| Use Case | Recommended | Rationale |
|----------|-------------|-----------|
| Local development | ChromaDB | Embedded, zero-config |
| n8n workflows | Qdrant or Supabase | Native n8n nodes available |
| Production scale | Pinecone or Zilliz | Managed, auto-scaling |
| Existing PostgreSQL | pgvector | Leverage existing infrastructure |
| Hybrid search | Elasticsearch or Weaviate | BM25 + vector support |

**Indexing Best Practices:**
- Normalize embeddings before storage (unit vectors)
- Use HNSW algorithm for sub-100ms retrieval
- Add metadata fields for filtering (source, date, category)
- Implement retention policies for cost control

**Embedding Model Selection:**
- General: `text-embedding-3-small` (OpenAI) or `all-MiniLM-L6-v2` (local)
- Multilingual: `multilingual-e5-large`
- Instruction-tuned: `INSTRUCTOR-large`
- Multimodal: `CLIP` (text + images)

See references/vector-databases.md for setup guides and optimization tips.

### Phase 4: Agentic Retrieval

**Framework Selection:**

Choose based on workflow complexity:

```
Simple RAG (query → retrieve → respond):
└── Use: LlamaIndex query engine OR LangChain retrieval chain

Structured workflows (research → filter → synthesize):
└── Use: CrewAI (role-based) OR LangChain with chains

Complex decision trees (conditional routing, parallel processing):
└── Use: LangGraph (graph-based) OR AutoGen (conversational)

Multi-agent collaboration (supervisor + specialized workers):
└── Use: CrewAI (hierarchical) OR LangGraph (graph) OR AutoGen (groupchat)
```

**Core Retrieval Patterns:**

1. **Basic RAG**: Vector search → Top-K → Inject to prompt
2. **Hybrid Retrieval**: Vector search + BM25 keyword → Rerank → Top-K
3. **Agentic RAG**: Agent decides when/what to retrieve → Multiple queries → Synthesize
4. **Self-RAG**: Model evaluates retrieval quality → Retry if insufficient

**Advanced Techniques:**
- **Reranking**: Use Cohere ReRank or ColBERT to refine top-K results
- **HyDE**: Generate hypothetical document, embed it, retrieve similar
- **Query expansion**: Rewrite user query multiple ways for better coverage
- **Metadata filtering**: Narrow search space before vector similarity

See references/agentic-retrieval.md for implementation patterns and code examples.

## Evaluation & Optimization

**Key Metrics to Track:**

1. **Retrieval Quality:**
   - Recall@K: % of relevant chunks in top-K results
   - Precision@K: % of retrieved chunks that are relevant
   - MRR (Mean Reciprocal Rank): Position of first relevant result
   - NDCG: Ranking quality metric

2. **Performance:**
   - End-to-end latency (target: <5s for user-facing apps)
   - Per-component timing (scraping, chunking, retrieval, generation)
   - Cost per query (API calls, compute, storage)

3. **Response Quality:**
   - Answer relevance (human eval or LLM-as-judge)
   - Hallucination rate (groundedness check)
   - Citation accuracy (links back to source)

**Optimization Checklist:**
- [ ] Chunk size tuned for your content type
- [ ] Overlap configured (10-20%)
- [ ] Metadata fields used for filtering
- [ ] Reranking implemented for top-K refinement
- [ ] Caching for frequently retrieved chunks
- [ ] Monitoring dashboards set up

See references/evaluation-metrics.md for measurement frameworks.

## Common Patterns by Use Case

### Pattern 1: Documentation RAG
**Scenario**: Technical documentation, help centers, API docs

**Stack:**
- Scraping: Recursive crawler (respects site structure)
- Chunking: Document structure (preserve sections/headers)
- Vector DB: Qdrant or Weaviate (filtering by version/category)
- Retrieval: LlamaIndex query engine with metadata filters

### Pattern 2: News/Content Aggregation
**Scenario**: News monitoring, competitor research, trend analysis

**Stack:**
- Scraping: Scheduled crawls with Apify or custom scrapers
- Chunking: Fixed-size with overlap (articles have similar structure)
- Vector DB: Pinecone (time-series filtering)
- Retrieval: Hybrid search (keyword + semantic) with recency boost

### Pattern 3: Enterprise Knowledge Base
**Scenario**: Internal docs, wikis, support tickets, Slack history

**Stack:**
- Scraping: Multiple connectors (Confluence, Slack, Drive)
- Chunking: Semantic splitting (preserve meaning across diverse content)
- Vector DB: Weaviate or Elasticsearch (ACL support, hybrid search)
- Retrieval: Multi-agent (different agents for different sources)

### Pattern 4: Research Assistant
**Scenario**: Academic papers, scientific articles, deep research

**Stack:**
- Scraping: PDF extraction + web search integration
- Chunking: Large chunks (400-500 tokens) with 20% overlap
- Vector DB: Zilliz Cloud (large scale, GPU acceleration)
- Retrieval: Agentic with chain-of-thought (plan → search → refine → synthesize)

See references/architecture-patterns.md for complete implementation examples.

## Cost Optimization

**Web Scraping:**
- Use raw HTTP for static sites (2x faster than browser)
- Implement caching for frequently scraped pages
- Batch requests in standby/pooled mode

**Embeddings:**
- Consider local models for dev/privacy (all-MiniLM-L6-v2)
- Use smaller embedding models when quality permits
- Batch embed in larger chunks (1000+ at once)

**Vector Storage:**
- Implement retention policies (delete old/irrelevant chunks)
- Use quantization for large datasets (PQ, SQ)
- Consider serverless options (pay-per-query)

**LLM Generation:**
- Return only relevant chunks (don't overstuff context)
- Use smaller models when possible (GPT-3.5 vs GPT-4)
- Implement caching for common queries

## Troubleshooting Guide

**Poor Retrieval Quality:**
1. Check chunk size (try 200, 300, 400 tokens)
2. Adjust overlap (increase to 20-25%)
3. Try semantic chunking instead of fixed-size
4. Add metadata filters to narrow search space
5. Implement reranking (Cohere ReRank)

**Slow Performance:**
1. Use raw HTTP scraping for static sites
2. Reduce maxResults for web search
3. Implement caching layer
4. Use smaller embedding models
5. Optimize vector DB index (HNSW params)

**High Costs:**
1. Reduce embedding dimensions if possible
2. Implement aggressive caching
3. Use local/smaller models where quality permits
4. Batch operations efficiently
5. Set retention policies on vector storage

**Hallucinations/Inaccurate Responses:**
1. Increase chunk context size
2. Retrieve more chunks (higher K)
3. Implement citation verification
4. Add prompt engineering (require citations)
5. Use reranking to improve chunk relevance

## Integration Examples

### With n8n

Load n8n workflow components from references/n8n-integration.md for:
- Complete workflow JSON templates
- Node configuration examples
- Error handling patterns
- Monitoring setup

### With Python/Docker

Load implementation guides from references/python-implementation.md for:
- Complete FastAPI application template
- Docker compose configurations
- Production deployment patterns
- Monitoring and logging setup

## Next Steps

After reading this skill:

1. **Determine your requirements**: Content type, scale, latency needs, budget
2. **Choose your stack**: Use decision frameworks above
3. **Load detailed references**: Read relevant reference files for implementation
4. **Start with Phase 1**: Implement web scraping first
5. **Iterate on quality**: Use evaluation metrics to optimize

**Detailed implementation guides available:**
- references/web-scraping-guide.md - Complete scraping implementations
- references/chunking-strategies.md - All chunking methods with code
- references/vector-databases.md - Database setup and optimization
- references/agentic-retrieval.md - Agent patterns and frameworks
- references/architecture-patterns.md - Complete system architectures
- references/evaluation-metrics.md - Measurement and testing
- references/n8n-integration.md - n8n workflow templates
- references/python-implementation.md - Python/FastAPI templates
