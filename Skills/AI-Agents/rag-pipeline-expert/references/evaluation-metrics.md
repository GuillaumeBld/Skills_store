# RAG Evaluation Metrics

## Retrieval Quality Metrics

### 1. Recall@K
**What**: Percentage of relevant documents retrieved in top-K results
**Formula**: (Relevant docs in top-K) / (Total relevant docs)
**Target**: >0.90 for K=10

```python
def recall_at_k(retrieved_docs, relevant_docs, k):
    top_k = retrieved_docs[:k]
    relevant_retrieved = set(top_k) & set(relevant_docs)
    return len(relevant_retrieved) / len(relevant_docs)
```

### 2. Precision@K
**What**: Percentage of retrieved documents that are relevant
**Formula**: (Relevant docs in top-K) / K
**Target**: >0.80

```python
def precision_at_k(retrieved_docs, relevant_docs, k):
    top_k = retrieved_docs[:k]
    relevant_retrieved = set(top_k) & set(relevant_docs)
    return len(relevant_retrieved) / k
```

### 3. Mean Reciprocal Rank (MRR)
**What**: Average of reciprocal ranks of first relevant document
**Formula**: Average(1 / rank_of_first_relevant)
**Target**: >0.70

```python
def mrr(queries_results, relevant_docs_per_query):
    reciprocal_ranks = []
    for i, results in enumerate(queries_results):
        relevant = relevant_docs_per_query[i]
        for rank, doc in enumerate(results, 1):
            if doc in relevant:
                reciprocal_ranks.append(1.0 / rank)
                break
    return sum(reciprocal_ranks) / len(queries_results)
```

### 4. NDCG (Normalized Discounted Cumulative Gain)
**What**: Ranking quality considering position and relevance
**Target**: >0.75

```python
import numpy as np

def ndcg_at_k(relevances, k):
    dcg = sum([rel / np.log2(idx + 2) for idx, rel in enumerate(relevances[:k])])
    ideal_rel = sorted(relevances, reverse=True)
    idcg = sum([rel / np.log2(idx + 2) for idx, rel in enumerate(ideal_rel[:k])])
    return dcg / idcg if idcg > 0 else 0
```

## Response Quality Metrics

### 1. Faithfulness (Groundedness)
**What**: Does response accurately reflect retrieved content?

```python
from langchain.evaluation import load_evaluator

evaluator = load_evaluator("criteria", criteria="faithfulness")

result = evaluator.evaluate_strings(
    prediction=generated_answer,
    input=query,
    reference=retrieved_context
)
```

### 2. Answer Relevance
**What**: Does response address the query?

```python
evaluator = load_evaluator("criteria", criteria="relevance")
score = evaluator.evaluate_strings(
    prediction=answer,
    input=query
)
```

### 3. Context Precision
**What**: Are retrieved chunks relevant to query?

```python
def context_precision(retrieved_chunks, query, llm):
    """LLM judges relevance of each chunk"""
    relevant_count = 0
    
    for chunk in retrieved_chunks:
        prompt = f"Is this context relevant to the query?\nQuery: {query}\nContext: {chunk}"
        response = llm.invoke(prompt)
        if "yes" in response.lower():
            relevant_count += 1
    
    return relevant_count / len(retrieved_chunks)
```

## Performance Metrics

### Latency Breakdown

```python
import time

class RAGMetrics:
    def __init__(self):
        self.metrics = {}
    
    def time_component(self, name):
        def decorator(func):
            def wrapper(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                self.metrics[name] = time.time() - start
                return result
            return wrapper
        return decorator

metrics = RAGMetrics()

@metrics.time_component("retrieval")
def retrieve(query):
    return vectorstore.similarity_search(query)

@metrics.time_component("generation")
def generate(query, context):
    return llm.invoke(f"{context}\n\nQuery: {query}")

# After RAG pipeline
print(metrics.metrics)
# {'retrieval': 0.234, 'generation': 1.567}
```

### Cost Tracking

```python
import tiktoken

def calculate_cost(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = len(encoding.encode(text))
    
    costs = {
        "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
    }
    
    return tokens * costs[model]["input"] / 1000
```

## Complete Evaluation Framework

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)

def evaluate_rag_system(test_dataset):
    """
    test_dataset format:
    {
        'question': [...],
        'answer': [...],
        'contexts': [[...]],  # retrieved chunks per question
        'ground_truths': [[...]]  # correct answers
    }
    """
    
    results = evaluate(
        test_dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ]
    )
    
    return results

# Usage
test_data = {
    'question': ["What is RAG?", "How to chunk text?"],
    'answer': [response1, response2],
    'contexts': [[chunk1, chunk2], [chunk3, chunk4]],
    'ground_truths': [["RAG combines retrieval..."], ["Text chunking..."]]
}

scores = evaluate_rag_system(test_data)
print(f"Faithfulness: {scores['faithfulness']}")
print(f"Answer Relevancy: {scores['answer_relevancy']}")
```

## A/B Testing

```python
import random

def ab_test_rag_systems(system_a, system_b, queries, sample_size=100):
    """Compare two RAG configurations"""
    
    results = {'A': [], 'B': []}
    
    for query in random.sample(queries, sample_size):
        # Randomly assign to A or B
        system = random.choice(['A', 'B'])
        
        if system == 'A':
            response = system_a.query(query)
            results['A'].append({
                'query': query,
                'response': response,
                'latency': response.metadata['latency'],
                'cost': response.metadata['cost']
            })
        else:
            response = system_b.query(query)
            results['B'].append({
                'query': query,
                'response': response,
                'latency': response.metadata['latency'],
                'cost': response.metadata['cost']
            })
    
    # Get human ratings
    ratings_a = get_human_ratings(results['A'])
    ratings_b = get_human_ratings(results['B'])
    
    print(f"System A avg rating: {np.mean(ratings_a)}")
    print(f"System B avg rating: {np.mean(ratings_b)}")
    
    # Statistical significance test
    from scipy import stats
    t_stat, p_value = stats.ttest_ind(ratings_a, ratings_b)
    print(f"P-value: {p_value}")
    print(f"Significant difference: {p_value < 0.05}")
```

## Monitoring Dashboard

```python
# Using Prometheus + Grafana pattern

from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
query_count = Counter('rag_queries_total', 'Total queries')
query_latency = Histogram('rag_query_latency_seconds', 'Query latency')
retrieval_quality = Gauge('rag_retrieval_quality', 'Retrieval quality score')

def monitored_rag_query(query):
    query_count.inc()
    
    start = time.time()
    
    # Retrieve
    chunks = vectorstore.similarity_search(query, k=5)
    
    # Generate
    response = llm.invoke(f"Context: {chunks}\n\nQuery: {query}")
    
    latency = time.time() - start
    query_latency.observe(latency)
    
    # Calculate quality (async)
    quality = evaluate_response_quality(query, response, chunks)
    retrieval_quality.set(quality)
    
    return response
```

## Target Benchmarks

| Metric | Target | World-Class |
|--------|--------|-------------|
| Recall@10 | >0.85 | >0.95 |
| Precision@5 | >0.75 | >0.90 |
| MRR | >0.65 | >0.80 |
| NDCG@10 | >0.70 | >0.85 |
| Latency (E2E) | <5s | <2s |
| Cost per query | <$0.05 | <$0.01 |
| User satisfaction | >4.0/5 | >4.5/5 |
