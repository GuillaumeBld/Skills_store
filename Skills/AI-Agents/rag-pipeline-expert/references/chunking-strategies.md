# Chunking Strategies for RAG

**Critical insight:** Chunking is the #1 factor affecting RAG performance. Poor chunking can create up to a 9% gap in recall performance.

## The Chunking Dilemma

**Too large:** Chunks mix multiple topics, dilute semantic meaning, reduce retrieval precision
**Too small:** Chunks lose context, miss the big picture, may fragment key information
**Just right:** Focused content, preserved context, optimal for both search and generation

## Quick Decision Matrix

| Document Type | Chunk Size | Overlap | Strategy | Reasoning |
|--------------|------------|---------|----------|-----------|
| Technical docs | 400-500 tokens | 50-75 | Document structure | Preserve API descriptions, code examples |
| Customer support | 150-250 tokens | 30-50 | Fixed/Semantic | Isolate specific issues, quick retrieval |
| Research papers | 300-400 tokens | 50-100 | Semantic | Maintain argument flow, cite properly |
| News articles | 250-350 tokens | 50 | Recursive character | Balance detail and context |
| Code documentation | 300-500 tokens | 75-100 | Language-aware | Keep functions/classes together |
| General web content | 300 tokens | 50 | Recursive character | Default starting point |

## Strategy Comparison

### 1. Fixed-Size Chunking

**How it works:** Split text into equal-sized pieces by character/token count

**Implementation:**
```python
from langchain.text_splitter import CharacterTextSplitter

splitter = CharacterTextSplitter(
    chunk_size=1000,  # characters
    chunk_overlap=200,
    separator="\n\n"
)
chunks = splitter.split_text(text)
```

**Pros:**
- Fast and predictable
- Consistent embedding sizes
- Low computational cost

**Cons:**
- May split mid-sentence or mid-word
- Ignores document structure
- Can lose context at boundaries

**Best for:** Homogeneous datasets (news articles, blog posts)

### 2. Recursive Character Splitting ⭐ **RECOMMENDED DEFAULT**

**How it works:** Try splitting by paragraphs first, then sentences, then words, recursively until chunk size is met

**Implementation:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,  # tokens ~= 400 characters
    chunk_overlap=50,  # 10-20% overlap
    separators=["\n\n", "\n", ". ", " ", ""],
    length_function=len
)
chunks = splitter.split_text(text)
```

**Pros:**
- Respects natural text boundaries
- Good balance of context and specificity
- Works well across document types
- Industry standard (10-20% overlap)

**Cons:**
- More complex than fixed-size
- May still split awkwardly on edge cases

**Best for:** Most use cases, especially when starting out

### 3. Document Structure-Based

**How it works:** Split based on document structure (headers, sections, lists)

**Implementation:**
```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
chunks = splitter.split_text(markdown_text)
```

**Pros:**
- Preserves logical document structure
- Maintains topical coherence
- Natural chunk boundaries

**Cons:**
- Requires structured documents
- Variable chunk sizes
- May create very large or small chunks

**Best for:** Technical documentation, APIs, structured content

### 4. Semantic Chunking

**How it works:** Use embeddings to identify semantic similarity and chunk based on topic changes

**Implementation:**
```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

splitter = SemanticChunker(
    embeddings=OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile"  # or "standard_deviation"
)
chunks = splitter.split_text(text)
```

**Pros:**
- Respects semantic boundaries
- Adapts to content naturally
- High-quality chunks

**Cons:**
- Computationally expensive (requires embeddings)
- Slower processing
- Variable chunk sizes

**Best for:** Complex documents, research papers, nuanced content

### 5. Language-Aware Splitting

**How it works:** Use language-specific parsing to split code intelligently

**Implementation:**
```python
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter

python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=500,
    chunk_overlap=100
)

# Keeps functions and classes together
chunks = python_splitter.split_text(python_code)
```

**Supported languages:** Python, JavaScript, TypeScript, Java, C++, Go, Rust, and more

**Pros:**
- Preserves code structure
- Keeps functions/classes together
- Syntax-aware

**Cons:**
- Language-specific
- Only for code
- Requires language detection

**Best for:** Code documentation, API references, technical repos

### 6. Token-Based Splitting

**How it works:** Split by actual tokens (as LLMs see them), not characters

**Implementation:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

def tiktoken_len(text):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    return len(tokenizer.encode(text))

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,  # tokens, not characters
    chunk_overlap=50,
    length_function=tiktoken_len,
    separators=["\n\n", "\n", " ", ""]
)
```

**Pros:**
- Aligns with embedding model limits
- More accurate sizing
- Better for LLM context windows

**Cons:**
- Slower due to tokenization
- Language-dependent token counts

**Best for:** When you need precise token control

## Overlap Strategy

**Why overlap matters:** Prevents information loss at chunk boundaries

**Optimal overlap:**
- **10-20% of chunk size** (industry standard)
- Example: 300-token chunks → 30-60 token overlap

**Overlap examples:**

```python
# 300 tokens, 50 overlap
Chunk 1: tokens 0-300
Chunk 2: tokens 250-550 (last 50 from chunk 1)
Chunk 3: tokens 500-800 (last 50 from chunk 2)
```

**Benefits:**
- Preserves context across boundaries
- Reduces information fragmentation
- Improves retrieval recall

**Trade-offs:**
- More chunks = more storage
- Potential duplicate information
- Slightly higher embedding costs

## Chunk Size Optimization

### Finding Optimal Size

**Start with 250-300 tokens**, then iterate based on:

1. **Embedding model limits:**
   - OpenAI: 8,191 tokens max
   - Sentence Transformers: Varies (usually 256-512)
   - Most use 384-512 tokens

2. **Query complexity:**
   - Simple lookups → Smaller chunks (150-250)
   - Complex reasoning → Larger chunks (400-600)

3. **Document characteristics:**
   - Dense technical → Larger chunks
   - FAQ/QA → Smaller chunks

### Testing Approach

```python
def test_chunk_sizes(documents, queries, sizes=[150, 250, 300, 400, 500]):
    results = {}
    
    for size in sizes:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=size,
            chunk_overlap=int(size * 0.15)  # 15% overlap
        )
        
        chunks = splitter.split_documents(documents)
        vector_store = create_vector_store(chunks)
        
        # Measure retrieval quality
        hit_rate = evaluate_retrieval(vector_store, queries)
        results[size] = hit_rate
    
    return results  # Choose size with best hit rate
```

## Metadata Enrichment

**Add metadata to chunks for better retrieval:**

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)

# Create documents with metadata
documents = [
    Document(
        page_content=chunk,
        metadata={
            "source": "docs.example.com/guide",
            "title": "Installation Guide",
            "section": "Prerequisites",
            "chunk_id": i,
            "timestamp": "2024-01-09",
            "doc_type": "documentation"
        }
    )
    for i, chunk in enumerate(chunks)
]
```

**Useful metadata fields:**
- **source:** URL or file path
- **title:** Document title
- **section:** Section/header the chunk belongs to
- **chunk_id:** Sequential identifier
- **timestamp:** When scraped/indexed
- **author:** Content author
- **language:** Content language
- **doc_type:** documentation, article, code, etc.

**Benefits:**
- Enable metadata filtering during search
- Improve retrieval precision
- Easier debugging and tracing
- Support for hybrid search

## Pre-processing Before Chunking

**Clean text for better chunking:**

```python
import re

def clean_text_for_chunking(text):
    # Lowercase (optional, depending on use case)
    # text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common encoding issues
    text = text.replace('\xa0', ' ')  # non-breaking space
    text = text.replace('\u200b', '')  # zero-width space
    
    # Remove URLs (if not needed)
    # text = re.sub(r'http\S+', '', text)
    
    # Normalize line breaks
    text = text.replace('\r\n', '\n')
    
    return text.strip()
```

**Normalization considerations:**
- **Lowercasing:** Helps matching but loses capitalization context
- **Stop words:** Usually keep them (they provide context)
- **Spelling correction:** Can help but adds complexity
- **Unicode normalization:** Important for multilingual content

## Advanced Chunking Patterns

### Hierarchical Chunking

**Create parent-child chunk relationships:**

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Parent chunks (larger)
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)

# Child chunks (smaller, for search)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

# Store both
store = InMemoryStore()
retriever = ParentDocumentRetriever(
    vectorstore=vector_store,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter
)

# Search with small chunks, retrieve with large context
retriever.add_documents(documents)
```

**Benefits:**
- Better search precision (small chunks)
- Better generation context (large chunks)
- Best of both worlds

### Sliding Window Chunking

**Create overlapping windows for continuity:**

```python
def sliding_window_chunks(text, window_size=300, stride=250):
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), stride):
        chunk = ' '.join(words[i:i + window_size])
        if len(chunk.split()) >= 100:  # Minimum chunk size
            chunks.append(chunk)
    
    return chunks
```

**Overlap = window_size - stride**
Example: 300 words window, 250 stride = 50 words overlap (16.7%)

### Multi-Representation Chunking

**Store multiple versions of same content:**

```python
# Original chunk
original = long_chunk

# Summary for search
summary = llm.summarize(original)

# Store both with link
vector_store.add_texts(
    texts=[summary],
    metadatas=[{"full_text_id": chunk_id}]
)

# Retrieve summary, return full text
```

**Pattern:**
1. Search with compressed/summary version
2. Retrieve full detailed version
3. Better search precision + complete context

## Evaluation Metrics

**Measure chunking quality:**

### 1. Hit Rate (Recall@k)
```python
def calculate_hit_rate(queries, vector_store, k=5):
    hits = 0
    
    for query, expected_doc_id in queries:
        results = vector_store.similarity_search(query, k=k)
        if any(expected_doc_id in r.metadata['source'] for r in results):
            hits += 1
    
    return hits / len(queries)
```

**Target: >80% hit rate at k=5**

### 2. Precision@k
```python
def calculate_precision(queries, vector_store, k=5):
    precisions = []
    
    for query, relevant_doc_ids in queries:
        results = vector_store.similarity_search(query, k=k)
        relevant_retrieved = sum(
            1 for r in results if r.metadata['source'] in relevant_doc_ids
        )
        precisions.append(relevant_retrieved / k)
    
    return sum(precisions) / len(queries)
```

**Target: >70% precision**

### 3. Mean Reciprocal Rank (MRR)
```python
def calculate_mrr(queries, vector_store):
    reciprocal_ranks = []
    
    for query, expected_doc_id in queries:
        results = vector_store.similarity_search(query, k=10)
        for i, result in enumerate(results, 1):
            if expected_doc_id in result.metadata['source']:
                reciprocal_ranks.append(1 / i)
                break
        else:
            reciprocal_ranks.append(0)
    
    return sum(reciprocal_ranks) / len(queries)
```

**Target: >0.7 MRR**

## Common Chunking Mistakes

| Mistake | Impact | Solution |
|---------|--------|----------|
| Chunks too large | Diluted meaning, poor retrieval | Reduce to 300-400 tokens |
| No overlap | Information loss at boundaries | Add 10-20% overlap |
| Ignoring structure | Fragmented context | Use structure-aware splitting |
| No metadata | Poor filtering, hard to debug | Add source, title, section |
| Same strategy for all | Suboptimal for varied content | Match strategy to document type |
| No testing | Unknown performance | Measure hit rate and precision |

## Chunking for Specific Use Cases

### FAQ / Customer Support
```python
# Small chunks, high precision
splitter = RecursiveCharacterTextSplitter(
    chunk_size=150,  # One Q&A pair per chunk
    chunk_overlap=30,
    separators=["\n\nQ:", "\n\n", "\n"]
)
```

### Technical Documentation
```python
# Larger chunks, preserve context
splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "Header 1"), ("##", "Header 2")],
    strip_headers=False  # Keep headers for context
)

# Then further split if needed
secondary_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=75
)
```

### Code Repositories
```python
# Language-aware with metadata
python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=400,
    chunk_overlap=100
)

# Add function/class names to metadata
chunks_with_metadata = add_code_metadata(chunks)
```

### Research Papers
```python
# Semantic chunking to preserve arguments
semantic_splitter = SemanticChunker(
    embeddings=OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=75  # More conservative splitting
)
```

## Integration with Vector Stores

**Complete chunking-to-storage pipeline:**

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

# 1. Prepare documents
documents = [
    Document(page_content=doc['text'], metadata=doc['metadata'])
    for doc in raw_documents
]

# 2. Chunk with overlap
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    length_function=len
)
chunks = splitter.split_documents(documents)

# 3. Enrich metadata
for i, chunk in enumerate(chunks):
    chunk.metadata['chunk_id'] = i
    chunk.metadata['chunk_size'] = len(chunk.page_content)

# 4. Embed and store
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="my_knowledge_base"
)

print(f"Stored {len(chunks)} chunks")
```

## Performance Considerations

### Processing Speed

| Strategy | Speed | When to Use |
|----------|-------|-------------|
| Fixed-size | Fastest | Real-time processing |
| Recursive character | Fast | Default choice |
| Document structure | Medium | Structured content |
| Semantic | Slowest | Quality-critical applications |

### Memory Usage

- **Streaming for large documents:**
```python
def chunk_large_file(file_path, chunk_size=300):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=50
    )
    
    # Process in batches to avoid memory issues
    with open(file_path, 'r') as f:
        for line_batch in read_in_batches(f, batch_size=10000):
            chunks = splitter.split_text(line_batch)
            yield from chunks
```

## Cost Optimization

**Embedding costs scale with number of chunks:**

```
Cost = (num_chunks × tokens_per_chunk) × embedding_price_per_token
```

**Example:**
- 1,000 documents
- 500 tokens each (before chunking)
- 300 token chunks with 50 overlap
- ~1.7 chunks per document
- 1,700 chunks × 300 tokens = 510,000 tokens
- OpenAI embedding: $0.00002 per 1K tokens
- **Total: $0.01 (very cheap)**

**Optimization tips:**
- Don't chunk too small (creates many chunks)
- Use appropriate overlap (10-20%, not 50%)
- Cache embeddings when possible
- Batch embedding requests

## Next Steps

- For vector database optimization, see `vector-databases.md`
- For retrieval strategies, see `agentic-retrieval.md`
- For complete pipeline integration, see `integration-patterns.md`
