# RAG Architecture Patterns

Complete system architectures for common RAG use cases.

## Pattern 1: Documentation RAG System

**Use Case**: Technical documentation, API references, help centers

### Architecture

```
Documentation Sources (Markdown/HTML)
    ↓
Recursive Web Scraper (respects structure)
    ↓
Document Structure Chunker (preserve sections)
    ↓
OpenAI Embeddings (text-embedding-3-small)
    ↓
Qdrant Vector DB (with metadata filtering)
    ↓
LlamaIndex Query Engine
    ↓
GPT-4 with citations
```

### Implementation

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from qdrant_client import QdrantClient
import qdrant_client

# Initialize Qdrant
client = QdrantClient(host="localhost", port=6333)

# Create vector store
vector_store = QdrantVectorStore(
    client=client,
    collection_name="documentation"
)

# Load and chunk documents
documents = SimpleDirectoryReader(
    input_dir="./docs",
    recursive=True
).load_data()

# Create index
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    embed_model=OpenAIEmbedding(model="text-embedding-3-small")
)

# Query with metadata filter
query_engine = index.as_query_engine(
    similarity_top_k=5,
    filters={"version": "latest"}
)

response = query_engine.query("How do I authenticate API requests?")
```

**Key Features**:
- Version filtering (multiple doc versions)
- Section-aware retrieval
- Code snippet highlighting
- Citation back to source

---

## Pattern 2: News Aggregation RAG

**Use Case**: News monitoring, competitive intelligence, trend analysis

### Architecture

```
RSS Feeds + Web Scraping
    ↓
Scheduled Crawls (Apify/Custom)
    ↓
Fixed-Size Chunking (consistent article structure)
    ↓
Sentence Transformers Embeddings (local/fast)
    ↓
Pinecone (with temporal metadata)
    ↓
CrewAI Agents (researcher + summarizer + analyst)
    ↓
Claude with hybrid search (keyword + semantic)
```

### Implementation

```python
from crewai import Agent, Task, Crew, Process
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings

# Initialize vector store
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = PineconeVectorStore(
    index_name="news-articles",
    embedding=embeddings
)

# Define agents
researcher = Agent(
    role='News Researcher',
    goal='Find relevant news articles on {topic}',
    backstory='Expert at finding and filtering relevant news',
    tools=[vectorstore.as_retriever(search_kwargs={"k": 10})]
)

analyst = Agent(
    role='News Analyst',
    goal='Analyze trends and extract insights from news',
    backstory='Experienced analyst who identifies patterns and trends'
)

# Define tasks
research_task = Task(
    description='Research recent news about {topic} from last 7 days',
    agent=researcher,
    expected_output='List of 10 most relevant articles'
)

analysis_task = Task(
    description='Analyze the articles and identify key trends',
    agent=analyst,
    expected_output='Summary of key trends with supporting evidence'
)

# Create crew
crew = Crew(
    agents=[researcher, analyst],
    tasks=[research_task, analysis_task],
    process=Process.sequential
)

# Run
result = crew.kickoff(inputs={'topic': 'artificial intelligence regulation'})
```

**Key Features**:
- Time-based filtering (last N days)
- Source diversity (multiple news outlets)
- Trend detection
- Sentiment analysis
- Duplicate detection

---

## Pattern 3: Enterprise Knowledge Base

**Use Case**: Internal wikis, Confluence, Slack, Google Drive

### Architecture

```
Multiple Sources (Confluence, Slack, Drive)
    ↓
Source-Specific Connectors
    ↓
Semantic Chunking (diverse content types)
    ↓
Instructor Embeddings (instruction-tuned)
    ↓
Weaviate (hybrid search + ACL)
    ↓
LangGraph Multi-Agent System
    ↓
GPT-4 with source attribution
```

### Implementation

```python
from langgraph.graph import Graph, StateGraph
from langchain_weaviate import WeaviateVectorStore
from langchain_community.document_loaders import (
    ConfluenceLoader,
    SlackDirectoryLoader,
    GoogleDriveLoader
)

# Load from multiple sources
confluence_docs = ConfluenceLoader(
    url="https://company.atlassian.net/wiki",
    username=os.getenv("CONFLUENCE_USER"),
    api_key=os.getenv("CONFLUENCE_API_KEY")
).load()

slack_docs = SlackDirectoryLoader(
    zip_path="./slack_export.zip"
).load()

drive_docs = GoogleDriveLoader(
    folder_id="folder_id_here",
    token_path="./token.json"
).load()

# Combine and enrich metadata
all_docs = confluence_docs + slack_docs + drive_docs
for doc in all_docs:
    doc.metadata['indexed_at'] = datetime.now().isoformat()

# Create vector store with ACL
vectorstore = WeaviateVectorStore.from_documents(
    documents=all_docs,
    embedding=InstructorEmbeddings(),
    client=weaviate_client,
    index_name="KnowledgeBase"
)

# Define graph workflow
class State(TypedDict):
    query: str
    source_filter: Optional[str]
    results: List[Document]
    answer: str

def route_query(state: State) -> str:
    """Determine which source to search based on query"""
    query = state['query'].lower()
    
    if any(word in query for word in ['wiki', 'confluence', 'documented']):
        return "confluence_search"
    elif any(word in query for word in ['discussed', 'chat', 'slack']):
        return "slack_search"
    elif any(word in query for word in ['document', 'file', 'spreadsheet']):
        return "drive_search"
    else:
        return "all_search"

# Create graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("confluence_search", lambda s: {...})
workflow.add_node("slack_search", lambda s: {...})
workflow.add_node("drive_search", lambda s: {...})
workflow.add_node("all_search", lambda s: {...})
workflow.add_node("synthesize", lambda s: {...})

# Add conditional edges
workflow.set_conditional_entry_point(route_query)
workflow.add_edge("confluence_search", "synthesize")
workflow.add_edge("slack_search", "synthesize")
workflow.add_edge("drive_search", "synthesize")
workflow.add_edge("all_search", "synthesize")

# Compile
app = workflow.compile()

# Run
result = app.invoke({"query": "What was discussed about Q3 metrics?"})
```

**Key Features**:
- Source-aware routing
- Permission-aware retrieval
- Cross-source synthesis
- Freshness ranking
- User context awareness

---

## Pattern 4: Research Assistant

**Use Case**: Academic papers, scientific research, deep analysis

### Architecture

```
ArXiv + PubMed + Web Search
    ↓
PDF Extraction + Web Scraping
    ↓
Large Chunks (400-500 tokens, 20% overlap)
    ↓
Scientific BERT Embeddings
    ↓
Zilliz Cloud (GPU-accelerated)
    ↓
AutoGen Multi-Agent (Chain-of-Thought)
    ↓
GPT-4 with step-by-step reasoning
```

### Implementation

```python
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from langchain_community.document_loaders import ArxivLoader, PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load research papers
arxiv_loader = ArxivLoader(query="machine learning", load_max_docs=50)
papers = arxiv_loader.load()

# Specialized embeddings
embeddings = HuggingFaceEmbeddings(model_name="allenai/scibert_scivocab_uncased")

# Large chunks for research
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,  # ~500 tokens
    chunk_overlap=400
)
chunks = text_splitter.split_documents(papers)

# Define research agents
planner = AssistantAgent(
    name="Planner",
    system_message="""You are a research planner. Break down research questions 
    into specific sub-questions that need to be answered.""",
    llm_config={"config_list": [{"model": "gpt-4"}]}
)

researcher = AssistantAgent(
    name="Researcher",
    system_message="""You search and retrieve relevant papers and information.
    Use the vector store tool to find papers.""",
    llm_config={"config_list": [{"model": "gpt-4"}]}
)

critic = AssistantAgent(
    name="Critic",
    system_message="""You critically evaluate research findings, identify gaps,
    and suggest additional research directions.""",
    llm_config={"config_list": [{"model": "gpt-4"}]}
)

synthesizer = AssistantAgent(
    name="Synthesizer",
    system_message="""You synthesize findings from multiple sources into
    comprehensive research summaries with citations.""",
    llm_config={"config_list": [{"model": "gpt-4"}]}
)

# User proxy
user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=0,
    code_execution_config=False
)

# Create group chat
groupchat = GroupChat(
    agents=[planner, researcher, critic, synthesizer, user_proxy],
    messages=[],
    max_round=20
)

manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": [{"model": "gpt-4"}]})

# Initiate research
user_proxy.initiate_chat(
    manager,
    message="Research the latest advances in transformer architectures for vision tasks"
)
```

**Key Features**:
- Multi-step reasoning
- Citation tracking
- Cross-reference validation
- Iterative refinement
- Comprehensive summaries

---

## Pattern 5: Customer Support RAG

**Use Case**: Support tickets, FAQs, troubleshooting guides

### Architecture

```
Support Docs + Ticket History
    ↓
Mixed Chunking (FAQ=small, guides=medium)
    ↓
FastEmbed (super fast, local)
    ↓
ChromaDB (simple, fast)
    ↓
LangChain RetrievalQA with history
    ↓
GPT-3.5-turbo (cost-effective)
```

### Implementation

```python
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory

# Fast local embeddings
embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

# Load support content
faq_docs = load_faqs()  # Small chunks
guides = load_guides()  # Medium chunks

# Create vector store
vectorstore = Chroma.from_documents(
    documents=faq_docs + guides,
    embedding=embeddings,
    persist_directory="./support_db"
)

# Create conversational chain
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key='answer'
)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    memory=memory,
    return_source_documents=True,
    verbose=True
)

# Use with conversation history
response = qa_chain({"question": "How do I reset my password?"})
print(response['answer'])

# Follow-up
response = qa_chain({"question": "What if that doesn't work?"})
```

**Key Features**:
- Conversation memory
- Fast response times (<2s)
- Cost-effective (GPT-3.5)
- Source citation
- Escalation detection

---

## Hybrid Approaches

### Pattern: n8n Orchestration + Python Processing

```
n8n Workflow (Orchestration)
    ↓
Trigger: Webhook/Schedule/Manual
    ↓
n8n HTTP Node: Fetch content
    ↓
n8n Code Node: Call Python FastAPI service
    ↓
Python Service: Chunk + Embed + Store
    ↓
n8n Supabase Node: Store metadata
    ↓
n8n Notification: Slack/Email
```

**When to use**: Best of both worlds - visual workflow + powerful processing

---

## Deployment Patterns

### Local Development

```
Docker Compose:
- ChromaDB (vector store)
- FastAPI (API)
- Streamlit (UI)

Advantages: Fast iteration, no costs
```

### Production (Cloud)

```
Infrastructure:
- Pinecone/Qdrant Cloud (vectors)
- Vercel/Railway (API)
- Cloudflare Workers (edge cache)

Advantages: Scalable, managed
```

### Hybrid (Best of Both)

```
- Local processing for dev/test
- Cloud vectors for production
- n8n Cloud for orchestration
- Supabase for metadata

Advantages: Flexible, cost-effective
```

---

## Cost Optimization Patterns

### Pattern: Tiered Retrieval

```python
# Tier 1: Local cache (instant, free)
cached_result = cache.get(query_hash)
if cached_result:
    return cached_result

# Tier 2: Keyword search (fast, cheap)
keyword_results = bm25_index.search(query)
if is_confident(keyword_results):
    return keyword_results

# Tier 3: Vector search (slower, more expensive)
vector_results = vectorstore.similarity_search(query)
return vector_results
```

### Pattern: Batch Processing

```python
# Bad: One-by-one
for doc in documents:
    embedding = embed_model.embed_query(doc.page_content)
    vectorstore.add_embedding(embedding)

# Good: Batched
texts = [doc.page_content for doc in documents]
embeddings = embed_model.embed_documents(texts)  # Batch API call
vectorstore.add_embeddings(embeddings)
```

## Monitoring & Observability

All patterns should include:

1. **Performance Metrics**: Latency, throughput, cost per query
2. **Quality Metrics**: Retrieval accuracy, response relevance
3. **Usage Metrics**: Popular queries, user satisfaction
4. **System Health**: Error rates, API quotas, storage usage

Example with LangSmith:

```python
from langsmith import Client

client = Client()

# Trace entire RAG pipeline
with client.trace("rag_query", project_name="production") as trace:
    # Your RAG code here
    pass
```
