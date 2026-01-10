# Platform Guide: Skills Store Access in Practice

This guide explains how the Skills Store Access system works across different platforms and how to ensure it works properly.

## How It Works Across Platforms

### Cursor / Claude Code (Codex)

**How it works:**
1. Skills are stored in `~/.codex/skills/` (or `$CODEX_HOME/skills/`)
2. Skills are automatically loaded on IDE startup
3. Skills are detected by reading `SKILL.md` frontmatter (name + description)
4. When user's query matches description, skill is loaded into context

**Installation:**
```bash
# Platform automatically detected as "codex"
bash equip-skills-store.sh

# This will:
# 1. Detect platform (codex)
# 2. Use skill-installer if available (recommended)
# 3. Fall back to manual copy if needed
# 4. Install to ~/.codex/skills/skill-library-manager/
# 5. Verify installation
```

**Verification:**
- After installation, **full IDE restart is required** (not just reload window)
- Skills load on startup, so changes take effect after restart
- Check: `ls ~/.codex/skills/skill-library-manager/` should show SKILL.md

**Testing:**
- Ask in IDE: "Use the skill-library-manager to search for database skills"
- The skill should automatically trigger based on description match
- If not working, check SKILL.md frontmatter description includes relevant keywords

### Claude.ai (Web Interface)

**How it works:**
1. Skills are managed through web UI (Settings → Skills)
2. Skills must be uploaded as folders or zip files
3. Claude.ai analyzes SKILL.md frontmatter to determine when to use skill
4. Skills are stored on Anthropic servers, not locally

**Installation:**
```bash
# Option 1: Clone and zip
gh repo clone GuillaumeBld/Skills_librairie
cd Skills_librairie/Skills
zip -r skill-library-manager.zip skill-library-manager/

# Option 2: Use equip script to prepare (but won't auto-install)
# Then manually upload via Claude.ai UI:
# 1. Go to https://claude.ai
# 2. Settings → Skills → Upload Skill
# 3. Select skill-library-manager folder or zip
```

**Verification:**
- Check Claude.ai Settings → Skills to see if skill appears
- Verify skill description matches what's in SKILL.md frontmatter
- Try asking Claude.ai: "Use the skill-library-manager to list skills"

**Testing:**
- Skills work immediately after upload (no restart needed)
- Test by asking questions that match skill description
- If skill doesn't trigger, description may need more specific keywords

### Claude API (Programmatic)

**How it works:**
1. Skills are uploaded via API endpoints
2. API returns skill ID after upload
3. Skill ID is used in API requests via `skill_ids` parameter
4. Skills are stored on Anthropic servers

**Installation:**
```python
import anthropic
import requests

# Upload skill via API
client = anthropic.Anthropic(api_key="your-api-key")

# Note: Actual API may differ, check Anthropic docs
# Skills are typically uploaded as zip files
# See: https://docs.anthropic.com/en/api/skills-guide
```

**Verification:**
- API returns skill ID after successful upload
- Save skill ID for use in subsequent requests
- Verify skill ID is valid by using it in an API call

**Testing:**
- Make API request with `skill_ids` parameter
- Verify response indicates skill was used
- Check API documentation for skill usage patterns

## Ensuring It Works Properly

### Step-by-Step Validation Process

#### 1. Platform Detection
```bash
python3 detect-platform.py
```
**What to check:**
- Platform is correctly detected (codex/claude-ai/api)
- Skills directory path is correct
- Required tools are available (git, gh, python3)

#### 2. Installation
```bash
bash equip-skills-store.sh
```
**What to check:**
- Installation completes without errors
- Script detects platform correctly
- Uses appropriate installation method
- Reports success at end

#### 3. Verification
```bash
python3 verify-installation.py
```
**What to check:**
- All checks pass (green checkmarks)
- No critical issues (red X marks)
- Warnings are acceptable (yellow warnings)
- Skills directory exists and is accessible

#### 4. Functional Testing
```bash
bash test-skills-store.sh
```
**What to check:**
- All tests pass
- Repository is accessible
- Scripts are executable
- Python dependencies are available

#### 5. Runtime Testing
**For Codex/Cursor:**
- Restart IDE completely
- Ask: "Use skill-library-manager to search for skills"
- Skill should trigger automatically

**For Claude.ai:**
- Upload via UI
- Check Settings → Skills shows skill
- Ask: "Use skill-library-manager to list all skills"

**For API:**
- Upload via API, save skill ID
- Make request with skill_id parameter
- Verify skill is used in response

### Common Issues and Solutions

#### Issue: Skill installed but not triggering

**For Codex/Cursor:**
- **Cause**: IDE not restarted after installation
- **Solution**: Full restart required (quit and reopen IDE)
- **Check**: Verify skill exists at `~/.codex/skills/skill-library-manager/`

**For Claude.ai:**
- **Cause**: Description too vague or doesn't match query
- **Solution**: Update SKILL.md frontmatter description with more specific keywords
- **Check**: Review description in Settings → Skills

**For API:**
- **Cause**: Skill ID not included in request or incorrect
- **Solution**: Verify skill ID is correct and included in request
- **Check**: Review API response to confirm skill usage

#### Issue: Repository access fails

**Symptoms:**
- Can't clone repository
- Scripts fail to find repository
- GitHub authentication errors

**Solutions:**
```bash
# Re-authenticate GitHub CLI
gh auth login

# Verify authentication
gh auth status

# Test repository access
gh repo view GuillaumeBld/Skills_librairie

# Alternative: Use Git directly
git clone https://github.com/GuillaumeBld/Skills_librairie.git
```

#### Issue: Scripts fail to execute

**Symptoms:**
- Permission denied errors
- Python import errors
- Missing dependencies

**Solutions:**
```bash
# Fix permissions
chmod +x scripts/*.sh scripts/*.py

# Install Python dependencies
pip install pyyaml

# Verify Python version (3.8+ required)
python3 --version

# Check script paths are correct
which python3
```

### Platform-Specific Best Practices

#### Codex/Cursor
- ✅ Always restart IDE after skill installation
- ✅ Use skill-installer when available (most reliable)
- ✅ Keep skills directory in sync with repository
- ✅ Test skills immediately after installation
- ❌ Don't edit skills while IDE is running (changes won't load)

#### Claude.ai
- ✅ Upload skills via web UI (easiest method)
- ✅ Verify skill appears in Settings → Skills
- ✅ Test immediately after upload (no restart needed)
- ✅ Update description if skill doesn't trigger
- ❌ Don't expect local file access (skills are server-side)

#### API
- ✅ Save skill IDs after upload
- ✅ Include skill_ids in API requests
- ✅ Monitor API responses for skill usage
- ✅ Check API documentation for updates
- ❌ Don't assume skills work the same as UI

## Continuous Verification

### Daily Checks
- Verify repository is accessible: `gh repo view GuillaumeBld/Skills_librairie`
- Check skill is still installed: `ls ~/.codex/skills/skill-library-manager/` (for Codex)
- Test basic functionality: Search for a skill

### Weekly Checks
- Run full test suite: `bash test-skills-store.sh`
- Update catalog if skills changed: `python3 catalog-builder.py`
- Sync with GitHub: `bash sync-library.sh`
- Review any errors in verification output

### Monthly Checks
- Review platform detection output (platforms may change)
- Update documentation if platform changes
- Check for skill system updates from Anthropic
- Verify all scripts still work with latest versions

## Summary

**Key Points:**
1. Platform detection is critical - always run `detect-platform.py` first
2. Installation method varies by platform - equip script handles this
3. Verification is essential - run `verify-installation.py` after installation
4. Testing confirms everything works - use `test-skills-store.sh`
5. Platform-specific behavior differs - follow platform guide for your environment

**Remember:**
- Codex/Cursor: Full restart required after installation
- Claude.ai: Skills work immediately after upload
- API: Skills require skill IDs in requests
- All platforms: Description in SKILL.md frontmatter determines when skill triggers
