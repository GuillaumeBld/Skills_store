---
name: db-ingest
description: "Use this to ingest raw content (crawled pages, audio transcriptions, scraped posts) into Martinique_DB. Parses raw content, extracts structured entries, runs LightRAG entity extraction, and updates the vector index."
---

# Martinique_DB Ingest Pipeline

Process raw content from any source (web crawl, audio transcription, TikTok scrape) into structured Martinique_DB entries with entity relationships. This is the ETL layer of the DB.

## Ingest Sources

| Source | Tool | Output |
|---|---|---|
| Web pages | firecrawl / crawl4ai | Markdown text |
| YouTube / audio | yt-dlp + faster-whisper | Transcript text |
| TikTok content | TikTokDownloader | Caption + metadata |
| PDFs / archives | RAGFlow | Structured text |
| RSS feeds | RSSHub + TrendRadar | News items |

## Pipeline Steps

### Step 1 — Raw Content Staging
All raw content lands in `martinique_db/staging/<source>/<date>/`. Never write directly to `data/`.

### Step 2 — Language Detection & Cleaning
- Detect language: French / Creole / mixed
- Remove boilerplate (nav menus, ads, footers)
- Flag Creole text segments for lexicon extraction (potential slang additions to `forge/lexicon/martinique_slang.json`)

### Step 3 — Entity Extraction (LightRAG)
Run LightRAG on cleaned text to extract:
- Named entities: people, places, events, traditions, foods, plants, music genres
- Relationships: `bèlè → performed_in → Fort-de-France`, `Aimé Césaire → born_in → Martinique`
- Store graph in `martinique_db/graph/`

### Step 4 — Entry Structuring
Convert extracted entities + source text into DB entries following the cultural-research SKILL.md Entry Format. Assign:
- `category` based on content analysis
- `reliability` score (web = estimate, institutional = verified, Wikipedia = verified)
- `geo` from location mentions

### Step 5 — Vector Embedding
Embed each entry using Gemini Embedding 2 (or local fallback).
Store vectors in Chroma DB at `martinique_db/vectors/`.

### Step 6 — Quality Gate
Before moving from staging to `data/`:
- Entry has all required fields
- Content length ≥ 50 words
- At least 1 entity extracted
- Not a duplicate (check by title similarity > 0.9 against existing entries)

### Step 7 — Promote & Index
Move passing entries from `staging/` to `martinique_db/data/<category>/`.
Update `martinique_db/coverage.json`.
Log ingest stats: entries added, entities extracted, duplicates skipped.

## Creole Lexicon Side-Channel

During step 2, whenever a Creole expression is encountered in natural context:
- Extract: phrase, usage context, source
- Append candidate to `forge/lexicon/candidates.json`
- Human reviews candidates weekly and promotes to `martinique_slang.json`
