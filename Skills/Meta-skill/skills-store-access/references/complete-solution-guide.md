# Complete Solution: Skill Discovery and Selection for AI Agents

## The Core Question

**"When should the AI consult the repo to fetch skills? How can we make it aware (without filling up its context) that it needs to establish what skills are required for its task and if it should even use one, which one, and if it does not exist but might need it later, it should do it now?"**

## The Answer: Research-Based Optimal Solution

### Key Finding: Claude Already Handles Installed Skills

**Critical Discovery**: Claude's progressive disclosure system already loads ALL installed skill metadata (name + description) into context at startup (~30-100 tokens per skill). This means:
- ✅ Installed skills are automatically known and triggerable
- ✅ No need to load catalogs for installed skills
- ❌ We only need discovery for **skills not yet installed**

### The Optimal Solution: Lightweight Discovery System

We don't need to store a full list in context. Instead, we use:

1. **Lightweight Index** - Minimal metadata (~10KB for 100+ skills)
2. **On-Demand Search** - Only when complexity/domain suggests skills needed
3. **Proactive Installation** - When task is ongoing or skill is highly relevant

## When Should AI Consult the Repo?

### Decision Framework

```
IF (task_complexity > 0.4) OR (domain_keywords_detected) OR (is_ongoing_project):
    → CONSULT repo (lightweight search)
ELSE IF (simple_one_off_task):
    → NO need to consult repo
```

### Specific Triggers

**1. At Task/Conversation Start** (Proactive Discovery)
- **When**: Beginning of new task or conversation
- **Why**: Establish available skills for task domain
- **How**: Quick lightweight search (`discover-skills.py`)
- **NOT**: Load full catalog into context

**2. When Task Complexity Increases** (Reactive Discovery)
- **When**: Task requires specialized domain knowledge
- **Triggers**:
  - User mentions complex domain (e.g., "deploy Docker stack")
  - Task involves repetitive patterns
  - Current approach is failing or inefficient
- **How**: Search for relevant skills, evaluate if skill would help

**3. For Ongoing Projects** (Proactive Installation)
- **When**: Task is part of larger project or will be reused
- **Decision**: Install now to avoid delays later
- **Criteria**: Complexity > 0.4 AND relevance > 0.7 AND (ongoing OR reusable)

**4. When User Explicitly Asks** (Explicit Discovery)
- **When**: User asks "What skills do I have?" or "Find skills for X"
- **How**: Search and present results

## How to Make AI Aware Without Filling Context

### Solution: Lightweight Index + On-Demand Search

**NOT in Context:**
- ❌ Full catalog.json (too heavy, 200KB+)
- ❌ All skill descriptions (redundant with installed skills)
- ❌ Detailed metadata (version, author, dependencies)

**In Context (when needed):**
- ✅ Lightweight skills-index.json (~10KB for 100+ skills)
- ✅ Only during active discovery searches
- ✅ Cleared after use

**Always Available (no context cost):**
- ✅ Installed skill metadata (already in Claude's context)
- ✅ Discovery scripts (executable, not in context)
- ✅ Decision logic (algorithm, not data)

### Discovery Workflow

```
Step 1: Task Analysis (lightweight)
  → analyze-task-requirements.py "user query"
  → Returns: complexity_score, domains, should_check
  
Step 2: Discovery (only if needed)
  IF should_check:
    → discover-skills.py "query keywords"
    → Returns: top 3-5 matches with relevance scores
    → Loads skills-index.json temporarily (NOT full catalog)
  
Step 3: Evaluation
  → Check if skill installed: ls ~/.codex/skills/<skill>/
  → Evaluate relevance vs installation cost
  → Decide: Use existing / Install / Create / Skip
  
Step 4: Action
  → Use skill if installed (auto-triggers)
  → Install if not installed and beneficial
  → Create if doesn't exist and needed
  → Proceed without skill if not beneficial
```

## Should It Store a List of Existing Skills?

### Answer: No, But Maintain a Lightweight Index

**Why Not Store Full List:**
- Claude already has installed skill metadata in context
- Full catalog is too heavy (200KB+)
- Would fill context unnecessarily

**What to Maintain Instead:**
- **Lightweight skills-index.json** (~10KB, 90%+ reduction)
  - Name, description (max 50 words), tags, keywords only
  - Generated from catalog.json but much smaller
  - Updated when new skills added
  - Used for discovery searches (not in context)

**When to Update:**
- After adding new skills to repository
- When catalog.json is regenerated
- Before major discovery searches (optional, auto-sync)

## Proactive Installation Strategy

### When to Install Proactively

**Decision Logic:**
```python
should_install_proactively = (
    (task_complexity > 0.5) AND
    (skill_relevance > 0.7) AND
    (
        is_ongoing_project OR
        skill_will_likely_be_reused OR
        skill_provides_significant_value
    )
)
```

**Examples:**

✅ **Install Proactively:**
- Task: "Building RAG pipeline for document search"
- Analysis: Complexity 0.85, relevance 0.95, ongoing project
- Decision: Install `rag-pipeline-expert` now (will need it throughout project)

✅ **Install Proactively:**
- Task: "Deploy Docker stack with Traefik"
- Analysis: Complexity 0.75, relevance 0.92, reusable pattern
- Decision: Install `vps-deployment-stack` now (will use this pattern again)

❌ **Don't Install:**
- Task: "What's the weather today?"
- Analysis: Complexity 0.1, no relevant skills
- Decision: Skip skill discovery entirely

❌ **Don't Install Proactively:**
- Task: "One-time PDF conversion"
- Analysis: Complexity 0.3, relevance 0.4
- Decision: Not worth installing (one-off task, low relevance)

## Implementation: Complete System

### Files Created

**Discovery Scripts:**
1. `generate-skills-index.py` - Creates lightweight index from catalog
2. `discover-skills.py` - Searches index for relevant skills
3. `analyze-task-requirements.py` - Determines if skills needed

**Documentation:**
1. `skill-discovery-strategy.md` - Complete strategy guide
2. `discovery-summary.md` - Solution summary
3. `complete-solution-guide.md` - This document

**Integration:**
- Works with existing skill-library-manager
- Leverages Claude's built-in progressive disclosure
- Minimal context overhead

### Usage Example

```python
# 1. Generate index (one-time, or after adding skills)
python3 generate-skills-index.py

# 2. Analyze task
python3 analyze-task-requirements.py "I need to deploy a Docker stack" --ongoing

# Output:
# {
#   "complexity_score": 0.75,
#   "domains": ["devops"],
#   "should_check_for_skills": true,
#   "check_reason": "Task complexity score 0.75 suggests specialized skills",
#   "recommended_skills": [
#     {"name": "vps-deployment-stack", "relevance": 0.92}
#   ],
#   "proactive_installation": [
#     {"skill": "vps-deployment-stack", "reason": "High complexity + good relevance"}
#   ]
# }

# 3. Discover specific skills (if not in analysis output)
python3 discover-skills.py "docker traefik deployment" --min-relevance 0.5

# 4. Install if needed
# (Use skill-library-manager to install discovered skills)
```

## Best Practices Summary

### ✅ DO:

1. **Check at conversation start** for complex tasks (complexity > 0.4)
2. **Use lightweight index** for discovery (skills-index.json, NOT catalog.json)
3. **Install proactively** if ongoing project + high relevance (> 0.7)
4. **Clear discovery results** from context after use
5. **Update index** when new skills are added

### ❌ DON'T:

1. **Don't load full catalog** into context (too heavy)
2. **Don't check for simple tasks** (complexity < 0.2)
3. **Don't install low-relevance skills** (< 0.6)
4. **Don't check repeatedly** within same task
5. **Don't store full skill lists** in context (Claude already has installed skills)

## Context Efficiency Calculation

**Scenario: 100 Skills in Repository**

**Full Catalog Approach:**
- catalog.json: ~200KB
- Context cost: ~50,000 tokens (if loaded)
- ❌ Too expensive for context

**Lightweight Index Approach:**
- skills-index.json: ~10KB
- Context cost: Only during searches (~2,500 tokens)
- ✅ 90%+ reduction, only when needed

**Claude's Built-in (Installed Skills):**
- Metadata for 20 installed skills: ~2,000 tokens
- ✅ Already in context (no additional cost)
- ✅ Auto-triggers based on description match

**Total Efficient Approach:**
- Installed skills: 2,000 tokens (always, built-in)
- Discovery index: 0 tokens (not in context, only during searches)
- Search results: ~500 tokens (temporary, cleared after use)
- ✅ Minimal context overhead

## Summary

**Answer to Core Question:**

1. **When to consult repo:**
   - At task start (complexity > 0.4)
   - When complexity increases
   - For ongoing projects
   - When user explicitly asks

2. **How to make aware without filling context:**
   - Use lightweight skills-index.json (NOT full catalog)
   - Only load during active searches
   - Clear results after use
   - Leverage Claude's built-in metadata for installed skills

3. **Should it store a list:**
   - No full list in context
   - Yes, lightweight index for discovery (not in context)
   - Claude already has installed skill metadata

4. **Proactive installation:**
   - Install if complexity > 0.5 AND relevance > 0.7 AND (ongoing OR reusable)
   - Don't install for simple one-off tasks
   - Evaluate cost vs benefit

**Key Principle:** 
- ✅ Use Claude's built-in system for installed skills (free, already in context)
- ✅ Use lightweight discovery for repository skills (only when needed)
- ✅ Install proactively when beneficial (ongoing projects, high relevance)
- ❌ Never load heavy catalogs into context
