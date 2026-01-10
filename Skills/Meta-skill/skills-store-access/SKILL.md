---
name: skills-store-access
description: MAIN ENTRY POINT - Equip any AI system (Claude Code, Claude.ai, Claude API, Cursor, or any platform) with complete Skills store capabilities. This foundational skill enables intelligent skill discovery, proactive installation, and lifecycle management without filling context. Works with any system supporting Claude skills - platform-aware installation auto-detects environment and uses appropriate method. Once equipped, create, store, fetch, search, discover, and manage skills in the Skills_librairie repository. Includes lightweight discovery system (90%+ context reduction), intelligent task analysis, proactive installation for ongoing projects, and complete cross-platform compatibility. Use when you need to equip any AI system with Skills store access, discover relevant skills for tasks, install skills proactively, or manage skills across platforms. The Skills store is located at https://github.com/GuillaumeBld/Skills_librairie and contains organized skills by category in the Skills/ directory.
---

# Skills Store Access

**⭐ MAIN ENTRY POINT - The Foundation of Skills Librairie**

This is the foundational skill that enables **any AI system** to access the complete Skills store. It provides platform-agnostic installation, intelligent discovery, proactive skill installation, and complete lifecycle management without context bloat.

**Works with ANY System:**
- ✅ Claude Code / Cursor (Codex)
- ✅ Claude.ai (Web Interface)
- ✅ Claude API (Programmatic)
- ✅ Any platform supporting Claude skills

**Key Capabilities:**
1. **Platform-Aware Installation** - Auto-detects and adapts to any platform
2. **Intelligent Discovery** - Lightweight skill discovery (90%+ context reduction)
3. **Proactive Installation** - Installs skills for ongoing projects automatically
4. **Complete Lifecycle Management** - Create, search, install, update, sync skills
5. **Context-Efficient** - Never loads heavy catalogs, uses lightweight index only

Once equipped, this skill enables the AI to discover, install, and manage skills from the Skills_librairie repository efficiently.

## Platform-Agnostic Installation: Works with Any System

**The Main Piece**: This skill is the **foundational entry point** for the entire Skills_librairie repository. It works with **any system** that supports Claude skills and automatically adapts to your platform.

The equip script automatically detects your platform and uses the appropriate installation method - no manual configuration needed.

### Step 1: Detect Your Platform

First, check which platform you're on:

```bash
# Run platform detection
python3 /Users/guillaumebld/Documents/Skills/Skills_librairie/Skills/Meta-skill/skills-store-access/scripts/detect-platform.py
```

This will show:
- Platform type (codex/cursor/claude-ai/api)
- Skills directory location
- Available installation methods
- Required tools (gh, git, etc.)

### Step 2: Install Based on Platform

#### For Cursor/Claude Code (Codex) - Recommended Method

```bash
# Method 1: Use equip script (easiest - auto-detects platform)
bash /Users/guillaumebld/Documents/Skills/Skills_librairie/Skills/Meta-skill/skills-store-access/scripts/equip-skills-store.sh

# Method 2: Use skill-installer directly (if available)
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/GuillaumeBld/Skills_librairie/tree/main/Skills/skill-library-manager

# Method 3: Manual installation
# Clone repository if needed
cd ~/Documents/Skills
gh repo clone GuillaumeBld/Skills_librairie

# Install to Codex skills directory
mkdir -p ~/.codex/skills
cp -r ~/Documents/Skills/Skills_librairie/Skills/skill-library-manager ~/.codex/skills/
```

**After installation**: Restart Cursor/Claude Code to pick up the new skill.

#### For Claude.ai (Web Interface)

Claude.ai uses a different skill management system. You have two options:

**Option A: Upload via Web UI**
1. Go to https://claude.ai
2. Navigate to Settings → Skills
3. Click "Upload Skill"
4. Select the skill-library-manager folder:
   ```bash
   # First, ensure repository is cloned locally
   cd ~/Documents/Skills
   gh repo clone GuillaumeBld/Skills_librairie
   
   # Then zip the skill (if needed)
   cd Skills_librairie/Skills
   zip -r skill-library-manager.zip skill-library-manager/
   ```
5. Upload the zip file or folder through Claude.ai UI

**Option B: Use API (if you have API access)**
```bash
# Use Anthropic API to upload skill
# See: https://docs.anthropic.com/en/api/skills-guide
curl -X POST https://api.anthropic.com/v1/skills \
  -H "x-api-key: YOUR_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -F "skill=@skill-library-manager.zip"
```

#### For Claude API (Programmatic Access)

If using Claude API programmatically:

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

# Skills are referenced by ID in API calls
# You'll need to upload the skill first via the API or web UI
# See: https://docs.anthropic.com/en/api/skills-guide
```

### Step 3: Verify Installation

After installation, verify it worked:

```bash
# Run verification script
python3 /Users/guillaumebld/Documents/Skills/Skills_librairie/Skills/Meta-skill/skills-store-access/scripts/verify-installation.py
```

The verification checks:
- ✓ Skills directory exists
- ✓ skill-library-manager is installed
- ✓ SKILL.md is present
- ✓ Required scripts exist
- ✓ Repository access is available
- ✓ Catalog.json is present (or warns if missing)

If verification passes, you're ready to use the Skills store!

```bash
# Clone or ensure repository exists
cd /Users/guillaumebld/Documents/Skills
if [ ! -d "Skills_librairie" ]; then
  gh repo clone GuillaumeBld/Skills_librairie Skills_librairie
fi

# Install to Codex skills directory
mkdir -p ~/.codex/skills
cp -r /Users/guillaumebld/Documents/Skills/Skills_librairie/Skills/skill-library-manager \
      ~/.codex/skills/skill-library-manager

# Or create symlink for development
ln -s /Users/guillaumebld/Documents/Skills/Skills_librairie/Skills/skill-library-manager \
      ~/.codex/skills/skill-library-manager
```

**After installation**: Restart Codex to pick up the new skill. The skill-library-manager will be available for use.

## Skill Discovery and Selection Strategy

### When Should You Consult the Skills Store?

Based on Claude's progressive disclosure architecture, here's when and how to discover and use skills:

#### Understanding Claude's Built-in System

Claude already loads **metadata (name + description)** of all installed skills into context (~30-100 tokens per skill). This means:
- ✅ You already know what installed skills are available
- ✅ Skills trigger automatically based on description matching your query
- ❌ You DON'T need to load a catalog into context (too heavy)

#### Decision Framework: When to Check the Repo

**1. At Conversation/Task Start** (Proactive Discovery)
- When: Beginning of complex task or new conversation
- Why: Establish available skills for the task domain
- How: Quick lightweight search using `discover-skills.py`
- **NOT**: Load full catalog into context

**2. When Task Complexity Increases** (Reactive Discovery)
- When: Task requires specialized domain knowledge
- Triggers:
  - User mentions complex domain (e.g., "deploy Docker stack", "build RAG pipeline")
  - Task involves repetitive patterns suggesting existing skills
  - Current approach is failing or inefficient
- How: Search for relevant skills, evaluate if skill would help

**3. For Ongoing Projects** (Proactive Installation)
- When: Task is part of larger project or will be reused
- Decision Logic:
  ```
  IF (task_complexity > 0.4) AND (skill_relevance > 0.7) AND (is_ongoing_project):
      INSTALL skill proactively
  ```
- Why: Install now to avoid delays later

#### Discovery Workflow

**Step 1: Analyze Task Requirements**
```bash
# Determine if skills are needed for this task
python3 scripts/analyze-task-requirements.py "I need to deploy a Docker stack with Traefik"
# Output: complexity_score, domains, should_check, recommended_skills
```

**Step 2: Discover Relevant Skills** (Only if needed)
```bash
# Search lightweight index (NOT full catalog)
python3 scripts/discover-skills.py "docker traefik deployment" --min-relevance 0.5
# Returns: Top 3-5 matches with relevance scores
```

**Step 3: Evaluate and Install** (If skill is beneficial)
```bash
# Check if skill is already installed
ls ~/.codex/skills/<skill-name>/

# If not installed and relevant, install it
bash scripts/equip-skills-store.sh  # Install skill-library-manager first
# Then use skill-library-manager to install the discovered skill
```

**Step 4: Use Skill** (Let it trigger naturally)
- Skills trigger automatically when description matches your query
- No need to explicitly "call" skills - Claude's built-in system handles this

### Best Practices

**Context Efficiency:**
- ✅ Use lightweight `skills-index.json` for discovery (NOT full catalog.json)
- ✅ Only search when complexity/domain indicators suggest skills needed
- ✅ Never load full catalog into context (too heavy)
- ✅ Generate index once, reuse for all searches

**Discovery Timing:**
- ✅ Check at conversation start for complex tasks
- ✅ Check when task complexity increases
- ✅ Check when user explicitly asks about skills
- ❌ Don't check for simple, one-off tasks
- ❌ Don't check repeatedly within same task

**Proactive Installation:**
- ✅ Install if task is part of ongoing project
- ✅ Install if skill will likely be reused (relevance > 0.7)
- ✅ Install if skill provides significant value (complexity > 0.5)
- ❌ Don't install if task is one-off and simple
- ❌ Don't install if skill relevance is low (< 0.6)

**See**: `references/skill-discovery-strategy.md` for complete strategy guide.

## What You Gain: Skills Store Capabilities

Once equipped with skill-library-manager, you have access to:

### 1. Create New Skills

Create skills following best practices with automated workflow:

```bash
cd /Users/guillaumebld/Documents/Skills/Skills_librairie
bash Skills/skill-library-manager/scripts/create-skill.sh

# Interactive prompts guide you through:
# - Skill name (kebab-case)
# - Category (Meta-skill, Automation, Infrastructure-DevOps, Development, Design-Creative, Communication, Document-Generation, AI-Agents)
# - Description
# - Author
# - Tags
# - Version

# The script automatically:
# - Creates skill structure with SKILL.md, scripts/, references/, assets/
# - Updates catalog.json
# - Commits and tags in Git
# - Pushes to GitHub
```

### 2. Search Skills Store

Find existing skills by keyword, tag, or category:

```bash
cd /Users/guillaumebld/Documents/Skills/Skills_librairie

# Search by keyword
python3 Skills/skill-library-manager/scripts/search-skills.py "database backup"

# Search by tag
python3 Skills/skill-library-manager/scripts/search-skills.py --tag backup

# Search by category
python3 Skills/skill-library-manager/scripts/search-skills.py --category Infrastructure-DevOps

# List all skills
python3 Skills/skill-library-manager/scripts/search-skills.py --all
```

### 3. Fetch/Retrieve Skills

Access skills from the Skills store:

```bash
# Skills are organized by category in:
# /Users/guillaumebld/Documents/Skills/Skills_librairie/Skills/

# Example categories:
# - Skills/Meta-skill/          (Meta-skills for managing skills)
# - Skills/Automation/          (n8n workflows, automation)
# - Skills/Infrastructure-DevOps/ (VPS, Docker, deployment)
# - Skills/Development/         (MCP builders, web tools)
# - Skills/Design-Creative/     (Canvas, themes, art)
# - Skills/Communication/       (Brand guidelines, docs)
# - Skills/Document-Generation/ (PDF, DOCX, PPTX, XLSX)
# - Skills/AI-Agents/           (RAG, AI workflows)

# Read any skill directly:
cat /Users/guillaumebld/Documents/Skills/Skills_librairie/Skills/Automation/n8n-workflow-patterns/SKILL.md

# Browse skill structure:
ls -la /Users/guillaumebld/Documents/Skills/Skills_librairie/Skills/Infrastructure-DevOps/
```

### 4. Store/Update Skills

Save new skills or update existing ones in the Skills store:

```bash
cd /Users/guillaumebld/Documents/Skills/Skills_librairie

# Option A: Use create-skill.sh (for new skills)
bash Skills/skill-library-manager/scripts/create-skill.sh

# Option B: Manual creation
# 1. Choose category
CATEGORY="Meta-skill"  # or Automation, Infrastructure-DevOps, etc.
SKILL_NAME="my-new-skill"

# 2. Create structure
mkdir -p Skills/${CATEGORY}/${SKILL_NAME}/{scripts,references,assets}

# 3. Create SKILL.md with frontmatter
cat > Skills/${CATEGORY}/${SKILL_NAME}/SKILL.md << 'EOF'
---
name: my-new-skill
description: Description of what this skill does
---
# My New Skill

[Skill content here]
EOF

# 4. Update catalog
python3 Skills/skill-library-manager/scripts/catalog-builder.py

# 5. Commit and push
git add Skills/${CATEGORY}/${SKILL_NAME}
git add catalog.json
git commit -m "Add ${SKILL_NAME} skill v1.0.0 to ${CATEGORY} category"
git tag ${SKILL_NAME}-v1.0.0
git push origin main --tags
```

### 5. Sync with GitHub

Keep Skills store synchronized with GitHub:

```bash
cd /Users/guillaumebld/Documents/Skills/Skills_librairie

# Pull latest changes
git pull origin main --tags

# Push local changes
git push origin main --tags

# Or use sync script
bash Skills/skill-library-manager/scripts/sync-library.sh
```

## Repository Structure

The Skills store repository structure:

```
Skills_librairie/
├── README.md                          # Library overview
├── catalog.json                       # Searchable skill index (auto-generated)
└── Skills/                            # Skills organized by category
    ├── Meta-skill/                    # Skills about managing skills
    ├── Automation/                    # n8n, workflow automation
    ├── Infrastructure-DevOps/         # VPS, Docker, deployment
    ├── Development/                   # MCP, web tools, testing
    ├── Design-Creative/               # Canvas, themes, art
    ├── Communication/                 # Brand, docs, internal comms
    ├── Document-Generation/           # PDF, DOCX, PPTX, XLSX
    ├── AI-Agents/                     # RAG, AI workflows
    └── skill-library-manager/         # This management skill
```

## Common Workflows

### "I need a skill for X"

```bash
# 1. Search the Skills store
cd /Users/guillaumebld/Documents/Skills/Skills_librairie
python3 Skills/skill-library-manager/scripts/search-skills.py "your search term"

# 2. If found, read it
cat Skills/<category>/<skill-name>/SKILL.md

# 3. If not found, create it (see "Create New Skills" above)
```

### "Create and store a new skill"

```bash
# Use automated workflow
cd /Users/guillaumebld/Documents/Skills/Skills_librairie
bash Skills/skill-library-manager/scripts/create-skill.sh

# Follow prompts, then skill is automatically:
# - Created with proper structure
# - Added to catalog.json
# - Committed to Git
# - Tagged with version
# - Pushed to GitHub
```

### "Update an existing skill"

```bash
cd /Users/guillaumebld/Documents/Skills/Skills_librairie

# 1. Navigate to skill
cd Skills/<category>/<skill-name>

# 2. Edit SKILL.md, add scripts, references, assets

# 3. Update version in SKILL.md frontmatter

# 4. Update catalog
cd /Users/guillaumebld/Documents/Skills/Skills_librairie
python3 Skills/skill-library-manager/scripts/catalog-builder.py

# 5. Commit with version bump
git add Skills/<category>/<skill-name>
git add catalog.json
git commit -m "Update <skill-name> to v<version>"
git tag <skill-name>-v<version>
git push origin main --tags
```

## Prerequisites

Before using the Skills store, ensure:

- **GitHub CLI (`gh`)**: `gh auth login` (for GitHub operations)
- **Git**: Installed and configured
- **Python 3.8+**: For catalog operations
- **Repository access**: Clone `GuillaumeBld/Skills_librairie` or ensure it exists at `/Users/guillaumebld/Documents/Skills/Skills_librairie`

## Verification and Testing

### Verify Installation

After equipping, always verify:

```bash
# Run comprehensive verification
python3 /Users/guillaumebld/Documents/Skills/Skills_librairie/Skills/Meta-skill/skills-store-access/scripts/verify-installation.py
```

### Test Skills Store Access

Once installed, test that you can access the Skills store:

```bash
# Test 1: Check if skill-library-manager is accessible
ls ~/.codex/skills/skill-library-manager/  # Should show SKILL.md, scripts/, etc.

# Test 2: Search for skills (requires repository)
cd /Users/guillaumebld/Documents/Skills/Skills_librairie
python3 Skills/skill-library-manager/scripts/search-skills.py --all

# Test 3: Try creating a test skill
bash Skills/skill-library-manager/scripts/create-skill.sh
# Enter test values, verify it creates the skill structure

# Test 4: Verify skill-library-manager skill is loaded
# In your IDE/Codex, try asking: "Use the skill-library-manager to search for skills"
```

### Platform-Specific Testing

**Cursor/Claude Code:**
- After installation, restart Cursor/Claude Code
- Try: "Use the skill-library-manager skill to list all skills"
- The skill should be automatically detected and used

**Claude.ai:**
- After uploading via UI, check Settings → Skills to see if it's listed
- Try: "Use the skill-library-manager to search for database skills"
- If skill doesn't trigger, check the description in SKILL.md frontmatter

**API:**
- After uploading via API, verify skill ID is returned
- Use skill ID in API calls with `skill_ids` parameter
- Test with a simple API request

## Troubleshooting

### Platform Detection Issues

```bash
# If platform detection fails, manually check:
python3 /Users/guillaumebld/Documents/Skills/Skills_librairie/Skills/Meta-skill/skills-store-access/scripts/detect-platform.py

# Check environment variables
echo $CODEX_HOME  # Should point to ~/.codex or custom location
echo $ANTHROPIC_API_KEY  # For API access

# Check for skills directories
ls -la ~/.codex/skills/  # Codex/Cursor
ls -la ~/.cursor/skills/  # Cursor (alternate location)
```

### Skill-library-manager Not Available After Installation

**For Codex/Cursor:**
```bash
# Verify installation
ls ~/.codex/skills/skill-library-manager/

# Check if skill is in correct location
# Codex looks for skills in: $CODEX_HOME/skills/ (default: ~/.codex/skills/)
# Cursor may use: ~/.cursor/skills/ or ~/.codex/skills/

# Reinstall if missing
bash /Users/guillaumebld/Documents/Skills/Skills_librairie/Skills/Meta-skill/skills-store-access/scripts/equip-skills-store.sh

# Restart IDE/Codex completely (not just reload window)
```

**For Claude.ai:**
- Check Settings → Skills to see if skill is listed
- Verify skill description includes relevant keywords
- Try re-uploading the skill
- Check skill frontmatter (name and description are required)

**For API:**
- Verify skill was uploaded successfully (check API response)
- Confirm skill ID is correct
- Check API key permissions (some keys may not support skills)

### Repository Not Found

```bash
# Clone repository
cd ~/Documents/Skills  # Or your preferred location
gh repo clone GuillaumeBld/Skills_librairie

# Or using git
git clone https://github.com/GuillaumeBld/Skills_librairie.git

# Verify structure
ls Skills_librairie/Skills/skill-library-manager/
```

### GitHub Authentication Issues

```bash
# Re-authenticate GitHub CLI
gh auth login

# Verify authentication
gh auth status

# Test repository access
gh repo view GuillaumeBld/Skills_librairie

# If using Git instead of gh
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Catalog Out of Sync

```bash
# Rebuild catalog
cd /Users/guillaumebld/Documents/Skills/Skills_librairie
python3 Skills/skill-library-manager/scripts/catalog-builder.py

# Verify catalog was created
cat catalog.json | python3 -m json.tool | head -20

# Commit updated catalog (if using Git)
git add catalog.json
git commit -m "Rebuild catalog"
git push
```

### Skill Not Triggering in IDE

**Common causes:**
1. **Skill not loaded**: Restart IDE completely
2. **Description too vague**: Update SKILL.md frontmatter description with more specific keywords
3. **Name collision**: Check if another skill has the same name
4. **Path issues**: Verify skill is in correct directory (`~/.codex/skills/` for Codex)

**Debug steps:**
```bash
# Check if skill is detected
ls ~/.codex/skills/skill-library-manager/SKILL.md

# Verify frontmatter
head -10 ~/.codex/skills/skill-library-manager/SKILL.md

# Check for syntax errors in SKILL.md
python3 -c "import yaml; yaml.safe_load(open('~/.codex/skills/skill-library-manager/SKILL.md').read().split('---')[1])"
```

### Platform-Specific Issues

**Cursor/Claude Code:**
- Skills load on startup, so full restart is required
- Check `~/.codex/skills/` (or `$CODEX_HOME/skills/`)
- Verify skill-installer scripts exist at `~/.codex/skills/.system/skill-installer/`

**Claude.ai:**
- Skills are managed through web UI (Settings → Skills)
- Upload size limits may apply (check Claude.ai documentation)
- Skill must have valid frontmatter (name + description)

**API:**
- Skills are uploaded via API endpoints (see Anthropic API docs)
- Skill IDs are returned after upload - save these
- API rate limits may apply for skill operations

## Complete Discovery Workflow Example

### Example 1: Complex Task - Discover and Use

```
User: "I need to deploy a Docker stack with Traefik and automatic HTTPS"

AI Analysis:
1. Run: analyze-task-requirements.py "deploy Docker stack Traefik HTTPS"
   → Complexity: 0.75, Domains: [devops], Should check: YES

2. Run: discover-skills.py "docker traefik https deployment"
   → Found: "vps-deployment-stack" (relevance: 0.92)

3. Check: Is it installed?
   → ls ~/.codex/skills/vps-deployment-stack/
   → If not: Install it via skill-library-manager

4. Use: Skill triggers automatically based on description match
   → Claude uses vps-deployment-stack skill for deployment
```

### Example 2: Ongoing Project - Proactive Installation

```
User: "I'm building a RAG system for document search"

AI Analysis:
1. Run: analyze-task-requirements.py "RAG system document search" --ongoing
   → Complexity: 0.85, Domains: [ai/rag], Should check: YES
   → Ongoing project: TRUE

2. Run: discover-skills.py "RAG pipeline vector search"
   → Found: "rag-pipeline-expert" (relevance: 0.95)

3. Evaluate: Should install proactively?
   → Ongoing project + high relevance (0.95) → YES
   → Install proactively

4. Install: Use skill-library-manager to install rag-pipeline-expert
   → Available for use throughout project
```

### Example 3: Simple Task - No Skill Needed

```
User: "What's the weather today?"

AI Analysis:
1. Run: analyze-task-requirements.py "weather today"
   → Complexity: 0.1, Domains: [], Should check: NO
   → Simple query, no specialized skills needed

2. Action: Proceed with built-in capabilities
   → No skill discovery needed
```

## Generating the Skills Index

Before using discovery tools, generate the lightweight index:

```bash
cd /Users/guillaumebld/Documents/Skills/Skills_librairie

# Generate lightweight index from catalog.json
python3 Skills/Meta-skill/skills-store-access/scripts/generate-skills-index.py

# This creates: skills-index.json
# Much smaller than catalog.json (90%+ reduction)
# Contains: name, description (max 50 words), tags, keywords only
# Optimized for quick searches without context overhead
```

Update the index whenever new skills are added:
```bash
# After adding new skill, regenerate catalog and index
python3 Skills/skill-library-manager/scripts/catalog-builder.py
python3 Skills/Meta-skill/skills-store-access/scripts/generate-skills-index.py
```

## Related Skills

- **skill-installer** (system skill) - Installs skills from GitHub
- **skill-creator** (system skill) - Guides skill creation
- **skill-library-manager** - The equipped skill that provides Skills store management
- See `references/skill-discovery-strategy.md` for detailed discovery strategy and best practices

## Quick Testing

After installation, run the test suite to verify everything works:

```bash
# Run comprehensive test suite
bash /Users/guillaumebld/Documents/Skills/Skills_librairie/Skills/Meta-skill/skills-store-access/scripts/test-skills-store.sh
```

The test suite checks:
- Platform detection works
- Verification script runs
- Equip script is executable
- Skill is installed (if on Codex/Cursor)
- Repository is accessible
- Required tools are available (Python, Git, GitHub CLI)
- Skill functionality works (catalog builder, search)

## Ensuring It Works Properly

### Best Practices for Cross-Platform Compatibility

1. **Always verify installation** after equipping:
   ```bash
   python3 /path/to/verify-installation.py
   ```

2. **Test on your specific platform**:
   - Codex/Cursor: Full IDE restart required after installation
   - Claude.ai: Check Settings → Skills to verify upload
   - API: Verify skill ID after upload

3. **Check platform-specific requirements**:
   ```bash
   python3 /path/to/detect-platform.py
   ```

4. **Use the test suite** to verify all components:
   ```bash
   bash /path/to/test-skills-store.sh
   ```

5. **Monitor for platform updates**: Skills system may change, check:
   - Codex/Cursor: Update documentation if skills directory changes
   - Claude.ai: Check for UI changes in skill management
   - API: Monitor Anthropic API changelog for skill-related changes

### Common Issues Across Platforms

**Issue**: Skill installed but not triggering
- **Solution**: Check frontmatter description includes relevant keywords
- **Solution**: Verify skill name is unique (no conflicts)
- **Solution**: Ensure full IDE restart (not just reload)

**Issue**: Repository access fails
- **Solution**: Verify GitHub authentication (`gh auth status`)
- **Solution**: Check network connectivity
- **Solution**: Verify repository exists and is accessible

**Issue**: Scripts fail to execute
- **Solution**: Check file permissions (`chmod +x script.sh`)
- **Solution**: Verify Python version (3.8+ required)
- **Solution**: Check Python dependencies (`pip install pyyaml`)

### Platform-Specific Validation

**For Cursor/Claude Code:**
```bash
# Verify skill is loaded
ls ~/.codex/skills/skill-library-manager/SKILL.md

# Check skill appears in IDE
# In IDE, try: "Use skill-library-manager to search for skills"
# Should trigger the skill automatically
```

**For Claude.ai:**
```bash
# After upload, verify in UI:
# Settings → Skills → Should show "skill-library-manager"
# Description should match what's in SKILL.md frontmatter

# Test by asking Claude.ai:
# "Use the skill-library-manager to list all skills"
```

**For API:**
```bash
# After upload, save skill ID from API response
# Use skill ID in subsequent API calls
# Test with simple request including skill_id
```

## Quick Reference

**Repository**: https://github.com/GuillaumeBld/Skills_librairie
**Local path**: `/Users/guillaumebld/Documents/Skills/Skills_librairie` (default)
**Install URL**: `https://github.com/GuillaumeBld/Skills_librairie/tree/main/Skills/skill-library-manager`
**Catalog file**: `catalog.json` (auto-generated, searchable index)
**Skill categories**: Meta-skill, Automation, Infrastructure-DevOps, Development, Design-Creative, Communication, Document-Generation, AI-Agents

**Key Scripts:**
- `equip-skills-store.sh` - Install skill-library-manager (auto-detects platform)
- `detect-platform.py` - Detect current platform and capabilities
- `verify-installation.py` - Verify installation and configuration
- `test-skills-store.sh` - Comprehensive test suite
- `generate-skills-index.py` - Generate lightweight index for discovery (lightweight, <10KB)
- `discover-skills.py` - Discover relevant skills for a task query
- `analyze-task-requirements.py` - Analyze if task needs specialized skills

**Discovery Tools:**
- `skills-index.json` - Lightweight index (name, description, tags, keywords only)
- Generated from catalog.json but much smaller (90%+ size reduction)
- Optimized for quick searches without loading into context
- Update when new skills are added to repository

**Platform-Specific Paths:**
- Codex/Cursor: `~/.codex/skills/` (or `$CODEX_HOME/skills/`)
- Claude.ai: Managed via web UI (Settings → Skills)
- API: Managed via API endpoints (skill IDs)

**Support:**
- Check platform detection output for your specific environment
- Run verification script to diagnose issues
- Use test suite to verify all components work
- Review troubleshooting section for common issues
