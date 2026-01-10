# Agentic Retrieval for RAG

Advanced AI agent patterns for intelligent information retrieval beyond basic vector search.

## When to Use Agents

**Use basic vector search when:**
- Simple lookup queries
- Single knowledge source
- Fast response critical
- Limited budget

**Use agentic retrieval when:**
- Complex multi-step queries
- Multiple knowledge sources needed
- Query disambiguation required
- High precision important

## Framework Selection

| Framework | Best For | Complexity | Learning Curve |
|-----------|---------|------------|----------------|
| **LlamaIndex** | Data-heavy RAG, index management | Medium | Low |
| **LangChain** | General purpose, tool integration | Medium | Medium |
| **CrewAI** | Role-based workflows, n8n-friendly | Low | Low |
| **AutoGen** | Conversational agents, code generation | Medium | Medium |
| **LangGraph** | Complex state management, DAGs | High | High |

## Agentic Patterns

### Pattern 1: Router Agent

**Use:** Direct queries to appropriate knowledge sources

```python
from langchain.agents import AgentExecutor
from langchain.agents import create_openai_functions_agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4", temperature=0)

tools = [
    {"name": "vector_search", "description": "Search documentation"},
    {"name": "web_search", "description": "Search current web"},
    {"name": "sql_query", "description": "Query database"}
]

agent = create_openai_functions_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

result = executor.invoke({"input": "Latest pricing for product X"})
```

### Pattern 2: Multi-Agent RAG (CrewAI)

**Use:** Complex queries requiring specialized agents

```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Web Researcher",
    goal="Find latest information",
    tools=[web_search_tool],
    verbose=True
)

retriever = Agent(
    role="Knowledge Base Retriever", 
    goal="Search internal documentation",
    tools=[vector_search_tool],
    verbose=True
)

synthesizer = Agent(
    role="Information Synthesizer",
    goal="Combine findings into coherent answer",
    tools=[],
    verbose=True
)

task = Task(
    description="Research competitive pricing and our current offers",
    expected_output="Comprehensive comparison",
    agents=[researcher, retriever, synthesizer]
)

crew = Crew(agents=[researcher, retriever, synthesizer], tasks=[task])
result = crew.kickoff()
```

### Pattern 3: Self-RAG (Self-Correcting)

**Use:** High-stakes queries requiring validation

```python
def self_rag_retrieval(query):
    # 1. Initial retrieval
    initial_results = vector_store.similarity_search(query, k=10)
    
    # 2. Self-critique: Are results relevant?
    relevance_scores = llm.evaluate_relevance(query, initial_results)
    
    # 3. If low relevance, reformulate query
    if max(relevance_scores) < 0.7:
        reformulated = llm.reformulate_query(query)
        results = vector_store.similarity_search(reformulated, k=10)
    else:
        results = initial_results
    
    # 4. Generate answer
    answer = llm.generate_answer(query, results)
    
    # 5. Self-check: Does answer address query?
    if not llm.validate_answer(query, answer):
        # Retrieve more context or admit uncertainty
        return "I need more information to answer accurately."
    
    return answer
```

### Pattern 4: HyDE (Hypothetical Document Embeddings)

**Use:** When query phrasing doesn't match document phrasing

```python
def hyde_retrieval(query):
    # 1. Generate hypothetical answer
    hypothetical_doc = llm.generate(f"Write a detailed answer to: {query}")
    
    # 2. Embed hypothetical answer (not the query)
    hyp_embedding = embeddings.embed_query(hypothetical_doc)
    
    # 3. Search with hypothetical embedding
    results = vector_store.similarity_search_by_vector(hyp_embedding, k=5)
    
    # 4. Generate actual answer from retrieved docs
    return llm.generate_final_answer(query, results)
```

**Why it works:** Hypothetical answers use similar language to actual documents

## Advanced Techniques

### 1. Reranking

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank

base_retriever = vector_store.as_retriever(search_kwargs={"k": 20})

reranker = CohereRerank(model="rerank-english-v2.0", top_n=5)

retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=base_retriever
)

results = retriever.get_relevant_documents(query)
```

**Impact:** 20-40% improvement in precision

### 2. Query Expansion

```python
def expand_query(original_query):
    expansions = llm.generate(
        f"Generate 3 alternative phrasings of: {original_query}"
    ).split("\n")
    
    all_results = []
    for query_variant in [original_query] + expansions:
        results = vector_store.similarity_search(query_variant, k=3)
        all_results.extend(results)
    
    # Deduplicate and rerank
    unique_results = deduplicate_by_content(all_results)
    return unique_results[:5]
```

### 3. Hierarchical Retrieval

```python
from langchain.retrievers import ParentDocumentRetriever

# Small chunks for search, large chunks for context
child_splitter = RecursiveCharacterTextSplitter(chunk_size=200)
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)

retriever = ParentDocumentRetriever(
    vectorstore=vector_store,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter
)

# Searches with 200-token chunks, returns 1000-token context
results = retriever.get_relevant_documents(query)
```

## Memory Management

### Conversation History

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Store context across turns
memory.save_context(
    {"input": "What's our refund policy?"},
    {"output": "30-day money-back guarantee..."}
)

# Use in next query
agent = create_agent_with_memory(llm, tools, memory)
```

### Entity Memory

```python
from langchain.memory import ConversationEntityMemory

entity_memory = ConversationEntityMemory(llm=llm)

# Tracks entities mentioned (products, people, places)
entity_memory.save_context(
    {"input": "Tell me about ProductX pricing"},
    {"output": "ProductX costs $99/month"}
)

# Later queries can reference "the product we discussed"
```

## Evaluation & Monitoring

### Retrieval Quality Metrics

```python
def evaluate_retrieval(test_queries):
    metrics = {
        'recall_at_5': [],
        'precision_at_5': [],
        'mrr': [],
        'latency': []
    }
    
    for query, expected_doc_ids in test_queries:
        start = time.time()
        results = retriever.get_relevant_documents(query)
        latency = time.time() - start
        
        retrieved_ids = [r.metadata['id'] for r in results[:5]]
        
        # Recall@5
        relevant_retrieved = len(set(retrieved_ids) & set(expected_doc_ids))
        recall = relevant_retrieved / len(expected_doc_ids)
        
        # Precision@5
        precision = relevant_retrieved / 5
        
        # MRR
        for i, doc_id in enumerate(retrieved_ids, 1):
            if doc_id in expected_doc_ids:
                mrr = 1 / i
                break
        else:
            mrr = 0
        
        metrics['recall_at_5'].append(recall)
        metrics['precision_at_5'].append(precision)
        metrics['mrr'].append(mrr)
        metrics['latency'].append(latency)
    
    return {k: sum(v)/len(v) for k, v in metrics.items()}
```

**Targets:**
- Recall@5: >80%
- Precision@5: >70%
- MRR: >0.7
- Latency: <500ms

## Integration Patterns

### n8n Workflow

```
1. Webhook Trigger (receive query)
2. Code Node: Determine query type
3. Switch Node:
   ├─ Simple → Direct vector search
   ├─ Complex → Multi-agent crew
   └─ Ambiguous → Clarification request
4. Vector Search Node (Supabase/Qdrant)
5. OpenAI Node: Generate answer
6. Respond to Webhook
```

### FastAPI Production

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    text: str
    k: int = 5

@app.post("/search")
async def search(query: Query):
    # Agent-based retrieval
    results = await agent_executor.ainvoke({"input": query.text})
    
    return {
        "answer": results["output"],
        "sources": [r.metadata for r in results["source_documents"]],
        "confidence": results.get("confidence", 0.0)
    }
```

## Cost Optimization

| Technique | Cost Impact | Quality Impact |
|-----------|-------------|----------------|
| Basic vector search | Baseline | Baseline |
| + Query expansion | +200% (more searches) | +15% recall |
| + Reranking | +$1/1K queries | +30% precision |
| + Multi-agent | +300% (LLM calls) | +40% complex queries |
| + HyDE | +100% (extra generation) | +25% recall |

**Optimization strategies:**
1. Start with basic search
2. Add reranking for important queries
3. Use agents only for complex queries (route based on complexity)
4. Cache frequently asked questions

## Next Steps

- For scraping, see `web-scraping.md`
- For chunking, see `chunking-strategies.md`
- For vector storage, see `vector-databases.md`
- For full pipelines, see `integration-patterns.md`
