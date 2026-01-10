# Using skills-store-access with ANY System

## Overview

The **skills-store-access** skill is the **main piece** of the Skills_librairie repository. It is designed to work with **any system** that supports Claude skills, automatically adapting to your platform without manual configuration.

## Universal Compatibility

### Supported Systems (Tested)

✅ **Claude Code / Cursor (Codex)**
- Full support with local scripts and file system access
- Platform detection: `codex`
- Installation: `~/.codex/skills/` directory
- Discovery: Local repository search

✅ **Claude.ai (Web Interface)**
- Full support via web UI
- Platform detection: `claude-ai` (if env var set)
- Installation: Settings → Skills → Upload
- Discovery: Server-side skill access

✅ **Claude API (Programmatic)**
- Full support via API endpoints
- Platform detection: `api` (if API key present)
- Installation: API upload endpoints
- Discovery: Skill IDs in API requests

✅ **Any Other System**
- Auto-detects platform and capabilities
- Adaptive installation methods
- Unified interface across platforms

### How It Works with Any System

**The Magic**: Platform detection and adaptation happen automatically.

```
User: "Go equip yourself with skills store"
  ↓
System detects platform automatically
  ↓
Uses appropriate installation method
  ↓
Verifies installation worked
  ↓
Ready to use - no manual configuration needed
```

## Installation for Any System

### Universal Installation Method

```bash
# This works on ANY system - auto-detects platform
bash Skills/Meta-skill/skills-store-access/scripts/equip-skills-store.sh
```

**What happens:**
1. Detects your platform (Codex/Cursor/Claude.ai/API/etc.)
2. Finds appropriate installation method
3. Installs skill-library-manager
4. Verifies installation
5. Reports success with platform-specific next steps

### System-Specific Details

**Claude Code / Cursor:**
- Detects: `codex` platform
- Uses: skill-installer if available, or manual copy
- Location: `~/.codex/skills/skill-library-manager/`
- After: Restart IDE

**Claude.ai:**
- Detects: `claude-ai` platform (or manual)
- Uses: Web UI upload
- Location: Anthropic servers
- After: Available immediately

**Claude API:**
- Detects: `api` platform (if API key present)
- Uses: API upload endpoints
- Location: Anthropic servers (via API)
- After: Use skill_id in requests

**Any System:**
- Detects: Platform capabilities
- Uses: Best available method
- Adapts: To system constraints
- Works: With minimal requirements

## Discovery Works the Same Everywhere

The discovery system is **platform-agnostic**:

```bash
# Same command works on ANY system
python3 Skills/Meta-skill/skills-store-access/scripts/discover-skills.py "docker deployment"

# Returns same results regardless of platform
# Uses lightweight index (skills-index.json)
# No platform-specific code needed
```

## Platform Detection

### Automatic Detection

```bash
python3 Skills/Meta-skill/skills-store-access/scripts/detect-platform.py
```

**Output:**
```
Platform Detection Results:
  Platform: codex (or claude-ai, api, unknown)
  Skills Directory: /path/to/skills
  Has Skill Installer: True/False
  Has GitHub CLI: True/False
  Has Git: True/False
  Can Install Local: True/False
  Can Use API: True/False
  Recommended Method: skill-installer (or manual-local, api, etc.)
```

### Manual Override

If auto-detection fails, you can manually specify:

```bash
# Set environment variables
export CODEX_HOME=~/.codex
export PLATFORM=codex

# Or specify repository location
export LIBRARY_ROOT=/path/to/Skills_librairie

# Then run equip script
bash Skills/Meta-skill/skills-store-access/scripts/equip-skills-store.sh
```

## Verification for Any System

### Universal Verification

```bash
# Same verification script works everywhere
python3 Skills/Meta-skill/skills-store-access/scripts/verify-installation.py
```

**Checks:**
- Skills directory exists (platform-specific location)
- skill-library-manager is installed
- SKILL.md is present
- Required scripts exist
- Repository access is available

**Output adapts to platform:**
- Codex/Cursor: Checks `~/.codex/skills/`
- Claude.ai: Checks server-side location (if accessible)
- API: Verifies skill_id is valid

## Using Skills Store Capabilities

### Discovery (Same Everywhere)

```bash
# Discover relevant skills
python3 Skills/Meta-skill/skills-store-access/scripts/discover-skills.py "your query"

# Analyze task requirements
python3 Skills/Meta-skill/skills-store-access/scripts/analyze-task-requirements.py "task description"
```

**Works identically on:**
- ✅ Codex/Cursor (local scripts)
- ✅ Claude.ai (if scripts accessible)
- ✅ API (if scripts accessible)
- ✅ Any system with Python 3.8+

### Skill Management (Platform-Specific)

**Creating Skills:**
- Codex/Cursor: Use local scripts directly
- Claude.ai: Use web UI or upload created skills
- API: Create via API or upload created skills

**Installing Skills:**
- Codex/Cursor: Use skill-installer or copy to `~/.codex/skills/`
- Claude.ai: Upload via web UI
- API: Upload via API endpoints

**Using Skills:**
- **All platforms**: Skills trigger automatically via Claude's built-in system
- No platform-specific code needed
- Description matching works the same everywhere

## Platform-Specific Workflows

### Claude Code / Cursor Workflow

```bash
# 1. Install skills-store-access
bash Skills/Meta-skill/skills-store-access/scripts/equip-skills-store.sh

# 2. Restart IDE

# 3. Use discovery
python3 Skills/Meta-skill/skills-store-access/scripts/discover-skills.py "query"

# 4. Skills auto-trigger based on description match
```

### Claude.ai Workflow

```
# 1. Clone repository
gh repo clone GuillaumeBld/Skills_librairie

# 2. Zip skills-store-access
cd Skills_librairie/Skills/Meta-skill/skills-store-access
zip -r skills-store-access.zip .

# 3. Upload via Claude.ai UI
# Settings → Skills → Upload Skill → Select skills-store-access.zip

# 4. Skills available immediately
# Discovery happens through skill itself
```

### Claude API Workflow

```python
# 1. Upload skill via API
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

# Upload skills-store-access skill
# (See Anthropic API docs for exact endpoint)

# 2. Use skill_id in requests
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    skill_ids=["skill-id-here"],
    messages=[{"role": "user", "content": "Discover skills for docker deployment"}]
)
```

### Any System Workflow

```bash
# 1. Detect platform
python3 Skills/Meta-skill/skills-store-access/scripts/detect-platform.py

# 2. Install using detected method
bash Skills/Meta-skill/skills-store-access/scripts/equip-skills-store.sh

# 3. Verify
python3 Skills/Meta-skill/skills-store-access/scripts/verify-installation.py

# 4. Use capabilities
# Discovery, installation, management all work the same
```

## Key Principles

### Platform-Agnostic Design

1. **Auto-Detection**: Platform is detected automatically
2. **Adaptive Installation**: Uses best method for platform
3. **Unified Interface**: Same scripts work everywhere
4. **No Configuration**: Just install and use

### System Requirements (Minimal)

**Required:**
- Python 3.8+ (for discovery scripts)
- Git (for repository operations)
- Access to Skills_librairie repository

**Optional (Recommended):**
- GitHub CLI (`gh`) - Easier GitHub operations
- Claude Code/Cursor - Development-friendly
- Claude.ai account - Web interface access
- Claude API key - Programmatic access

### What's the Same Across Platforms

✅ **Discovery System** - Same lightweight index, same search
✅ **Task Analysis** - Same complexity/domain detection
✅ **Proactive Installation** - Same decision logic
✅ **Skill Usage** - Same auto-triggering via description match
✅ **Lifecycle Management** - Same create/search/update workflows

### What's Different Across Platforms

🔧 **Installation Method** - Adapts to platform capabilities
🔧 **Skills Location** - Platform-specific paths (handled automatically)
🔧 **Access Method** - Local files vs web UI vs API (auto-detected)
🔧 **Verification** - Platform-specific checks (handled automatically)

## Troubleshooting Across Platforms

### Issue: Platform Not Detected

```bash
# Manual detection
python3 Skills/Meta-skill/skills-store-access/scripts/detect-platform.py

# Check environment variables
echo $CODEX_HOME
echo $PLATFORM

# Set manually if needed
export CODEX_HOME=~/.codex
export PLATFORM=codex
```

### Issue: Installation Fails

```bash
# Try manual method
cd Skills_librairie
cp -r Skills/Meta-skill/skills-store-access ~/.codex/skills/

# Verify
python3 Skills/Meta-skill/skills-store-access/scripts/verify-installation.py
```

### Issue: Discovery Not Working

```bash
# Regenerate index
python3 Skills/Meta-skill/skills-store-access/scripts/generate-skills-index.py

# Test discovery
python3 Skills/Meta-skill/skills-store-access/scripts/discover-skills.py "test"
```

## Summary

**The skills-store-access skill:**

✅ **Works with ANY system** supporting Claude skills
✅ **Auto-detects platform** - No manual configuration
✅ **Adapts installation** - Uses appropriate method
✅ **Unified interface** - Same scripts everywhere
✅ **No system-specific code** - Pure Python, platform-agnostic
✅ **Maintains /Skills structure** - Organized by category
✅ **Foundation of repository** - Everything builds on this

**Key Differentiator:**
Unlike other skill management systems that are platform-specific, this works **universally** - install once, works everywhere, same interface, same capabilities.

**Start Here**: Install [skills-store-access](../../../Skills/Meta-skill/skills-store-access/) and your system is ready to use the complete Skills store!
