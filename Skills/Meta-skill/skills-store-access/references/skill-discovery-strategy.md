# Skill Discovery and Selection Strategy

Based on Claude's progressive disclosure architecture and best practices, this document outlines the optimal strategy for skill discovery, selection, and proactive installation.

## Understanding Claude's Built-in Skill System

### Progressive Disclosure (Built-in)

Claude uses a three-level progressive disclosure system:

1. **Level 1: Metadata (Always Loaded)** - ~30-100 tokens per skill
   - Name + description from SKILL.md frontmatter
   - **Already available in context** - Claude reads this at startup
   - Used for skill triggering/matching

2. **Level 2: SKILL.md Body (When Triggered)** - <5k words
   - Full instructions only loaded when description matches user query
   - Loaded on-demand, not always in context

3. **Level 3: Bundled Resources (As Needed)** - Unlimited
   - Scripts executed without loading into context
   - References read only when explicitly needed

**Key Insight**: Claude already has access to ALL installed skill metadata (name + description) in context. We don't need to duplicate this.

## When Should AI Consult the Repo?

### Decision Framework

The AI should consult the Skills store repository in these scenarios:

#### 1. **New Task/Conversation Start** (Proactive Discovery)
**When**: At the beginning of a new task or conversation
**Why**: Establish what skills are available for the task
**How**: 
- Quick check: "What skills exist for [task domain]?"
- Lightweight search: Query catalog.json for relevant skills
- **NOT**: Load full catalog into context (too heavy)

#### 2. **Task Complexity Indicates Specialized Skills Needed** (Reactive Discovery)
**When**: Task requires domain-specific knowledge or workflows
**Triggers**:
- User mentions complex domain (e.g., "deploy Docker stack", "build RAG pipeline")
- Task involves repetitive patterns that suggest existing skills
- User explicitly asks about skills for a task
**How**:
- Search catalog by keywords/tags matching task
- Check if skill exists before attempting manual implementation

#### 3. **Current Approach Failing or Inefficient** (Reactive Discovery)
**When**: Current method is slow, error-prone, or clearly wrong
**Why**: Existing skill might provide better workflow
**How**:
- Pause current approach
- Quick search: "What skills exist for [current task]?"
- Evaluate if skill would improve outcomes

#### 4. **Proactive Installation** (Future-Proofing)
**When**: Task might benefit from skill later, even if not needed now
**Triggers**:
- Multi-step workflow where later steps might need skills
- User indicates ongoing work in a domain
- Task is part of larger project
**Decision Logic**:
```
IF (task_complexity > threshold) AND (skill_available) AND (skill_relevance > 0.7):
    INSTALL skill proactively
```

## Optimal Solution: Lightweight Discovery System

### 1. Minimal Catalog Index (Not in Context)

Create a **lightweight index** for discovery queries (NOT loaded into context):

```json
{
  "skills_index": [
    {
      "name": "skill-name",
      "description": "One-sentence description",  // Max 50 words
      "tags": ["tag1", "tag2"],                    // Max 5 tags
      "category": "category",
      "keywords": ["keyword1", "keyword2"]         // Extracted keywords for matching
    }
  ]
}
```

**Why lightweight?**
- Only name, description, tags, keywords
- No version, author, location, dependencies (not needed for discovery)
- Searchable by semantic similarity or keyword matching
- Generated from catalog.json but much smaller

### 2. Skill Requirement Analysis

Before consulting repo, analyze if skill is needed:

```
Decision Tree:
1. Is this a simple, one-off task?
   → NO SKILL NEEDED (proceed normally)

2. Is this a specialized domain with known patterns?
   → CHECK FOR EXISTING SKILL

3. Is this a complex multi-step workflow?
   → CHECK FOR EXISTING SKILL + CONSIDER PROACTIVE INSTALLATION

4. Will this task be repeated or part of larger project?
   → CHECK FOR EXISTING SKILL + PROACTIVE INSTALLATION
```

### 3. Discovery Workflow

**Step 1: Task Analysis**
```python
def analyze_task_requirements(user_query, task_context):
    """
    Determine if specialized skills are needed
    
    Returns:
    - complexity_score (0-1)
    - domain_tags (list of relevant domains)
    - requires_skill (bool)
    """
    # Analyze query for domain keywords
    # Check task complexity indicators
    # Return recommendations
```

**Step 2: Lightweight Search** (Only when needed)
```python
def discover_relevant_skills(query, tags=None):
    """
    Search skills_index.json for relevant skills
    Returns: List of matching skills with relevance scores
    """
    # Load lightweight index (not full catalog)
    # Semantic/keyword matching
    # Return top 3-5 matches with scores
```

**Step 3: Skill Evaluation**
```python
def evaluate_skill_relevance(skill, task):
    """
    Determine if skill should be used/installed
    Returns: relevance_score, should_use, should_install_proactively
    """
    # Match skill description to task
    # Check dependencies
    # Evaluate installation cost vs benefit
```

**Step 4: Decision & Action**
- Use existing installed skill? → Use it
- Install from repo? → Install then use
- Create new skill? → Create it
- No skill needed? → Proceed normally

## Implementation Strategy

### Phase 1: Lightweight Index Generator

Create `scripts/generate-skills-index.py`:
- Extracts minimal metadata from catalog.json
- Creates `skills-index.json` (lightweight, <10KB even for 100+ skills)
- Includes name, description, tags, keywords only
- Optimized for quick searches

### Phase 2: Discovery Script

Create `scripts/discover-skills.py`:
- Accepts task query/description
- Searches skills-index.json
- Returns relevant skills with relevance scores
- Can run without loading into context

### Phase 3: Requirement Analyzer

Create `scripts/analyze-task-requirements.py`:
- Analyzes user query for skill needs
- Determines if skill search is warranted
- Suggests proactive installation if beneficial

### Phase 4: Integration with Skill Library Manager

Update skill-library-manager to:
- Generate lightweight index automatically
- Provide discovery API/script
- Support proactive installation recommendations

## Best Practices

### 1. Context Efficiency
- **Never** load full catalog.json into context (too heavy)
- **Only** load skills-index.json when actively searching
- **Never** keep discovery results in context longer than needed
- **Always** use lightweight queries for discovery

### 2. Discovery Timing
- **DO** check at conversation start for complex tasks
- **DO** check when task complexity increases
- **DO** check when user explicitly asks about skills
- **DON'T** check for simple, one-off tasks
- **DON'T** check repeatedly within same task

### 3. Proactive Installation
- **DO** install if task is part of ongoing project
- **DO** install if skill will likely be reused
- **DO** install if skill provides significant value
- **DON'T** install if task is one-off and simple
- **DON'T** install if skill relevance is low (<0.6)

### 4. Skill Selection
- **DO** prefer installed skills over repo skills (no installation delay)
- **DO** install if multiple related skills are available (install category)
- **DO** check dependencies before installation
- **DON'T** install if skill description doesn't clearly match task
- **DON'T** install without user confirmation for large/complex skills

## Example Workflows

### Workflow 1: Simple Task (No Skill Needed)
```
User: "What's the weather today?"
AI Analysis: Simple, one-off query
Decision: No skill needed, proceed normally
Action: Use built-in capabilities
```

### Workflow 2: Complex Task (Discover & Use)
```
User: "I need to deploy a Docker stack with Traefik and automatic HTTPS"
AI Analysis: Complex, specialized domain
Decision: Check for existing skills
Action:
  1. Run: discover-skills.py "docker traefik https deployment"
  2. Result: "vps-deployment-stack" (relevance: 0.9)
  3. Check: Is it installed? Yes
  4. Action: Use skill-library-manager to guide deployment
```

### Workflow 3: Multi-Step Task (Proactive Installation)
```
User: "I'm building a RAG system for document search"
AI Analysis: Complex, ongoing project, specialized domain
Decision: Check for skills + proactive installation
Action:
  1. Run: discover-skills.py "RAG pipeline vector search"
  2. Result: "rag-pipeline-expert" (relevance: 0.95)
  3. Check: Is it installed? No
  4. Decision: Install proactively (project will need it)
  5. Action: Install skill, then use it
```

### Workflow 4: Task Evolution (Reactive Discovery)
```
User: "Help me create a document"
AI: Proceeds with normal document creation
User: "Actually, I need to follow our company's structured doc workflow"
AI Analysis: Task complexity increased, specialized workflow needed
Decision: Check for existing skills
Action:
  1. Run: discover-skills.py "document workflow structured"
  2. Result: "doc-coauthoring" (relevance: 0.85)
  3. Check: Is it installed? Yes
  4. Action: Switch to using doc-coauthoring skill
```

## Metrics for Success

Track these metrics to optimize discovery:

1. **Discovery Efficiency**: % of times skill discovery found relevant skills
2. **False Positives**: % of times skill was installed but not used
3. **Missed Opportunities**: % of times skill existed but wasn't discovered
4. **Proactive Installation Value**: % of proactively installed skills actually used
5. **Context Cost**: Average tokens used for discovery vs value gained

## Summary

**Key Principles:**
1. **Leverage built-in system**: Claude already has installed skill metadata
2. **Lightweight discovery**: Use minimal index for searching, not full catalog
3. **Strategic timing**: Check at conversation start and when complexity increases
4. **Proactive when beneficial**: Install if task is ongoing or skill is highly relevant
5. **Context efficiency**: Never load heavy catalogs into context unnecessarily

**Implementation Priority:**
1. Generate lightweight skills-index.json
2. Create discovery script for querying index
3. Integrate discovery into task analysis workflow
4. Add proactive installation decision logic
5. Track metrics and optimize
