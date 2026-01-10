# JAAT-Enhanced Skill Auto-Discovery System

## Overview

This system integrates **JAAT (Job Ad Analysis Toolkit)** into the Skills Library to automatically identify required skills from user queries, detect gaps in the catalog, and auto-create missing skills using authoritative sources.

**What is JAAT?**

JAAT is a library that extracts standardized skill and task information from text using:
- **O*NET** - Occupational Information Network task taxonomy
- **EuropaCode** - European skills classification system

This enables the Skills Library to:
1. Understand complex queries using standardized skill definitions
2. Map user needs to professional skill taxonomies
3. Identify gaps where skills don't exist but should
4. Auto-create skills using authoritative sources

## Architecture

```
User Query/Context
    ↓
[Enhanced Task Analysis] ← Uses JAAT to extract standardized skills/tasks (O*NET + EuropaCode)
    ↓
[Skill Identification] ← Maps standardized skills to needed skills
    ↓
[Catalog Search] ← Check if skills exist in Skills Library
    ↓
    ├─→ Skills Found → Recommend existing skills
    └─→ Skills Missing → [Auto-Create Skills]
                           ↓
                    [Gather Authoritative Sources]
                           ↓
                    [Generate Skill Content]
                           ↓
                    [Create Skill via skill-creator]
                           ↓
                    [Validate & Integrate]
```

## Components

### 1. JAAT Enhancement Module
**File**: `scripts/jaat-enhanced-discovery.py`

- Extracts O*NET tasks using `TaskMatch.get_tasks()`
- Extracts EuropaCode skills using `SkillMatch.get_skills()`
- Normalizes outputs for catalog matching
- Maps to skill domains

**Usage**:
```bash
python3 jaat-enhanced-discovery.py "We need a backend engineer to design APIs" --json
```

**Known Issues**:
- JAAT has a pickling issue with local functions that prevents full extraction in some cases
- Workaround: System gracefully falls back to keyword-based analysis if JAAT fails
- The extraction works, but result serialization can fail - this is a JAAT library issue

### 2. Enhanced Task Analysis
**File**: `scripts/analyze-task-requirements.py` (enhanced)

- Integrates JAAT extraction when `--use-jaat` flag is provided
- Combines keyword-based and JAAT-based analysis
- Generates enhanced search queries from standardized skills

**Usage**:
```bash
python3 analyze-task-requirements.py "Deploy Docker stack" --use-jaat --json
```

### 3. Skill Gap Detection
**File**: `scripts/detect-skill-gaps.py`

- Compares identified skill requirements against catalog
- Finds missing skills
- Prioritizes which skills to create

**Usage**:
```bash
echo '{"skill_requirements": [...]}' | python3 detect-skill-gaps.py --json
```

### 4. Source Gathering
**File**: `scripts/gather-skill-sources.py`

- Identifies authoritative sources (official docs, GitHub, O*NET, EuropaCode)
- Maps technologies to their documentation URLs
- Can fetch content (optional, slow)

**Usage**:
```bash
echo '{"prioritized_gaps": [...]}' | python3 gather-skill-sources.py --json
```

### 5. Auto-Skill Creation
**File**: `scripts/auto-create-skill.py`

- Generates SKILL.md content from requirements and sources
- Uses skill-creator workflow (`init_skill.py`)
- Creates skill structure following best practices

**Usage**:
```bash
echo '{"requirement": {...}}' | python3 auto-create-skill.py --dry-run
```

### 6. End-to-End Test
**File**: `scripts/test-jaat-workflow.py`

- Tests complete workflow from query to skill creation
- Demonstrates integration between components

**Usage**:
```bash
python3 test-jaat-workflow.py "Deploy Docker application" --use-jaat
```

## Workflow

### Step 1: Analyze Requirements
```bash
python3 analyze-task-requirements.py "query" --use-jaat
```

### Step 2: Extract Standardized Skills (JAAT)
- Extracts O*NET tasks
- Extracts EuropaCode skills
- Normalizes for catalog search

### Step 3: Detect Gaps
```bash
# Pipe requirements to gap detection
python3 analyze-task-requirements.py "query" --json | \
  python3 detect-skill-gaps.py --json
```

### Step 4: Gather Sources
```bash
# Pipe gaps to source gathering
python3 detect-skill-gaps.py --json < requirements.json | \
  python3 gather-skill-sources.py --json
```

### Step 5: Create Skills
```bash
# Create skill from requirement
python3 auto-create-skill.py --dry-run < requirement.json
```

## Current Status

### ✅ Completed
- JAAT integration module created
- Enhanced task analysis with JAAT support
- Skill gap detection script
- Source gathering framework
- Auto-creation framework
- End-to-end test script

### ✅ Completed (Implementation Status)
- ✅ JAAT integration module created and functional
- ✅ Enhanced task analysis with JAAT support
- ✅ Skill gap detection script implemented
- ✅ Source gathering framework created
- ✅ Auto-creation framework implemented
- ✅ End-to-end test script created
- ✅ Main SKILL.md updated with JAAT workflow documentation
- ✅ Integration guide documentation completed
- ✅ Requirements.txt created with dependencies
- ✅ Path consistency fixes applied across scripts

### ⚠️ Known Issues
1. **JAAT Pickling Error**: JAAT library has internal pickling issues that prevent full extraction in some cases. The system gracefully handles this with fallback to keyword analysis. This is a known JAAT library limitation, not a bug in our implementation.

### 🔄 Future Enhancements (Optional)
1. **Full Content Fetching**: Enhance `gather-skill-sources.py` to fetch and parse full content from authoritative sources (currently just identifies URLs)
2. **Enhanced Skill Generation**: Improve `auto-create-skill.py` to generate more detailed SKILL.md content from fetched sources
3. **Validation Pipeline**: Add comprehensive validation and quality checks for auto-created skills before integration
4. **Batch Processing**: Support analyzing multiple queries/job postings in batch mode
5. **Skill Improvement**: Implement skill improvement suggestions based on usage patterns
6. **n8n Integration**: Create n8n workflows for automated skill creation pipelines
7. **Source Monitoring**: Monitor authoritative sources for changes and suggest skill updates

## Installation

### Step 1: Install Dependencies

```bash
cd /Users/guillaumebld/Documents/Skills/Skills_librairie
pip install -r Skills/Meta-skill/skills-store-access/requirements.txt
```

Or install individually:
```bash
pip install JAAT requests beautifulsoup4 markdownify lxml
```

**Note**: JAAT may require additional dependencies. If installation fails, check the [JAAT documentation](https://github.com/your-org/JAAT) for specific requirements.

### Step 2: Verify Installation

```bash
# Test JAAT import
python3 -c "from JAAT import JAAT; print('JAAT installed successfully')"

# Test the JAAT extraction script
python3 Skills/Meta-skill/skills-store-access/scripts/jaat-enhanced-discovery.py \
  "We need a backend engineer to design REST APIs" --json
```

## Dependencies

**Required:**
- `JAAT>=1.0.0` - Job Ad Analysis Toolkit
- `requests>=2.31.0` - For fetching authoritative sources
- `beautifulsoup4>=4.12.0` - For parsing HTML documentation
- `markdownify>=0.11.0` - For converting HTML to markdown

**Optional:**
- `lxml>=4.9.0` - For enhanced HTML parsing (faster than default parser)
- `sentence-transformers` - Automatically installed with JAAT for embeddings

**Existing Tools Used:**
- `skill-creator/scripts/init_skill.py` - Initialize skill structure
- `skill-creator/scripts/package_skill.py` - Package created skills
- `skill-library-manager/scripts/catalog-builder.py` - Update catalog

## Testing

Run the complete workflow test:
```bash
cd /Users/guillaumebld/Documents/Skills/Skills_librairie
python3 Skills/Meta-skill/skills-store-access/scripts/test-jaat-workflow.py \
  "I need to deploy a Docker stack with database migrations" \
  --use-jaat
```

## Usage Examples

### Example 1: Basic JAAT Extraction

```bash
# Extract standardized skills from a query
python3 scripts/jaat-enhanced-discovery.py \
  "We need a DevOps engineer to deploy microservices on Kubernetes" \
  --json
```

**Output:**
- O*NET tasks: Tasks related to infrastructure deployment
- EuropaCode skills: Standardized skill codes for DevOps, containerization
- Generated search queries: Keywords for catalog matching

### Example 2: Complete Workflow with Auto-Creation

```bash
# Full workflow: query → analysis → gap detection → auto-creation
python3 scripts/test-jaat-workflow.py \
  "Build a RAG pipeline with vector database and semantic search" \
  --use-jaat
```

### Example 3: Gap Detection Only

```bash
# Analyze requirements and detect gaps
python3 scripts/analyze-task-requirements.py \
  "Deploy Docker stack with CI/CD" \
  --use-jaat --json | \
  python3 scripts/detect-skill-gaps.py --json
```

### Example 4: Create Skill from Requirement

```bash
# Generate skill from requirement (dry-run first)
echo '{
  "type": "task",
  "source": "onet",
  "description": "Design and implement API endpoints",
  "priority": "high"
}' | python3 scripts/auto-create-skill.py --dry-run
```

## Troubleshooting

### JAAT Import Errors

**Problem**: `ImportError: No module named 'JAAT'`

**Solution**:
```bash
# Verify installation
pip list | grep -i jaat

# Reinstall if needed
pip install --upgrade JAAT

# Check Python version (requires Python 3.8+)
python3 --version
```

### JAAT Pickling Errors

**Problem**: Pickling errors when extracting tasks/skills

**Known Issue**: JAAT has internal pickling issues with local functions in some versions.

**Workaround**: The system gracefully falls back to keyword-based analysis if JAAT fails. This is handled automatically in `analyze-task-requirements.py`.

**Solution**: Update JAAT to latest version:
```bash
pip install --upgrade JAAT
```

### Missing Dependencies

**Problem**: `ModuleNotFoundError` for requests, beautifulsoup4, etc.

**Solution**:
```bash
pip install -r Skills/Meta-skill/skills-store-access/requirements.txt
```

### Skill Creation Fails

**Problem**: `auto-create-skill.py` fails to create skill structure

**Solution**:
1. Verify `skill-creator/scripts/init_skill.py` exists
2. Check file permissions on Skills directory
3. Run with `--dry-run` first to see what would be created
4. Check error output for specific issues

## Future Enhancements

- **Batch Processing**: Analyze multiple job postings/queries at once
- **Skill Improvement**: Suggest improvements based on usage patterns
- **n8n Integration**: Automated skill creation pipelines via n8n workflows
- **Source Monitoring**: Automatic skill updates when authoritative sources change
- **Quality Scoring**: Automated quality assessment for auto-created skills
- **Validation Pipeline**: Enhanced validation and testing for created skills
- **User Feedback Loop**: Collect feedback on auto-created skills to improve generation
