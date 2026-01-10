# n8n RAG Integration Guide

Complete n8n workflow patterns for RAG pipelines.

## Basic RAG Workflow

```json
{
  "name": "Basic RAG Pipeline",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "query",
        "responseMode": "responseNode",
        "options": {}
      },
      "id": "webhook",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook"
    },
    {
      "parameters": {
        "operation": "search",
        "qdrantCollection": "documents",
        "query": "={{ $json.body.question }}",
        "limit": 5
      },
      "id": "qdrant_search",
      "name": "Qdrant Vector Search",
      "type": "@n8n/n8n-nodes-qdrant.qdrant"
    },
    {
      "parameters": {
        "jsCode": "const context = $input.all().map(item => item.json.payload).join('\\n\\n');\nconst question = $('Webhook').first().json.body.question;\n\nreturn { context, question };"
      },
      "id": "prepare_context",
      "name": "Prepare Context",
      "type": "n8n-nodes-base.code"
    },
    {
      "parameters": {
        "resource": "chat",
        "operation": "create",
        "modelId": "gpt-4",
        "messages": {
          "values": [
            {
              "role": "system",
              "content": "Answer based only on the provided context."
            },
            {
              "role": "user",
              "content": "=Context: {{ $json.context }}\\n\\nQuestion: {{ $json.question }}"
            }
          ]
        }
      },
      "id": "openai",
      "name": "OpenAI Chat",
      "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi"
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { answer: $json.choices[0].message.content } }}"
      },
      "id": "respond",
      "name": "Respond to Webhook",
      "type": "n8n-nodes-base.respondToWebhook"
    }
  ],
  "connections": {
    "Webhook": { "main": [[{ "node": "Qdrant Vector Search" }]] },
    "Qdrant Vector Search": { "main": [[{ "node": "Prepare Context" }]] },
    "Prepare Context": { "main": [[{ "node": "OpenAI Chat" }]] },
    "OpenAI Chat": { "main": [[{ "node": "Respond to Webhook" }]] }
  }
}
```

## Web Scraping + Indexing Workflow

```json
{
  "name": "Scrape and Index",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [{"field": "cronExpression", "expression": "0 0 * * *"}]
        }
      },
      "name": "Schedule",
      "type": "n8n-nodes-base.scheduleTrigger"
    },
    {
      "parameters": {
        "url": "={{ $json.url }}",
        "options": {
          "response": {"response": {"fullResponse": false}}
        }
      },
      "name": "Fetch Page",
      "type": "n8n-nodes-base.httpRequest"
    },
    {
      "parameters": {
        "jsCode": "const html = $input.first().json.data;\nconst TurndownService = require('turndown');\nconst turndown = new TurndownService();\n\nconst markdown = turndown.turndown(html);\n\nreturn { markdown, url: $input.first().json.url };"
      },
      "name": "HTML to Markdown",
      "type": "n8n-nodes-base.code"
    },
    {
      "parameters": {
        "operation": "chunk",
        "text": "={{ $json.markdown }}",
        "chunkSize": 1000,
        "chunkOverlap": 200
      },
      "name": "Chunk Text",
      "type": "n8n-nodes-base.code"
    },
    {
      "parameters": {
        "operation": "embed",
        "model": "text-embedding-3-small",
        "input": "={{ $json.chunk }}"
      },
      "name": "Create Embeddings",
      "type": "@n8n/n8n-nodes-langchain.openAiEmbedding"
    },
    {
      "parameters": {
        "operation": "upsert",
        "collection": "documents",
        "points": "={{ [{id: $json.id, vector: $json.embedding, payload: {text: $json.chunk, url: $json.url}}] }}"
      },
      "name": "Store in Qdrant",
      "type": "@n8n/n8n-nodes-qdrant.qdrant"
    }
  ]
}
```

## CrewAI Integration

```json
{
  "name": "Multi-Agent RAG",
  "nodes": [
    {
      "parameters": {
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "method": "POST",
        "url": "http://localhost:8000/crew/kickoff",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "query",
              "value": "={{ $json.query }}"
            },
            {
              "name": "crew_type",
              "value": "research"
            }
          ]
        },
        "options": {}
      },
      "name": "CrewAI API",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

## Supabase Vector Storage

```json
{
  "name": "Supabase RAG",
  "nodes": [
    {
      "parameters": {
        "operation": "select",
        "table": "documents",
        "returnAll": false,
        "limit": 5,
        "additionalFields": {
          "rpc": {
            "function": "match_documents",
            "parameters": {
              "query_embedding": "={{ $json.embedding }}",
              "match_count": 5
            }
          }
        }
      },
      "name": "Vector Search",
      "type": "@n8n/n8n-nodes-supabase.supabase"
    }
  ]
}
```

## Error Handling Pattern

```json
{
  "nodes": [
    {
      "parameters": {},
      "name": "Try",
      "type": "n8n-nodes-base.errorTrigger"
    },
    {
      "parameters": {
        "operation": "insert",
        "table": "error_logs",
        "columns": "error_message, workflow_id, timestamp"
      },
      "name": "Log Error",
      "type": "@n8n/n8n-nodes-supabase.supabase"
    },
    {
      "parameters": {
        "channel": "#alerts",
        "text": "RAG Pipeline Error: {{ $json.error }}"
      },
      "name": "Slack Alert",
      "type": "n8n-nodes-base.slack"
    }
  ]
}
```

## Complete Production Workflow

Combines: Scraping + Chunking + Embedding + Indexing + Querying + Monitoring

```json
{
  "name": "Production RAG System",
  "meta": {
    "templateCredsSetupCompleted": true
  },
  "nodes": [
    {"id": "trigger", "type": "schedule"},
    {"id": "fetch_urls", "type": "code"},
    {"id": "http_request", "type": "httpRequest"},
    {"id": "html_to_md", "type": "code"},
    {"id": "chunk", "type": "code"},
    {"id": "embed", "type": "openai"},
    {"id": "upsert_qdrant", "type": "qdrant"},
    {"id": "log_metrics", "type": "supabase"},
    {"id": "error_handler", "type": "errorTrigger"}
  ]
}
```

## Tips & Best Practices

1. **Use Credentials**: Store API keys in n8n credentials
2. **Batch Processing**: Process multiple items in single node when possible
3. **Error Handling**: Always add error trigger nodes
4. **Monitoring**: Log to Supabase or other DB for tracking
5. **Rate Limiting**: Add delay nodes between API calls
6. **Caching**: Store frequently accessed data in n8n static data
7. **Testing**: Use manual trigger for development
