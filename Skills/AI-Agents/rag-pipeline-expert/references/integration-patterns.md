# RAG Integration Patterns

Complete end-to-end RAG pipeline architectures and implementation patterns.

## Complete Pipeline Architectures

### Architecture 1: Basic RAG (Development)

```
┌──────────────┐     ┌─────────┐     ┌──────────┐     ┌───────────┐
│   Scraper    │────▶│ Chunker │────▶│ Embedder │────▶│ ChromaDB  │
│ (BeautifulSoup)│    │ (300/50) │    │ (OpenAI) │    │ (local)   │
└──────────────┘     └─────────┘     └──────────┘     └───────────┘
                                                              │
                                                              ▼
┌──────────────┐     ┌─────────┐     ┌──────────────────────┘
│   Response   │◀────│   LLM   │◀────│  Vector Search (k=5)
│              │     │ (GPT-4) │     │
└──────────────┘     └─────────┘     └──────────────────────┘
```

**Implementation:**
```python
# Pipeline setup
from rag_scraper.scraper import Scraper
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma

# 1. Ingestion
html = Scraper.fetch_html(url)
markdown = Converter.html_to_markdown(html)

# 2. Chunking
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = splitter.split_text(markdown)

# 3. Storage
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = Chroma.from_texts(chunks, embeddings)

# 4. Retrieval
def query(question):
    docs = vector_store.similarity_search(question, k=5)
    context = "\n\n".join([d.page_content for d in docs])
    
    llm = ChatOpenAI(model="gpt-4")
    response = llm.invoke(f"Context: {context}\n\nQuestion: {question}")
    
    return response.content
```

**Best for:** Development, prototyping, small projects
**Estimated cost:** <$5/month

### Architecture 2: Production RAG (Code-Based)

```
┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  FastAPI     │     │   Celery    │     │   Worker     │
│  Endpoint    │────▶│   Queue     │────▶│   Pool       │
└──────────────┘     └─────────────┘     └──────────────┘
                                                 │
        ┌────────────────────────────────────────┘
        ▼                                 ▼
┌──────────────┐                   ┌──────────────┐
│  Playwright  │                   │   Qdrant     │
│  Scraper     │──────────────────▶│   Cluster    │
└──────────────┘                   └──────────────┘
                                          │
┌──────────────┐     ┌─────────────┐     │
│   Redis      │◀────│    LLM      │◀────┘
│   Cache      │     │   (GPT-4)   │
└──────────────┘     └─────────────┘
        │                   │
        └───────────────────┘
                    │
        ┌───────────────────────┐
        │    Prometheus +       │
        │    Grafana            │
        │    (Monitoring)       │
        └───────────────────────┘
```

**Implementation:**
```python
# app.py (FastAPI)
from fastapi import FastAPI, BackgroundTasks
from celery_app import scrape_and_index

app = FastAPI()

@app.post("/ingest")
async def ingest_url(url: str, background_tasks: BackgroundTasks):
    task = scrape_and_index.delay(url)
    return {"task_id": task.id, "status": "processing"}

@app.post("/query")
async def query(question: str):
    # Check cache
    cached = redis_client.get(f"query:{hash(question)}")
    if cached:
        return {"answer": cached, "source": "cache"}
    
    # Retrieve from Qdrant
    results = qdrant_client.search(
        collection_name="documents",
        query_vector=embeddings.embed_query(question),
        limit=5
    )
    
    # Generate answer
    context = "\n".join([r.payload['text'] for r in results])
    answer = llm.invoke(f"Context: {context}\n\nQuestion: {question}")
    
    # Cache result
    redis_client.setex(f"query:{hash(question)}", 3600, answer.content)
    
    return {"answer": answer.content, "sources": results}

# celery_app.py (Background tasks)
from celery import Celery

celery = Celery('rag_tasks', broker='redis://localhost:6379')

@celery.task
def scrape_and_index(url):
    # Scrape
    html = scraper.fetch(url)
    
    # Chunk
    chunks = splitter.split_text(html)
    
    # Embed and store
    qdrant_client.upsert(
        collection_name="documents",
        points=[{
            "id": f"{url}_{i}",
            "vector": embeddings.embed_query(chunk),
            "payload": {"text": chunk, "source": url}
        } for i, chunk in enumerate(chunks)]
    )
```

**Best for:** Production applications, high traffic
**Estimated cost:** $200-500/month

### Architecture 3: n8n Workflow Automation

```
┌──────────────────┐
│ Schedule Trigger │
│  (Daily 2 AM)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ScrapeNinja Node │
│ (Recursive)      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Code Node       │
│  (Chunk + Meta)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Supabase Node    │
│ (pgvector)       │
└────────┬─────────┘
         │
┌────────┴─────────┐
│                  │
▼                  ▼
[Webhook Trigger]  [Scheduled Report]
│                  │
▼                  ▼
[Vector Search]    [Quality Check]
│                  │
▼                  ▼
[OpenAI Node]      [Slack Notification]
│
▼
[Respond to Webhook]
```

**n8n Workflow JSON excerpt:**
```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": { "rule": { "interval": [{"field": "hours", "value": 24}] } }
    },
    {
      "type": "n8n-nodes-scrapeninja.scrapeNinja",
      "parameters": {
        "url": "={{$json.target_url}}",
        "recursive": true,
        "maxDepth": 3
      }
    },
    {
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "// Chunking logic\nconst chunks = [];\n..."
      }
    },
    {
      "type": "n8n-nodes-base.supabase",
      "parameters": {
        "operation": "insert",
        "table": "documents"
      }
    }
  ]
}
```

**Best for:** Teams preferring visual workflows, easier maintenance
**Estimated cost:** $50-150/month (n8n + services)

### Architecture 4: Multi-Agent Research

```
┌──────────────┐
│ User Query   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Router Agent │─────┐
└──────────────┘     │
       │             │
       ▼             ▼
┌──────────────┐   ┌────────────────┐   ┌──────────────┐
│ Web Scraper  │   │ Vector Search  │   │ SQL Database │
│ Agent        │   │ Agent          │   │ Agent        │
└──────┬───────┘   └────────┬───────┘   └──────┬───────┘
       │                    │                   │
       └────────────────────┴───────────────────┘
                            │
                            ▼
                   ┌──────────────┐
                   │ Synthesizer  │
                   │ Agent        │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ Response     │
                   └──────────────┘
```

**Implementation (CrewAI):**
```python
from crewai import Agent, Task, Crew

# Define agents
web_researcher = Agent(
    role="Web Research Specialist",
    goal="Find current information from the web",
    tools=[web_search_tool, scraping_tool],
    backstory="Expert at finding relevant online information"
)

knowledge_retriever = Agent(
    role="Knowledge Base Specialist",
    goal="Search internal documentation",
    tools=[vector_search_tool],
    backstory="Deep knowledge of company documentation"
)

data_analyst = Agent(
    role="Data Analyst",
    goal="Query databases for numerical data",
    tools=[sql_tool],
    backstory="Expert at SQL and data analysis"
)

synthesizer = Agent(
    role="Information Synthesizer",
    goal="Combine all sources into coherent answer",
    backstory="Expert at creating comprehensive reports"
)

# Define tasks
research_task = Task(
    description="Research {topic} from web and knowledge base",
    agent=web_researcher,
    expected_output="Summary of findings"
)

data_task = Task(
    description="Get relevant metrics for {topic}",
    agent=data_analyst,
    expected_output="Key metrics and trends"
)

synthesis_task = Task(
    description="Create comprehensive report combining all findings",
    agent=synthesizer,
    expected_output="Final report with citations",
    context=[research_task, data_task]
)

# Create crew
crew = Crew(
    agents=[web_researcher, knowledge_retriever, data_analyst, synthesizer],
    tasks=[research_task, data_task, synthesis_task],
    process="sequential"  # or "hierarchical"
)

# Execute
result = crew.kickoff(inputs={"topic": "Q4 sales performance"})
```

**Best for:** Complex queries, research tasks, multi-source analysis
**Estimated cost:** $500-1000/month (high LLM usage)

## Error Handling Patterns

### Retry with Exponential Backoff

```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s")
                    time.sleep(delay)
        
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3)
def scrape_url(url):
    return requests.get(url, timeout=10)
```

### Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
            
            raise

# Usage
breaker = CircuitBreaker()
result = breaker.call(vector_store.similarity_search, query, k=5)
```

### Graceful Degradation

```python
def query_with_fallback(question):
    try:
        # Try agentic retrieval
        return agent_retrieval(question)
    except Exception as e:
        logger.warning(f"Agent failed: {e}, falling back to vector search")
        
        try:
            # Fallback to basic vector search
            return basic_vector_search(question)
        except Exception as e2:
            logger.error(f"Vector search failed: {e2}, using generic response")
            
            # Ultimate fallback
            return "I'm experiencing technical difficulties. Please try again later."
```

## Monitoring & Observability

### Comprehensive Monitoring

```python
from prometheus_client import Counter, Histogram, Gauge
import logging

# Metrics
query_total = Counter('rag_queries_total', 'Total queries')
query_latency = Histogram('rag_query_latency_seconds', 'Query latency')
cache_hits = Counter('rag_cache_hits_total', 'Cache hits')
retrieval_quality = Gauge('rag_retrieval_quality', 'Retrieval quality score')

# Structured logging
import structlog

logger = structlog.get_logger()

@query_latency.time()
def query_pipeline(question):
    query_total.inc()
    
    logger.info("query_started", question=question)
    
    try:
        # Check cache
        if cached := cache.get(question):
            cache_hits.inc()
            logger.info("cache_hit", question=question)
            return cached
        
        # Retrieve
        docs = vector_store.similarity_search(question, k=5)
        logger.info("retrieval_complete", num_docs=len(docs))
        
        # Generate
        answer = llm.invoke(f"Context: {docs}\n\nQuestion: {question}")
        
        # Measure quality (if ground truth available)
        quality = evaluate_answer(question, answer)
        retrieval_quality.set(quality)
        
        # Cache
        cache.set(question, answer)
        
        logger.info("query_complete", question=question, quality=quality)
        
        return answer
        
    except Exception as e:
        logger.error("query_failed", question=question, error=str(e))
        raise
```

### LangSmith Integration

```python
from langsmith import Client
from langsmith.run_helpers import traceable

client = Client()

@traceable(run_type="chain", name="RAG Pipeline")
def rag_pipeline(question: str):
    # LangSmith automatically traces this
    docs = retriever.get_relevant_documents(question)
    answer = llm.invoke(f"Context: {docs}\n\nQuestion: {question}")
    return answer

# View traces at smith.langchain.com
```

## Caching Strategies

### Multi-Level Cache

```python
from functools import lru_cache
import redis

# Level 1: In-memory (LRU)
@lru_cache(maxsize=100)
def get_embedding_l1(text):
    return embeddings.embed_query(text)

# Level 2: Redis
redis_client = redis.Redis()

def get_embedding_l2(text):
    cached = redis_client.get(f"emb:{hash(text)}")
    if cached:
        return pickle.loads(cached)
    
    embedding = embeddings.embed_query(text)
    redis_client.setex(f"emb:{hash(text)}", 86400, pickle.dumps(embedding))
    return embedding

# Combined
def get_embedding(text):
    try:
        return get_embedding_l1(text)  # Try L1 first
    except:
        return get_embedding_l2(text)  # Fall back to L2
```

## Testing Strategies

### Unit Tests

```python
import pytest

def test_chunking():
    text = "This is a test. " * 100
    chunks = chunker.split_text(text)
    
    assert len(chunks) > 0
    assert all(len(chunk) <= 1000 for chunk in chunks)
    assert sum(len(chunk) for chunk in chunks) >= len(text) * 0.9  # Account for overlap

def test_retrieval():
    vector_store.add_texts(["Python is a programming language"])
    results = vector_store.similarity_search("What is Python?", k=1)
    
    assert len(results) == 1
    assert "Python" in results[0].page_content
```

### Integration Tests

```python
def test_end_to_end():
    # Ingest
    url = "https://example.com/test-doc"
    ingest_pipeline(url)
    
    # Query
    answer = query_pipeline("What is the main topic?")
    
    assert answer is not None
    assert len(answer) > 10
```

### Evaluation with Ground Truth

```python
test_cases = [
    ("What's the refund policy?", "expected_doc_id_1"),
    ("How do I reset password?", "expected_doc_id_2"),
]

def evaluate_system():
    scores = []
    for question, expected_id in test_cases:
        docs = retriever.get_relevant_documents(question)
        
        # Did we retrieve the right doc?
        found = any(expected_id in d.metadata['id'] for d in docs)
        scores.append(1 if found else 0)
    
    accuracy = sum(scores) / len(scores)
    print(f"Retrieval accuracy: {accuracy:.2%}")
    
    assert accuracy > 0.8  # 80% threshold
```

## Cost Management

### Budget Tracking

```python
class CostTracker:
    def __init__(self):
        self.costs = {
            'embedding': 0,
            'llm': 0,
            'storage': 0,
            'scraping': 0
        }
    
    def track_embedding(self, tokens):
        cost = (tokens / 1000) * 0.00002  # OpenAI pricing
        self.costs['embedding'] += cost
    
    def track_llm(self, input_tokens, output_tokens):
        cost = (input_tokens / 1000) * 0.0005 + (output_tokens / 1000) * 0.0015
        self.costs['llm'] += cost
    
    def report(self):
        total = sum(self.costs.values())
        return {
            **self.costs,
            'total': total,
            'breakdown': {k: f"{(v/total)*100:.1f}%" for k, v in self.costs.items()}
        }
```

## Security Best Practices

### Input Validation

```python
def sanitize_query(query: str) -> str:
    # Remove potential injection attempts
    query = re.sub(r'[^\w\s\?\.,!-]', '', query)
    
    # Limit length
    if len(query) > 1000:
        raise ValueError("Query too long")
    
    return query.strip()
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter

@app.post("/query")
@limiter.limit("10/minute")
async def query(request: Request, question: str):
    return {"answer": query_pipeline(question)}
```

## Deployment Checklist

- [ ] Environment variables for secrets
- [ ] Logging and monitoring configured
- [ ] Error handling and retries
- [ ] Caching implemented
- [ ] Rate limiting enabled
- [ ] Health check endpoint
- [ ] Database backups automated
- [ ] Cost tracking active
- [ ] Security review complete
- [ ] Load testing performed
- [ ] Documentation updated
- [ ] Rollback plan documented

## Next Steps

- For component details, see other reference files
- For production deployment, follow checklist above
- For optimization, monitor metrics and iterate
