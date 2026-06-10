---
name: ralph-loki
description: "Autonomous full-stack startup builder combining Ralph's iterative PRD loop (snarktank/ralph) with Loki's multi-agent swarm orchestration (loki-mode). Use when building complete applications or startups end-to-end: PRD → user stories → autonomous parallel agent execution → deployed product. Triggers on: build this app, execute this PRD, autonomous build, ralph-loki, launch this startup, full-stack autonomous, implement end-to-end. Combines: Ralph (iterative agent loop, prd.json, progress.txt), Loki (37 agents, 6 swarms), feature-forge (requirements), fullstack-guardian (cross-stack implementation), senior-fullstack (scaffolding)."
version: "1.0.0"
license: MIT
metadata:
  author: QualiaAI / Guillaume Bolivard
  domain: AI-Agents
  tags: [autonomous, multi-agent, startup, fullstack, ralph, loki, prd, orchestration]
  related-skills: loki-mode, feature-forge, fullstack-guardian, senior-fullstack, fastapi-expert, nextjs-developer, superpowers
---

# Ralph-Loki: Autonomous Full-Stack Builder

**Combines Ralph's disciplined iterative loop with Loki's multi-agent swarm power.**

Ralph gives you the discipline (PRD → JSON → iterate → commit → repeat).
Loki gives you the scale (37 agents, 6 swarms, parallel execution).
Together: from idea to deployed product, autonomously.

---

## Mental Model

```
IDEA
  ↓
[feature-forge]   → structured PRD (EARS format, clarifying questions)
  ↓
[/ralph skill]    → prd.json (user stories, priorities, acceptance criteria)
  ↓
[ralph-loki loop] → parallel swarms execute stories
  │
  ├── Swarm 1: Product    (PM, designer, UX)
  ├── Swarm 2: Backend    (FastAPI expert, DB, API)
  ├── Swarm 3: Frontend   (Next.js, UI components)
  ├── Swarm 4: Infra      (Docker, VPS, CI/CD)
  ├── Swarm 5: QA         (tests, browser verification)
  └── Swarm 6: Business   (docs, pitch, monetization)
  ↓
[fullstack-guardian] → security + integration review each story
  ↓
DEPLOYED PRODUCT
```

---

## Phase 0: Requirements (feature-forge)

Before any code, run the requirements workshop:

```
Load feature-forge and define requirements for: [your idea]
```

feature-forge will:
1. Ask 3–5 clarifying questions (PM + Dev perspectives)
2. Generate EARS-format requirements
3. Write acceptance criteria (Given/When/Then)
4. Output `tasks/prd-[feature-name].md`

**Do NOT skip this phase.** Vague requirements = wasted iterations.

---

## Phase 1: PRD → prd.json (Ralph skill)

Convert the PRD to Ralph's JSON format:

```
Load the ralph skill and convert tasks/prd-[feature-name].md to prd.json
```

### prd.json schema:
```json
{
  "project": "KotéPrix",
  "branchName": "ralph/koteprix-backend-v1",
  "description": "Price transparency infrastructure for Martinique food markets",
  "swarmConfig": {
    "backend": ["fastapi-expert", "senior-backend"],
    "frontend": ["nextjs-developer", "senior-frontend"],
    "infra": ["senior-devops"],
    "qa": ["senior-qa"],
    "parallel": true
  },
  "userStories": [
    {
      "id": "US-001",
      "title": "PriceRecord SQLAlchemy model",
      "description": "As a developer, I want a PriceRecord model so that prices can be stored",
      "swarm": "backend",
      "acceptanceCriteria": [
        "Model has: id (UUID), product_name, store, price (Decimal), collected_at",
        "Alembic migration created",
        "pytest tests pass"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

### Story sizing rules (CRITICAL):
- ✅ Right-sized: "Add PriceRecord model + migration"
- ✅ Right-sized: "Add GET /prices/latest endpoint"
- ✅ Right-sized: "Build PriceTable component with color coding"
- ❌ Too big: "Build the entire API" → split into 5–10 stories
- ❌ Too big: "Build the dashboard" → split by component/page

---

## Phase 2: Ralph-Loki Execution Loop

### Setup

```bash
# In your project root
mkdir -p scripts/ralph
curl -sf https://raw.githubusercontent.com/snarktank/ralph/main/ralph.sh \
     -o scripts/ralph/ralph.sh
chmod +x scripts/ralph/ralph.sh

# Copy the CLAUDE.md template
curl -sf https://raw.githubusercontent.com/snarktank/ralph/main/CLAUDE.md \
     -o scripts/ralph/CLAUDE.md
```

Customize `scripts/ralph/CLAUDE.md` with your stack:
```markdown
## Quality Checks
- Backend: `cd koteprix-api && pytest tests/ -v`
- Frontend: `cd koteprix-web && npm run type-check && npm run build`
- Lint: `ruff check . && eslint .`

## Stack
- Backend: FastAPI + PostgreSQL + async SQLAlchemy
- Frontend: Next.js 14 App Router + Tailwind + shadcn/ui
- Infra: Docker + docker-compose
```

### Run the loop

```bash
# Single agent (Ralph classic - Claude Code)
./scripts/ralph/ralph.sh --tool claude 20

# Parallel swarms (Ralph-Loki mode)
./scripts/ralph/ralph-loki.sh --parallel 6
```

### What each iteration does (Ralph loop)
1. Read `prd.json` → pick highest priority `passes: false` story
2. Check swarm assignment → spawn right agent (fastapi-expert, nextjs-developer, etc.)
3. Implement the story
4. Run quality checks (`pytest`, `npm run build`, `typecheck`)
5. Update `AGENTS.md` with learnings
6. Commit: `feat: US-001 - PriceRecord SQLAlchemy model`
7. Set `passes: true` in `prd.json`
8. Append to `progress.txt`
9. Repeat until all `passes: true` or max iterations

---

## Phase 3: Parallel Swarm Mode (Loki)

For stories that can run in parallel (no dependencies), spawn multiple agents:

```bash
# ralph-loki.sh spawns agents per swarm in parallel
# Backend swarm: fastapi-expert handles US-001, US-002, US-003
# Frontend swarm: nextjs-developer handles US-010, US-011
# Both run simultaneously via background sessions
```

### Swarm assignment in prd.json

Tag each story with its swarm:
- `"swarm": "backend"` → fastapi-expert + senior-backend
- `"swarm": "frontend"` → nextjs-developer + senior-frontend
- `"swarm": "infra"` → senior-devops
- `"swarm": "qa"` → senior-qa (runs after backend/frontend)
- `"swarm": "data"` → ml-pipeline + rag-pipeline-expert

### Dependency rules
- Backend stories → can parallelize freely
- Frontend stories → can parallelize freely
- QA stories → must run after backend+frontend
- Infra stories → run after all code stories
- `"blockedBy": ["US-001"]` → waits for story to pass

---

## Phase 4: Quality Gates (fullstack-guardian)

After each batch of stories, fullstack-guardian reviews:

```
Load fullstack-guardian and review the implementation of [feature]
```

Checks:
- [Frontend] UX, performance, accessibility
- [Backend] API design, error handling, validation
- [Security] Auth, injection prevention, data exposure

Only proceed to next batch if all three perspectives pass.

---

## Memory System (Ralph pattern)

### progress.txt (append-only)
```
## Codebase Patterns
- Use async/await everywhere (SQLAlchemy async engine)
- PriceRecord.normalized_name is auto-set by normalizer pipeline
- Docker must be running for integration tests
- API base URL: http://localhost:8000/api/v1

## 2026-03-05 17:00 - US-001
- Implemented PriceRecord model + Alembic migration
- Files: app/models/price.py, alembic/versions/001_price_record.py
- Learnings: UUID primary key requires `import uuid` in migration env.py
---
```

### AGENTS.md (per directory)
```markdown
# koteprix-api/app/models/ - AGENTS.md

## Conventions
- All models use UUID primary keys (not Integer)
- Always set `collected_at` at scraper level, not DB default
- `normalized_name` is computed by normalizer.py, never set manually

## Gotchas
- Alembic env.py must import all models for autogenerate to work
- Use `Decimal` not `Float` for prices (precision matters)
```

---

## Commands Reference

### `/prd` — Generate PRD
```
Load the prd skill and create a PRD for [feature description]
```

### `/ralph` — Convert PRD to JSON
```
Load the ralph skill and convert tasks/prd-[name].md to prd.json
```

### `/ralph-loki execute` — Run the loop
```bash
./scripts/ralph/ralph.sh --tool claude [max_iterations]
```

### `/ralph-loki status` — Check progress
```bash
cat prd.json | jq '.userStories[] | {id, title, passes}'
cat progress.txt | tail -30
git log --oneline -10
```

### `/ralph-loki swarms` — Launch parallel swarms
```bash
./scripts/ralph/ralph-loki.sh --parallel
```

---

## Skill Composition Map

| Phase | Primary Skill | Supporting Skills |
|---|---|---|
| Requirements | feature-forge | — |
| PRD → JSON | ralph (prd skill) | — |
| Backend stories | fastapi-expert | senior-backend, postgres-pro |
| Frontend stories | nextjs-developer | senior-frontend, react-expert |
| Cross-stack | fullstack-guardian | — |
| Infra | senior-devops | — |
| QA | senior-qa | playwright-skill |
| Orchestration | ralph-loki (this) | loki-mode, claude-code |
| Memory | ralph (progress.txt) | AGENTS.md pattern |
| Quality | superpowers (TDD) | fullstack-guardian |

---

## Anti-patterns (Do NOT do)

- ❌ Skip feature-forge → vague requirements = wasted iterations
- ❌ Create stories that are too big → agent runs out of context mid-story
- ❌ Skip quality checks before commit → broken code compounds
- ❌ Forget AGENTS.md updates → future iterations repeat mistakes
- ❌ Run QA stories before backend/frontend passes → false failures
- ❌ Mix infrastructure changes with feature code in one story

---

## Example: KotéPrix Full Build

```bash
# Step 1: Requirements
# "Load feature-forge and define requirements for KotéPrix price API"

# Step 2: PRD
# "Load ralph skill and convert to prd.json"

# Step 3: Execute
cd ~/Projects/koteprix-backend
./scripts/ralph/ralph.sh --tool claude 30

# Step 4: Parallel (after US-001 backend done)
cd ~/Projects/koteprix-frontend
./scripts/ralph/ralph.sh --tool claude 20 &

# Monitor
cat prd.json | jq '[.userStories[] | select(.passes == false)] | length'
# → 12 stories remaining
```

---

## References

- `references/ralph-loop.md` — Ralph loop internals, debugging
- `references/swarm-patterns.md` — Parallel swarm patterns
- `references/prd-template.md` — PRD template (EARS format)
- `references/agents-md-guide.md` — How to write AGENTS.md files
- `assets/prd.json.example` — Complete prd.json example

## Sources
- Ralph: https://github.com/snarktank/ralph (Geoffrey Huntley pattern)
- Loki Mode: https://github.com/asklokesh/claudeskill-loki-mode
- Skills: Skills_librairie (feature-forge, fullstack-guardian, senior-fullstack, fastapi-expert, nextjs-developer)
