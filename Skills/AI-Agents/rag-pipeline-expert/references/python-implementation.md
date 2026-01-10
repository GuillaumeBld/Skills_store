# Python RAG Implementation

Production-ready FastAPI RAG application template.

## Complete FastAPI Application

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

app = FastAPI(title="RAG API")

# Initialize components
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings,
    collection_name="documents"
)
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Create QA chain
prompt_template = """Use the following context to answer the question.
If you cannot answer based on the context, say so.

Context: {context}

Question: {question}

Answer:"""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    chain_type_kwargs={"prompt": PROMPT},
    return_source_documents=True
)

# Request/Response models
class QueryRequest(BaseModel):
    question: str
    filters: Optional[dict] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

class DocumentRequest(BaseModel):
    content: str
    metadata: dict

# Endpoints
@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the RAG system"""
    try:
        result = qa_chain({"query": request.question})
        
        sources = [
            {
                "content": doc.page_content[:200],
                "metadata": doc.metadata
            }
            for doc in result['source_documents']
        ]
        
        return QueryResponse(
            answer=result['result'],
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index")
async def index_document(doc: DocumentRequest):
    """Add document to vector store"""
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.create_documents(
            texts=[doc.content],
            metadatas=[doc.metadata]
        )
        
        vectorstore.add_documents(chunks)
        
        return {"status": "success", "chunks_added": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  rag-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./chroma_db:/app/chroma_db
    depends_on:
      - qdrant
  
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  qdrant_data:
```

```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
langchain==0.1.0
langchain-openai==0.0.2
langchain-community==0.0.10
chromadb==0.4.18
pydantic==2.5.0
python-dotenv==1.0.0
```

## Advanced: Multi-Agent System

```python
# agents.py
from crewai import Agent, Task, Crew, Process
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient

# Initialize vector store
client = QdrantClient(host="localhost", port=6333)
vectorstore = Qdrant(
    client=client,
    collection_name="documents",
    embeddings=OpenAIEmbeddings()
)

# Define agents
researcher = Agent(
    role='Research Specialist',
    goal='Find relevant information from the knowledge base',
    backstory='Expert at searching and retrieving relevant documents',
    tools=[vectorstore.as_retriever_tool()]
)

analyst = Agent(
    role='Data Analyst',
    goal='Analyze and synthesize information',
    backstory='Skilled at extracting insights from multiple sources'
)

writer = Agent(
    role='Content Writer',
    goal='Create clear, comprehensive responses',
    backstory='Expert at explaining complex topics simply'
)

# Define workflow
def create_research_crew(question: str):
    research_task = Task(
        description=f'Research: {question}',
        agent=researcher,
        expected_output='Relevant documents and information'
    )
    
    analysis_task = Task(
        description='Analyze the research findings',
        agent=analyst,
        expected_output='Key insights and patterns'
    )
    
    writing_task = Task(
        description='Write comprehensive answer',
        agent=writer,
        expected_output='Clear, detailed response with citations'
    )
    
    crew = Crew(
        agents=[researcher, analyst, writer],
        tasks=[research_task, analysis_task, writing_task],
        process=Process.sequential
    )
    
    return crew

# Use in FastAPI
@app.post("/research")
async def research(question: str):
    crew = create_research_crew(question)
    result = crew.kickoff()
    return {"answer": result}
```

## Monitoring & Logging

```python
# monitoring.py
from prometheus_client import Counter, Histogram
import time
import logging

# Metrics
query_counter = Counter('rag_queries_total', 'Total queries')
query_duration = Histogram('rag_query_duration_seconds', 'Query duration')
error_counter = Counter('rag_errors_total', 'Total errors')

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitored_query(func):
    """Decorator for monitoring queries"""
    def wrapper(*args, **kwargs):
        query_counter.inc()
        start = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            query_duration.observe(duration)
            
            logger.info(f"Query completed in {duration:.2f}s")
            return result
        except Exception as e:
            error_counter.inc()
            logger.error(f"Query failed: {e}")
            raise
    
    return wrapper
```

## Testing

```python
# test_rag.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_query():
    response = client.post(
        "/query",
        json={"question": "What is RAG?"}
    )
    assert response.status_code == 200
    assert "answer" in response.json()

def test_index():
    response = client.post(
        "/index",
        json={
            "content": "RAG stands for Retrieval Augmented Generation",
            "metadata": {"source": "test"}
        }
    )
    assert response.status_code == 200
```

## Deployment (Railway/Render)

```yaml
# railway.toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

