#!/usr/bin/env python3
"""
Semantic deduplication for research papers using embeddings.

Uses sentence-transformers for local embedding, falls back to simple TF-IDF
if not available.
"""

import json
import re
from pathlib import Path

# Try to import ML libraries, fall back to simple approach
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        HAS_SKLEARN = True
    except ImportError:
        HAS_SKLEARN = False


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def get_paper_text(paper: dict) -> str:
    """Extract text representation of paper for embedding."""
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    authors = " ".join(paper.get("authors", []))
    return f"{title} {abstract} {authors}"


def semantic_dedupe_transformers(papers: list[dict], similarity_threshold: float = 0.85) -> list[dict]:
    """
    Deduplicate using sentence-transformers embeddings.
    Groups similar papers, keeps highest-scored from each group.
    """
    if not papers:
        return []
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate embeddings
    texts = [get_paper_text(p) for p in papers]
    embeddings = model.encode(texts, convert_to_numpy=True)
    
    # Compute similarity matrix
    similarity_matrix = np.dot(embeddings, embeddings.T)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    similarity_matrix = similarity_matrix / (norms @ norms.T + 1e-8)
    
    # Cluster similar papers
    n = len(papers)
    visited = [False] * n
    clusters = []
    
    for i in range(n):
        if visited[i]:
            continue
        cluster = [i]
        visited[i] = True
        for j in range(i + 1, n):
            if not visited[j] and similarity_matrix[i, j] >= similarity_threshold:
                cluster.append(j)
                visited[j] = True
        clusters.append(cluster)
    
    # Keep best paper from each cluster
    def score_paper(p):
        citations = p.get("citations", 0) or 0
        year = p.get("year", 2000) or 2000
        return citations * 0.3 + (year - 2000) * 2
    
    deduped = []
    for cluster in clusters:
        cluster_papers = [papers[i] for i in cluster]
        best = max(cluster_papers, key=score_paper)
        if len(cluster) > 1:
            best["_merged_from"] = len(cluster)
            best["_similar_titles"] = [papers[i]["title"] for i in cluster if papers[i]["title"] != best["title"]]
        deduped.append(best)
    
    return deduped


def semantic_dedupe_tfidf(papers: list[dict], similarity_threshold: float = 0.7) -> list[dict]:
    """
    Fallback deduplication using TF-IDF vectors.
    Lower threshold than transformers (TF-IDF less semantic).
    """
    if not papers:
        return []
    
    texts = [get_paper_text(p) for p in papers]
    
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(texts)
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Same clustering logic
    n = len(papers)
    visited = [False] * n
    clusters = []
    
    for i in range(n):
        if visited[i]:
            continue
        cluster = [i]
        visited[i] = True
        for j in range(i + 1, n):
            if not visited[j] and similarity_matrix[i, j] >= similarity_threshold:
                cluster.append(j)
                visited[j] = True
        clusters.append(cluster)
    
    def score_paper(p):
        citations = p.get("citations", 0) or 0
        year = p.get("year", 2000) or 2000
        return citations * 0.3 + (year - 2000) * 2
    
    deduped = []
    for cluster in clusters:
        cluster_papers = [papers[i] for i in cluster]
        best = max(cluster_papers, key=score_paper)
        if len(cluster) > 1:
            best["_merged_from"] = len(cluster)
        deduped.append(best)
    
    return deduped


def semantic_dedupe_simple(papers: list[dict]) -> list[dict]:
    """
    Simplest fallback: normalized title matching with fuzzy tolerance.
    """
    if not papers:
        return []
    
    def title_key(title: str) -> str:
        normalized = normalize_text(title)
        words = sorted(normalized.split())
        return " ".join(words[:8])  # First 8 words, sorted
    
    seen = {}
    for paper in papers:
        key = title_key(paper.get("title", ""))
        if key not in seen:
            seen[key] = paper
        else:
            # Keep higher-scored version
            existing = seen[key]
            existing_score = (existing.get("citations", 0) or 0) * 0.3 + ((existing.get("year", 2000) or 2000) - 2000) * 2
            new_score = (paper.get("citations", 0) or 0) * 0.3 + ((paper.get("year", 2000) or 2000) - 2000) * 2
            if new_score > existing_score:
                seen[key] = paper
    
    return list(seen.values())


def semantic_dedupe(papers: list[dict], similarity_threshold: float = None) -> tuple[list[dict], str]:
    """
    Main entry point. Tries best available method.
    Returns (deduped_papers, method_used).
    """
    if HAS_TRANSFORMERS:
        threshold = similarity_threshold or 0.85
        return semantic_dedupe_transformers(papers, threshold), "sentence-transformers"
    elif HAS_SKLEARN:
        threshold = similarity_threshold or 0.7
        return semantic_dedupe_tfidf(papers, threshold), "tfidf"
    else:
        return semantic_dedupe_simple(papers), "title-matching"


def dedupe_and_rank(search_results: list[dict], max_papers: int = 10) -> tuple[list[dict], dict]:
    """
    Full deduplication pipeline with stats.
    
    Returns:
        (ranked_papers, stats_dict)
    """
    # Flatten all papers
    all_papers = []
    for result in search_results:
        for paper in result.get("papers", []):
            paper["_source"] = result.get("source", "unknown")
            all_papers.append(paper)
    
    initial_count = len(all_papers)
    
    # Semantic deduplication
    deduped, method = semantic_dedupe(all_papers)
    
    # Rank by quality signals
    source_weight = {
        "nber": 1.2, "fed": 1.2, "bis": 1.1,
        "ssrn": 1.0, "arxiv": 1.0,
        "google_scholar": 0.9, "semantic_scholar": 0.9
    }
    
    def score(p):
        citations = p.get("citations", 0) or 0
        year = p.get("year", 2000) or 2000
        src_weight = source_weight.get(p.get("_source", ""), 1.0)
        return (citations * 0.3 + (year - 2000) * 2) * src_weight
    
    deduped.sort(key=score, reverse=True)
    ranked = deduped[:max_papers]
    
    stats = {
        "initial_count": initial_count,
        "after_dedupe": len(deduped),
        "duplicates_removed": initial_count - len(deduped),
        "final_count": len(ranked),
        "method": method
    }
    
    return ranked, stats


if __name__ == "__main__":
    # Test with sample data
    test_papers = [
        {"title": "ESG and Credit Risk: A Study", "abstract": "We examine ESG factors...", "citations": 50, "year": 2022},
        {"title": "ESG and Credit Risk - A Study", "abstract": "This paper examines ESG...", "citations": 45, "year": 2021},
        {"title": "Climate Risk in Banking", "abstract": "Climate change affects banks...", "citations": 100, "year": 2023},
    ]
    
    deduped, stats = dedupe_and_rank([{"papers": test_papers, "source": "test"}], max_papers=5)
    print(f"Stats: {stats}")
    print(f"Deduped papers: {[p['title'] for p in deduped]}")
