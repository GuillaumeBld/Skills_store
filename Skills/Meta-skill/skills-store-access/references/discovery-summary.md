# Skill Discovery Solution Summary

## Problem Statement

**Challenge**: How can an AI efficiently discover, select, and install skills from the Skills store without:
1. Filling up context window with heavy catalogs
2. Checking unnecessarily for simple tasks
3. Missing opportunities for complex tasks that need specialized skills
4. Installing skills that won't be used

## Research Findings

### Claude's Built-in Progressive Disclosure System

Claude uses a 3-level system that's already optimized:

1. **Level 1: Metadata (Always Loaded)** - ~30-100 tokens per skill
   - Name + description from SKILL.md frontmatter
   - **Already in context** - Claude reads at startup
   - Used for automatic skill triggering

2. **Level 2: SKILL.md Body (When Triggered)** - <5k words
   - Full instructions loaded only when description matches query
   - On-demand, not always in context

3. **Level 3: Bundled Resources (As Needed)** - Unlimited
   - Scripts executed without loading into context
   - References read only when explicitly needed

**Key Insight**: Claude already has access to ALL installed skill metadata. We don't need to duplicate this in context.

### Optimal Solution: Lightweight Discovery System

**Principle**: Use minimal metadata for discovery, only when needed, not in context.

## Solution Architecture

### 1. Lightweight Skills Index (`skills-index.json`)

**Purpose**: Minimal index for discovery queries (NOT loaded into context)

**Structure**:
```json
{
  "version": "1.0.0",
  "updated": "2026-01-15T10:30:00Z",
  "total_skills": 50,
  "skills": [
    {
      "name": "skill-name",
      "description": "One-sentence description (max 50 words)",
      "tags": ["tag1", "tag2"],  // Max 5 tags
      "category": "category",
      "keywords": ["keyword1", "keyword2"]  // Extracted for matching
    }
  ]
}
```

**Size**: ~10KB for 100+ skills (vs 200KB+ for full catalog)
**Benefits**: 
- 90%+ size reduction vs full catalog
- Quick searches without context overhead
- Only loaded when actively searching

### 2. Discovery Workflow

**Step 1: Task Analysis** (`analyze-task-requirements.py`)
- Analyzes query complexity (0-1 score)
- Identifies relevant domains
- Determines if skill discovery is needed

**Step 2: Lightweight Search** (`discover-skills.py`)
- Only runs when complexity/domain suggests skills needed
- Searches `skills-index.json` (NOT full catalog)
- Returns top 3-5 matches with relevance scores

**Step 3: Skill Evaluation**
- Evaluates relevance score
- Checks if skill is already installed
- Decides if proactive installation is beneficial

**Step 4: Action**
- Use existing skill? → Use it
- Install from repo? → Install then use
- Create new skill? → Create it
- No skill needed? → Proceed normally

### 3. Decision Framework

**When to Check Repository:**
1. **New task start** (complexity > 0.4)
2. **Task complexity increases** (user adds requirements)
3. **Ongoing project** (will likely need skills later)
4. **Current approach failing** (suggests better workflow exists)

**When NOT to Check:**
1. Simple, one-off tasks (complexity < 0.2)
2. Already have relevant installed skills
3. Task is progressing well without skills

**Proactive Installation Criteria:**
```
IF (task_complexity > 0.4) 
   AND (skill_relevance > 0.7) 
   AND (is_ongoing_project OR skill_will_be_reused):
    INSTALL proactively
```

## Implementation

### Scripts Created

1. **`generate-skills-index.py`**
   - Extracts minimal metadata from catalog.json
   - Creates lightweight `skills-index.json`
   - 90%+ size reduction
   - Run after adding new skills

2. **`discover-skills.py`**
   - Searches skills-index.json for relevant skills
   - Returns top matches with relevance scores
   - Only loads index during search (not in context)
   - Keyword/tag/description matching

3. **`analyze-task-requirements.py`**
   - Analyzes query for complexity and domain
   - Determines if skill discovery is warranted
   - Recommends proactive installation if beneficial
   - Returns structured analysis

### Integration Points

**With Skill Library Manager:**
- Index generation runs after catalog updates
- Discovery integrates with skill installation workflow
- Recommendations feed into proactive installation logic

**With Claude's Built-in System:**
- Leverages existing metadata loading (don't duplicate)
- Uses lightweight index only for repo discovery
- Installed skills trigger automatically (no changes needed)

## Usage Patterns

### Pattern 1: Simple Task (No Skill)
```
User: "What's the weather?"
Analysis: Complexity 0.1, no domains
Decision: No skill needed
Action: Proceed normally
```

### Pattern 2: Complex Task (Discover & Use)
```
User: "Deploy Docker stack with Traefik"
Analysis: Complexity 0.75, domain: devops
Discovery: "vps-deployment-stack" (relevance: 0.92)
Check: Already installed? Yes
Action: Use skill (auto-triggers)
```

### Pattern 3: Ongoing Project (Proactive Install)
```
User: "Building RAG pipeline for document search"
Analysis: Complexity 0.85, domain: ai/rag, ongoing: true
Discovery: "rag-pipeline-expert" (relevance: 0.95)
Evaluation: Ongoing + high relevance → Install proactively
Action: Install now, use throughout project
```

## Best Practices

### Context Efficiency
- ✅ Never load full catalog.json into context
- ✅ Only load skills-index.json during active searches
- ✅ Use lightweight queries for discovery
- ✅ Clear discovery results from context after use

### Discovery Timing
- ✅ Check at conversation start for complex tasks
- ✅ Check when task complexity increases
- ✅ Check when user explicitly asks about skills
- ❌ Don't check for simple, one-off tasks
- ❌ Don't check repeatedly within same task

### Proactive Installation
- ✅ Install if task is ongoing project
- ✅ Install if skill relevance > 0.7
- ✅ Install if task complexity > 0.5
- ❌ Don't install if relevance < 0.6
- ❌ Don't install if task is one-off

## Metrics to Track

1. **Discovery Efficiency**: % times discovery found relevant skills
2. **False Positives**: % times skill installed but not used
3. **Missed Opportunities**: % times skill existed but wasn't discovered
4. **Proactive Value**: % proactively installed skills actually used
5. **Context Cost**: Average tokens for discovery vs value gained

## Summary

**Key Principles:**
1. **Leverage built-in system**: Claude already has installed skill metadata
2. **Lightweight discovery**: Use minimal index, not full catalog
3. **Strategic timing**: Check at start and when complexity increases
4. **Proactive when beneficial**: Install if ongoing project or high relevance
5. **Context efficiency**: Never load heavy catalogs unnecessarily

**Files:**
- `skills-index.json` - Lightweight index for discovery
- `generate-skills-index.py` - Generate index from catalog
- `discover-skills.py` - Search index for relevant skills
- `analyze-task-requirements.py` - Analyze if skills needed
- `references/skill-discovery-strategy.md` - Complete strategy guide

**Integration:**
- Works with existing skill-library-manager
- Leverages Claude's built-in progressive disclosure
- Minimal context overhead
- Efficient discovery and installation
