# Vector Databases & Embeddings

Comprehensive guide to vector storage and semantic search for RAG systems.

## Quick Selection Guide

```
Development/Testing?
├─ YES → ChromaDB (embedded, zero setup)
│   └─ Need persistence? → Add persist_directory
└─ NO (Production) →
    ├─ Have PostgreSQL? → pgvector (extend existing DB)
    ├─ Need hybrid search? → Elasticsearch or Weaviate
    ├─ Want managed? → Pinecone or Zilliz Cloud
    └─ Want self-hosted? → Qdrant or Milvus
```

## Vector Database Comparison

| Database | Type | Best For | Scalability | Cost | Complexity |
|----------|------|---------|-------------|------|------------|
| **ChromaDB** | Embedded | Development, small scale | Limited | Free | Very Low |
| **FAISS** | Library | Fast prototyping, research | Limited | Free | Low |
| **Qdrant** | Server | Production, self-hosted | High | Free/Paid | Medium |
| **Pinecone** | Cloud | Managed production | Very High | Paid | Low |
| **Weaviate** | Server | Hybrid search, GraphQL | High | Free/Paid | Medium |
| **Milvus** | Distributed | Massive scale, GPU | Very High | Free/Paid | High |
| **pgvector** | Extension | PostgreSQL users | Medium | Free | Low |
| **Elasticsearch** | Search engine | Existing ES infra | High | Free/Paid | Medium |

## Implementation Examples

### ChromaDB (Development)

**Best for:** Local development, testing, small projects

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# In-memory (temporary)
vector_store = Chroma.from_texts(
    texts=chunks,
    embedding=embeddings,
    collection_name="my_docs"
)

# Persistent (recommended)
vector_store = Chroma(
    collection_name="my_docs",
    embedding_function=embeddings,
    persist_directory="./chroma_db"  # Will persist to disk
)

# Add documents
vector_store.add_texts(texts=chunks, metadatas=metadata_list)

# Search
results = vector_store.similarity_search("query", k=5)
```

**Pros:** Zero setup, embedded, great for prototyping
**Cons:** Not for production scale, limited features

### Qdrant (Production Self-Hosted)

**Best for:** Production deployments, full control, good performance

```python
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)

vector_store = Qdrant(
    client=client,
    collection_name="my_docs",
    embeddings=embeddings
)

# Add with metadata filtering support
vector_store.add_texts(
    texts=chunks,
    metadatas=[
        {"source": "docs.example.com", "section": "api", "date": "2024-01-09"}
        for chunk in chunks
    ]
)

# Search with metadata filtering
results = vector_store.similarity_search(
    "API authentication",
    k=5,
    filter={"section": "api"}  # Only search API docs
)
```

**Pros:** Fast, scalable, metadata filtering, open source
**Cons:** Requires server setup, more complex

**Docker setup:**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Pinecone (Managed Cloud)

**Best for:** Production without infrastructure management

```python
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="your-api-key")

# Create index (one-time)
pc.create_index(
    name="my-docs",
    dimension=1536,  # OpenAI embedding dimension
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)

# Use with LangChain
vector_store = PineconeVectorStore.from_texts(
    texts=chunks,
    embedding=embeddings,
    index_name="my-docs"
)

# Search
results = vector_store.similarity_search("query", k=5)
```

**Pros:** Fully managed, auto-scaling, reliable
**Cons:** Costs money, vendor lock-in

**Pricing:** ~$70-120/month for small to medium usage

### Supabase pgvector (PostgreSQL)

**Best for:** Existing PostgreSQL infrastructure, SQL familiarity

```python
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client

supabase_client = create_client(
    supabase_url="your-project-url",
    supabase_key="your-anon-key"
)

vector_store = SupabaseVectorStore.from_texts(
    texts=chunks,
    embedding=embeddings,
    client=supabase_client,
    table_name="documents",
    query_name="match_documents"  # Postgres function
)

# Search
results = vector_store.similarity_search("query", k=5)
```

**Pros:** SQL queries, existing PostgreSQL knowledge, ACID compliance
**Cons:** Less optimized than specialized vector DBs

**Setup:** Enable pgvector extension in Supabase dashboard

### Weaviate (Hybrid Search)

**Best for:** Combining keyword and semantic search

```python
from langchain_community.vectorstores import Weaviate
import weaviate

client = weaviate.Client(url="http://localhost:8080")

vector_store = Weaviate.from_texts(
    texts=chunks,
    embedding=embeddings,
    client=client,
    by_text=False
)

# Hybrid search (keyword + semantic)
results = vector_store.similarity_search(
    "API authentication",
    k=5,
    search_type="hybrid",  # Combines BM25 + vector search
    alpha=0.5  # 0=pure keyword, 1=pure semantic
)
```

**Pros:** Built-in hybrid search, GraphQL API, schema validation
**Cons:** More complex setup, learning curve

## Embedding Models

### Model Comparison

| Model | Dimensions | Cost | Best For |
|-------|------------|------|---------|
| **OpenAI text-embedding-3-small** | 1536 | $0.00002/1K tokens | General purpose, good quality |
| **OpenAI text-embedding-3-large** | 3072 | $0.00013/1K tokens | Highest quality, expensive |
| **OpenAI ada-002** | 1536 | $0.0001/1K tokens | Legacy, still good |
| **sentence-transformers/all-MiniLM-L6-v2** | 384 | Free | Local, fast, decent quality |
| **INSTRUCTOR-large** | 768 | Free | Task-specific instructions |
| **multilingual-e5-large** | 1024 | Free | 100+ languages |
| **CLIP** | 512 | Free | Text + images |

### Implementation

```python
# OpenAI (recommended for production)
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    # Can adjust dimensions for storage savings:
    # dimensions=512  # Reduces from 1536 to 512
)

# Local model (free, privacy-preserving)
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},  # or 'cuda' for GPU
    encode_kwargs={'normalize_embeddings': True}  # Recommended
)

# Instruction-based (task-specific)
from langchain_community.embeddings import HuggingFaceInstructEmbeddings

embeddings = HuggingFaceInstructEmbeddings(
    model_name="hkunlp/instructor-large",
    embed_instruction="Represent the document for retrieval: "
)
```

## Index Configuration

### HNSW Index (Most Common)

**Best for:** Sub-100ms retrieval at 95%+ recall

```python
# Qdrant HNSW config
from qdrant_client.models import Distance, VectorParams

client.create_collection(
    collection_name="my_docs",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE,  # or DOT, EUCLIDEAN
        hnsw_config={
            "m": 16,  # Number of connections (default 16)
            "ef_construct": 100  # Construction time accuracy
        }
    )
)
```

**Parameters:**
- **m:** 8-64, higher = better accuracy, more memory
- **ef_construct:** 100-500, higher = better index quality, slower build
- **ef:** 100-500 at search time, higher = better accuracy, slower search

### IVF Index (Large Scale)

**Best for:** Billion-scale datasets

```python
import faiss

# Create IVF index
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist=100)

# Train on sample data
index.train(training_vectors)

# Add vectors
index.add(vectors)

# Search
index.nprobe = 10  # Search in 10 nearest clusters
D, I = index.search(query_vector, k=5)
```

**Parameters:**
- **nlist:** Number of clusters (√n to 4√n)
- **nprobe:** Clusters to search (1-nlist, higher = better accuracy)

## Search Strategies

### 1. Basic Similarity Search

```python
results = vector_store.similarity_search(
    query="How to authenticate API requests?",
    k=5  # Return top 5 most similar chunks
)
```

### 2. Similarity Search with Score

```python
results = vector_store.similarity_search_with_score(
    query="API authentication",
    k=10
)

# Filter by threshold
filtered = [(doc, score) for doc, score in results if score > 0.7]
```

### 3. MMR (Maximal Marginal Relevance)

**Balances relevance with diversity:**

```python
results = vector_store.max_marginal_relevance_search(
    query="API authentication",
    k=5,
    fetch_k=20,  # Fetch 20 candidates
    lambda_mult=0.7  # 0=max diversity, 1=max relevance
)
```

**Use when:** You want diverse results, not all similar

### 4. Metadata Filtering

```python
# Qdrant example
results = vector_store.similarity_search(
    query="API auth",
    k=5,
    filter={
        "must": [
            {"key": "section", "match": {"value": "api"}},
            {"key": "date", "range": {"gte": "2024-01-01"}}
        ]
    }
)

# Pinecone example
results = vector_store.similarity_search(
    query="API auth",
    k=5,
    filter={"section": {"$eq": "api"}}
)
```

### 5. Hybrid Search (Keyword + Semantic)

```python
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers import BM25Retriever

# Keyword retriever
bm25_retriever = BM25Retriever.from_texts(texts)
bm25_retriever.k = 5

# Semantic retriever
vector_retriever = vector_store.as_retriever(search_kwargs={"k": 5})

# Combine both
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.3, 0.7]  # 30% keyword, 70% semantic
)

results = ensemble_retriever.get_relevant_documents("query")
```

**Benefits:** Better recall, handles both keyword and semantic queries

## Reranking

**Improve top-k precision after initial retrieval:**

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank

# Get initial candidates
base_retriever = vector_store.as_retriever(search_kwargs={"k": 20})

# Rerank top candidates
compressor = CohereRerank(
    model="rerank-english-v2.0",
    top_n=5  # Return top 5 after reranking
)

retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever
)

results = retriever.get_relevant_documents("query")
```

**Benefits:** Much higher precision, better ranking
**Cost:** ~$1 per 1K rerank requests (Cohere)

## Performance Optimization

### 1. Batch Operations

```python
# Batch embedding (faster)
texts_batch = chunks[0:100]
vector_store.add_texts(texts_batch)  # Single API call

# vs. individual (slower)
for text in chunks:
    vector_store.add_texts([text])  # Many API calls
```

### 2. Async Operations

```python
import asyncio
from langchain_community.vectorstores import Qdrant

async def add_documents_async(chunks):
    tasks = [
        vector_store.aadd_texts(batch)
        for batch in batch_chunks(chunks, size=100)
    ]
    await asyncio.gather(*tasks)

asyncio.run(add_documents_async(all_chunks))
```

### 3. Connection Pooling

```python
from qdrant_client import QdrantClient

# Reuse client across requests
client = QdrantClient(
    host="localhost",
    port=6333,
    timeout=30,
    grpc_port=6334,
    prefer_grpc=True  # Faster than HTTP
)
```

### 4. Caching

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def get_embedding(text):
    # Cache embeddings for frequently accessed text
    return embeddings.embed_query(text)

# Or use Redis for distributed caching
import redis
r = redis.Redis(host='localhost', port=6379)

def get_cached_results(query):
    cache_key = hashlib.md5(query.encode()).hexdigest()
    cached = r.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    results = vector_store.similarity_search(query, k=5)
    r.setex(cache_key, 3600, json.dumps(results))  # Cache for 1 hour
    return results
```

## Monitoring & Metrics

### Essential Metrics

```python
import time

class VectorStoreMonitor:
    def __init__(self):
        self.query_latencies = []
        self.cache_hits = 0
        self.cache_misses = 0
    
    def track_query(self, query, k=5):
        start = time.time()
        results = vector_store.similarity_search(query, k=k)
        latency = time.time() - start
        
        self.query_latencies.append(latency)
        
        return results
    
    def get_stats(self):
        avg_latency = sum(self.query_latencies) / len(self.query_latencies)
        p95_latency = sorted(self.query_latencies)[int(len(self.query_latencies) * 0.95)]
        
        return {
            'avg_latency_ms': avg_latency * 1000,
            'p95_latency_ms': p95_latency * 1000,
            'cache_hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses),
            'total_queries': len(self.query_latencies)
        }
```

**Target metrics:**
- **Latency:** <100ms p95
- **Recall@5:** >80%
- **Precision@5:** >70%

## Cost Optimization

### Storage Costs

```python
# Calculate storage requirements
num_vectors = 10000
dimensions = 1536  # OpenAI embedding size
bytes_per_float = 4

storage_mb = (num_vectors * dimensions * bytes_per_float) / (1024 ** 2)
print(f"Storage needed: {storage_mb:.2f} MB")

# With metadata (~100 bytes per vector)
total_storage_mb = storage_mb + (num_vectors * 100 / (1024 ** 2))
```

**Monthly costs:**
- **Pinecone:** ~$0.50 per 1GB
- **Qdrant Cloud:** ~$0.30 per 1GB
- **Self-hosted:** ~$0.10 per 1GB (S3/disk)

### Embedding Costs

```python
# OpenAI pricing
tokens_per_chunk = 300
num_chunks = 10000

total_tokens = tokens_per_chunk * num_chunks
cost = (total_tokens / 1000) * 0.00002  # $0.00002 per 1K tokens

print(f"Embedding cost: ${cost:.2f}")  # Very cheap!
```

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Slow queries | No index optimization | Tune HNSW/IVF parameters |
| Poor recall | Bad embeddings or chunking | Test different embedding models |
| High costs | Too many chunks | Optimize chunk size |
| Memory issues | Large vectors in memory | Use disk-based storage, smaller dimensions |
| Stale results | No cache invalidation | Implement TTL on cache |
| Connection errors | No pooling | Use connection pool |

## Migration & Updates

### Re-embedding After Model Change

```python
# 1. Create new collection
new_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
new_vector_store = Qdrant(client=client, collection_name="my_docs_v2")

# 2. Re-embed all documents
for batch in batch_chunks(all_documents, size=100):
    new_vector_store.add_documents(batch)

# 3. Test thoroughly

# 4. Switch to new collection (atomic)
# Update app config to use "my_docs_v2"

# 5. Delete old collection (after verification)
client.delete_collection("my_docs")
```

## Next Steps

- For scraping optimization, see `web-scraping.md`
- For agentic retrieval patterns, see `agentic-retrieval.md`
- For complete pipeline integration, see `integration-patterns.md`
