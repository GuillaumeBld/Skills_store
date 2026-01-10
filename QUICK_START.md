# Quick Start: Equip Any AI with Skills Librairie

**Simple prompts to equip any AI system with Skills Librairie capabilities**

## 🚀 Universal Prompt (Works with Any AI System)

**Copy and paste this prompt:**

```
Read and follow the instructions from: https://raw.githubusercontent.com/GuillaumeBld/Skills_librairie/main/Skills/Meta-skill/skills-store-access/SKILL.md

After reading, equip yourself with Skills Librairie access by:
1. Installing the skill-library-manager skill from this repository
2. Generating the skills discovery index
3. Verifying you can discover and use skills from the Skills_librairie repository

The repository is at: https://github.com/GuillaumeBld/Skills_librairie
Main entry point: Skills/Meta-skill/skills-store-access/
```

## 🎯 Platform-Specific Prompts

### For Claude Code / Cursor (Codex)

**Simple one-liner:**

```
Install the skills-store-access skill from https://github.com/GuillaumeBld/Skills_librairie/tree/main/Skills/Meta-skill/skills-store-access and equip yourself with Skills Librairie capabilities
```

**Or more detailed:**

```
Please equip yourself with Skills Librairie access:

1. Install the skills-store-access skill using the skill-installer:
   Repository: https://github.com/GuillaumeBld/Skills_librairie
   Path: Skills/Meta-skill/skills-store-access

2. After installation, run the equip script:
   bash Skills/Meta-skill/skills-store-access/scripts/equip-skills-store.sh

3. Generate the discovery index:
   python3 Skills/Meta-skill/skills-store-access/scripts/generate-skills-index.py

4. Verify installation:
   python3 Skills/Meta-skill/skills-store-access/scripts/verify-installation.py

Once equipped, you should be able to discover and use skills from the Skills_librairie repository.
```

### For Claude.ai (Web Interface)

**Prompt for web interface:**

```
I want to equip you with Skills Librairie access. Please read the following skill and follow its instructions:

URL: https://raw.githubusercontent.com/GuillaumeBld/Skills_librairie/main/Skills/Meta-skill/skills-store-access/SKILL.md

After reading, help me:
1. Clone the repository locally (or download it)
2. Navigate to Skills/Meta-skill/skills-store-access/
3. Prepare the skill for upload via Claude.ai UI (Settings → Skills → Upload Skill)

The repository contains organized skills by category that will enable you to work more effectively across various domains.
```

**After reading the skill, the AI will guide you through the upload process.**

### For Claude API (Programmatic)

**Prompt/instruction:**

```
Use the Anthropic API to upload the skills-store-access skill from:
https://github.com/GuillaumeBld/Skills_librairie/tree/main/Skills/Meta-skill/skills-store-access

After uploading, use the returned skill_id to include this skill in subsequent API requests.

The skill will enable you to discover and use skills from the Skills_librairie repository.
```

**API code example:**

```python
import anthropic
import requests
import zipfile
import os

# Step 1: Clone or download the repository
# (Do this manually or with git)

# Step 2: Create zip of skills-store-access
os.chdir('Skills_librairie/Skills/Meta-skill')
with zipfile.ZipFile('skills-store-access.zip', 'w') as zipf:
    for root, dirs, files in os.walk('skills-store-access'):
        for file in files:
            zipf.write(os.path.join(root, file))

# Step 3: Upload via API
client = anthropic.Anthropic(api_key="your-api-key")
# See API docs for upload endpoint
```

### For Any AI System (Universal Approach)

**Most universal prompt (works even if AI can't execute scripts):**

```
I want you to access the Skills Librairie repository and equip yourself with its capabilities.

Repository: https://github.com/GuillaumeBld/Skills_librairie

Main entry point: Skills/Meta-skill/skills-store-access/SKILL.md

Please:
1. Read the skills-store-access skill file from the repository
2. Understand how it enables AI systems to discover and use skills
3. Based on your capabilities, implement or follow the appropriate installation method
4. Once equipped, let me know you're ready to discover and use skills from the repository

The repository contains organized skills including:
- superpowers: Foundational workflow skills (TDD, systematic debugging, collaborative planning)
- Community skills: ios-simulator-skill, playwright-skill, claude-d3js-skill, and more
- Skills organized by category: Meta-skill, Development, Design-Creative, Security, Scientific, AI-Agents, etc.
```

## 📋 What Happens After Equipping

Once the AI is equipped with skills-store-access, it will be able to:

1. **Discover skills intelligently** - Use lightweight index to find relevant skills for tasks
2. **Install skills proactively** - Automatically install skills for ongoing projects
3. **Use skills systematically** - Follow superpowers methodology (TDD, systematic debugging, etc.)
4. **Manage skills lifecycle** - Create, search, update, sync skills in the repository

## 🔧 Verification Prompt

**After equipping, verify with this prompt:**

```
Now that you're equipped with Skills Librairie access:

1. List the categories of skills available in the repository
2. Search for skills related to [your domain/task]
3. Show me how to use a specific skill (e.g., superpowers or ios-simulator-skill)
4. Demonstrate the discovery system by finding relevant skills for a sample task

Repository location: https://github.com/GuillaumeBld/Skills_librairie
```

## 💡 Example: Equipping for a Specific Task

**If you want the AI to equip itself for a specific task:**

```
I need you to work on [iOS app development / web automation / data visualization / etc.].

Please equip yourself with Skills Librairie access and specifically install/use these relevant skills:
- [skill name 1]
- [skill name 2]
- superpowers (for systematic workflows)

Repository: https://github.com/GuillaumeBld/Skills_librairie
Entry point: Skills/Meta-skill/skills-store-access/

Once equipped, let me know which skills you've activated and how they'll help with this task.
```

## 🎓 Using superpowers Skill

**To specifically equip with superpowers workflow methodology:**

```
Read and follow the superpowers skill from Skills Librairie:
https://raw.githubusercontent.com/GuillaumeBld/Skills_librairie/main/Skills/Meta-skill/superpowers/SKILL.md

This will teach you how to use skills to their best capabilities using:
- Test-Driven Development (TDD)
- Systematic debugging
- Collaborative planning
- Proper code review practices

Once you've read it, confirm you understand the workflow and are ready to use it.
```

## 📝 Shortest Possible Prompt

**Absolute minimum (for Claude Code/Cursor):**

```
Equip yourself with Skills Librairie: https://github.com/GuillaumeBld/Skills_librairie/tree/main/Skills/Meta-skill/skills-store-access
```

**Or even shorter:**

```
Install skills-store-access from GuillaumeBld/Skills_librairie
```

## 🔗 Reference Links

- **Repository**: https://github.com/GuillaumeBld/Skills_librairie
- **Main Entry Point**: https://github.com/GuillaumeBld/Skills_librairie/tree/main/Skills/Meta-skill/skills-store-access
- **Raw SKILL.md**: https://raw.githubusercontent.com/GuillaumeBld/Skills_librairie/main/Skills/Meta-skill/skills-store-access/SKILL.md
- **superpowers Skill**: https://raw.githubusercontent.com/GuillaumeBld/Skills_librairie/main/Skills/Meta-skill/superpowers/SKILL.md
- **README**: https://raw.githubusercontent.com/GuillaumeBld/Skills_librairie/main/README.md

## ⚡ Quick Copy-Paste Templates

### Template 1: Universal Equip
```
Equip yourself with Skills Librairie capabilities by reading and following:
https://raw.githubusercontent.com/GuillaumeBld/Skills_librairie/main/Skills/Meta-skill/skills-store-access/SKILL.md

Repository: https://github.com/GuillaumeBld/Skills_librairie
```

### Template 2: Equip + Use superpowers
```
Equip yourself with Skills Librairie and specifically use the superpowers skill for systematic workflows:
- https://raw.githubusercontent.com/GuillaumeBld/Skills_librairie/main/Skills/Meta-skill/skills-store-access/SKILL.md
- https://raw.githubusercontent.com/GuillaumeBld/Skills_librairie/main/Skills/Meta-skill/superpowers/SKILL.md
```

### Template 3: Equip for Specific Domain
```
Equip yourself with Skills Librairie and activate skills for [DOMAIN]:
Repository: https://github.com/GuillaumeBld/Skills_librairie
After equipping, discover and use relevant skills for [your specific task/domain]
```

---

**Remember**: The AI will automatically adapt to its platform (Claude Code, Claude.ai, API, etc.) once it reads the skills-store-access skill.
