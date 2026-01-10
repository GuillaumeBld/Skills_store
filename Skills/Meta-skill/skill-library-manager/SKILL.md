---
name: skill-library-manager
description: Manage Claude skills lifecycle with GitHub integration. Create new skills following best practices, store them in GuillaumeBld/Skills_librairie repository, pull existing skills for reuse, search skill catalog by tags/keywords, version management with semantic versioning, and install skills to Claude.ai or local directories. Use when creating skills for your library, searching for existing skills, updating skill versions, syncing with GitHub, or organizing your skill collection. Requires GitHub CLI (gh) for authentication.
---

# Skill Library Manager

Complete lifecycle management for Claude skills with GitHub integration.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Git installed
- Python 3.8+ (for catalog operations)
- Access to https://github.com/GuillaumeBld/Skills_librairie.git

### First-Time Setup

```bash
# 1. Install GitHub CLI (if not already installed)
# macOS: brew install gh
# Linux: See https://github.com/cli/cli/blob/trunk/docs/install_linux.md
# Windows: winget install --id GitHub.cli

# 2. Authenticate
gh auth login

# 3. Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 4. Test access
gh repo view GuillaumeBld/Skills_librairie
```

## Quick Start: Complete Workflow

### 1. Initialize Library (First Use)

```bash
# Clone your Skills_librairie repository
cd ~/
gh repo clone GuillaumeBld/Skills_librairie

# Verify structure
ls ~/Skills_librairie
# Expected: skills/, packaged/, catalog.json, README.md
```

If catalog.json doesn't exist, create it:
```bash
cat > ~/Skills_librairie/catalog.json << 'EOF'
{
  "version": "1.0.0",
  "updated": "2026-01-10",
  "skills": []
}
EOF
```

### 2. Create New Skill

Use `scripts/create-skill.sh` to automate the full workflow.

**Example: Create a PostgreSQL backup skill**

```bash
# Run creation script
cd ~/Skills_librairie
bash ~/path/to/scripts/create-skill.sh

# Interactive prompts:
# Skill name: postgres-backup
# Description: Automate PostgreSQL backups with pg_dump and S3 upload
# Author: Guillaume
# Tags: database, backup, postgresql, s3
# Version: 1.0.0

# Script will:
# 1. Initialize skill structure
# 2. Open editor for SKILL.md
# 3. Validate skill
# 4. Package to .skill file
# 5. Update catalog.json
# 6. Git commit + push
# 7. Create Git tag (postgres-backup-v1.0.0)
```

**Manual workflow:**
```bash
# 1. Create skill structure
python3 /mnt/skills/examples/skill-creator/scripts/init_skill.py postgres-backup --path ~/Skills_librairie/skills

# 2. Edit content
# Add your SKILL.md, scripts/, references/, assets/

# 3. Validate and package
python3 /mnt/skills/examples/skill-creator/scripts/package_skill.py ~/Skills_librairie/skills/postgres-backup ~/Skills_librairie/packaged

# 4. Update catalog (see scripts/catalog-builder.py)
python3 scripts/catalog-builder.py

# 5. Commit and push
git add .
git commit -m "Add postgres-backup skill v1.0.0"
git tag postgres-backup-v1.0.0
git push origin main --tags
```

### 3. Search Skills

```bash
# Search by keyword
python3 scripts/search-skills.py database

# Search by tag
python3 scripts/search-skills.py --tag backup

# List all skills
python3 scripts/search-skills.py --all

# Output example:
# Found 3 skills matching "database":
# 
# 1. postgres-backup (v1.0.0)
#    Description: Automate PostgreSQL backups with pg_dump and S3 upload
#    Tags: database, backup, postgresql, s3
#    Location: skills/postgres-backup/
#    Package: packaged/postgres-backup.skill
#
# 2. mysql-monitoring (v2.1.0)
#    Description: Monitor MySQL performance metrics and slow queries
#    Tags: database, monitoring, mysql
#    ...
```

### 4. Install Skill

**Option A: Install to Claude.ai (Manual)**
```bash
# 1. Locate packaged skill
ls ~/Skills_librairie/packaged/postgres-backup.skill

# 2. Upload in Claude.ai:
#    - Profile → Skills → Upload Skill
#    - Select postgres-backup.skill
#    - Confirm installation
```

**Option B: Install to Local Directory**
```bash
# Create local skills directory
mkdir -p ~/.claude/skills

# Copy skill folder
cp -r ~/Skills_librairie/skills/postgres-backup ~/.claude/skills/

# Or extract .skill package
cd ~/.claude/skills
unzip ~/Skills_librairie/packaged/postgres-backup.skill
```

### 5. Update Existing Skill

```bash
# 1. Make changes to skill
cd ~/Skills_librairie/skills/vps-deployment-stack
# Edit SKILL.md, add scripts, etc.

# 2. Update version in SKILL.md frontmatter
# version: 1.0.0 → 1.1.0

# 3. Update CHANGELOG
echo "## v1.1.0 - 2026-01-15
- Added backup automation scripts
- Improved troubleshooting guide
" >> CHANGELOG.md

# 4. Repackage
python3 /mnt/skills/examples/skill-creator/scripts/package_skill.py ~/Skills_librairie/skills/vps-deployment-stack ~/Skills_librairie/packaged

# 5. Update catalog
cd ~/Skills_librairie
python3 scripts/catalog-builder.py

# 6. Commit with version bump
git add .
git commit -m "Update vps-deployment-stack to v1.1.0"
git tag vps-deployment-stack-v1.1.0
git push origin main --tags
```

### 6. Sync Library

```bash
# Pull latest changes from GitHub
cd ~/Skills_librairie
git pull origin main --tags

# Push local changes
git push origin main --tags
```

## Workflows

### Workflow 1: "I need a skill for X, let me check if I have one"

```bash
# Search your library
python3 ~/Skills_librairie/scripts/search-skills.py "kubernetes deployment"

# If found: Install it
# If not found: Create it (see Workflow 2)
```

### Workflow 2: "Create a new skill and save it"

```bash
# Option A: Automated (recommended)
cd ~/Skills_librairie
bash scripts/create-skill.sh

# Option B: Manual (more control)
# 1. Initialize
python3 /mnt/skills/examples/skill-creator/scripts/init_skill.py my-skill --path ~/Skills_librairie/skills

# 2. Edit content
code ~/Skills_librairie/skills/my-skill/SKILL.md

# 3. Package
python3 /mnt/skills/examples/skill-creator/scripts/package_skill.py ~/Skills_librairie/skills/my-skill ~/Skills_librairie/packaged

# 4. Update catalog
python3 ~/Skills_librairie/scripts/catalog-builder.py

# 5. Commit
cd ~/Skills_librairie
git add .
git commit -m "Add my-skill v1.0.0"
git tag my-skill-v1.0.0
git push origin main --tags
```

### Workflow 3: "Share skill with team"

```bash
# 1. Ensure skill is pushed to GitHub
cd ~/Skills_librairie
git push origin main --tags

# 2. Share repository URL
# Team members clone: gh repo clone GuillaumeBld/Skills_librairie

# 3. Or share packaged .skill file
# Send: ~/Skills_librairie/packaged/my-skill.skill
```

### Workflow 4: "Update skill after improvements"

See section 5 above (Update Existing Skill).

### Workflow 5: "Browse all skills in library"

```bash
# List all with metadata
python3 ~/Skills_librairie/scripts/search-skills.py --all

# View catalog directly
cat ~/Skills_librairie/catalog.json | jq '.skills'

# Browse on GitHub
gh repo view GuillaumeBld/Skills_librairie --web
```

## Repository Structure

Your Skills_librairie repository should follow this structure:

```
Skills_librairie/
├── README.md                          # Library overview
├── catalog.json                       # Searchable skill index
├── skills/                            # Source skills (unpackaged)
│   ├── vps-deployment-stack/
│   │   ├── SKILL.md
│   │   ├── CHANGELOG.md
│   │   ├── scripts/
│   │   ├── references/
│   │   └── assets/
│   ├── docker-workflow/
│   ├── postgres-backup/
│   └── ...
├── packaged/                          # .skill files for distribution
│   ├── vps-deployment-stack.skill
│   ├── docker-workflow.skill
│   ├── postgres-backup.skill
│   └── ...
└── scripts/                           # Management scripts
    ├── create-skill.sh                # Automated skill creation
    ├── catalog-builder.py             # Generate catalog.json
    ├── search-skills.py               # Search catalog
    └── sync-library.sh                # Pull + push wrapper
```

## Catalog Schema

`catalog.json` structure:

```json
{
  "version": "1.0.0",
  "updated": "2026-01-15T10:30:00Z",
  "repository": "https://github.com/GuillaumeBld/Skills_librairie",
  "skills": [
    {
      "name": "vps-deployment-stack",
      "version": "1.1.0",
      "description": "Deploy Dokploy + Traefik + Docker + Kuma with automatic HTTPS",
      "author": "Guillaume",
      "created": "2026-01-10",
      "updated": "2026-01-15",
      "tags": ["devops", "docker", "vps", "deployment", "traefik"],
      "dependencies": [],
      "compatibility": ["claude.ai", "claude-code"],
      "license": "MIT",
      "location": "skills/vps-deployment-stack/",
      "package": "packaged/vps-deployment-stack.skill",
      "size": "45KB"
    },
    {
      "name": "postgres-backup",
      "version": "1.0.0",
      "description": "Automate PostgreSQL backups with pg_dump and S3 upload",
      "author": "Guillaume",
      "created": "2026-01-15",
      "updated": "2026-01-15",
      "tags": ["database", "backup", "postgresql", "s3"],
      "dependencies": [],
      "compatibility": ["claude.ai"],
      "license": "MIT",
      "location": "skills/postgres-backup/",
      "package": "packaged/postgres-backup.skill",
      "size": "12KB"
    }
  ],
  "categories": {
    "devops": ["vps-deployment-stack", "docker-workflow"],
    "database": ["postgres-backup", "mysql-monitoring"],
    "development": ["docker-workflow", "git-automation"]
  }
}
```

## Versioning Strategy

Follow **Semantic Versioning** (semver):

- **Major (x.0.0)**: Breaking changes, incompatible updates
- **Minor (1.x.0)**: New features, backward compatible
- **Patch (1.0.x)**: Bug fixes, minor improvements

**Examples:**
- `1.0.0` → `1.0.1`: Fixed typo in SKILL.md
- `1.0.1` → `1.1.0`: Added new reference file
- `1.1.0` → `2.0.0`: Restructured skill, changed interface

**Git Tags:**
- Format: `{skill-name}-v{version}`
- Example: `postgres-backup-v1.0.0`
- List tags: `git tag -l "postgres-backup-*"`

## GitHub Operations

### Common Commands

```bash
# Clone library
gh repo clone GuillaumeBld/Skills_librairie

# View repository
gh repo view GuillaumeBld/Skills_librairie

# Create issue (for skill requests)
gh issue create --repo GuillaumeBld/Skills_librairie --title "Request: New skill for X"

# List releases
gh release list --repo GuillaumeBld/Skills_librairie

# Create release (for major versions)
gh release create v1.0.0 --repo GuillaumeBld/Skills_librairie --title "Skills Library v1.0.0" --notes "Initial release"

# Sync fork (if working with forks)
gh repo sync GuillaumeBld/Skills_librairie --source upstream/main
```

### Backup Strategy

```bash
# Clone to multiple locations
gh repo clone GuillaumeBld/Skills_librairie ~/Skills_librairie
gh repo clone GuillaumeBld/Skills_librairie ~/Backups/Skills_librairie-$(date +%Y%m%d)

# Or create local archive
cd ~/Skills_librairie
tar -czf ~/Backups/skills-library-$(date +%Y%m%d).tar.gz .
```

## Best Practices

### 1. Skill Naming
- Use kebab-case: `postgres-backup`, `vps-deployment`
- Be descriptive: `docker-dev-workflow` not `docker-skill`
- Avoid generic names: `database-utils` → `postgres-backup-automation`

### 2. Documentation
- Always include SKILL.md with clear description
- Add CHANGELOG.md for version history
- Include README.md in complex skills
- Document prerequisites clearly

### 3. Tagging
- Use 3-5 relevant tags per skill
- Common tags: devops, database, monitoring, backup, security, docker, kubernetes
- Consistent naming: `postgresql` not `postgres`, `backup` not `backups`

### 4. Versioning
- Start at v1.0.0 for production-ready skills
- Use v0.x.x for experimental/beta skills
- Always update CHANGELOG.md with version bumps
- Tag releases in Git

### 5. Organization
- Group related skills in catalog categories
- Keep skills focused (single responsibility)
- Extract common patterns into separate skills
- Document skill dependencies

## Troubleshooting

### Library Not Found
```bash
# Check if cloned
ls ~/Skills_librairie

# If not, clone
gh repo clone GuillaumeBld/Skills_librairie ~/Skills_librairie
```

### GitHub Authentication Failed
```bash
# Re-authenticate
gh auth login

# Check status
gh auth status

# Test access
gh repo view GuillaumeBld/Skills_librairie
```

### Catalog Out of Sync
```bash
# Rebuild catalog from skills
cd ~/Skills_librairie
python3 scripts/catalog-builder.py

# Commit updated catalog
git add catalog.json
git commit -m "Rebuild catalog"
git push
```

### Merge Conflicts
```bash
# Pull latest changes first
git pull origin main

# If conflicts, resolve manually
git status
# Edit conflicting files
git add .
git commit -m "Resolve merge conflicts"
git push
```

### Skill Validation Fails
```bash
# Run validator manually
python3 /mnt/skills/examples/skill-creator/scripts/package_skill.py ~/Skills_librairie/skills/my-skill

# Common issues:
# - Missing SKILL.md
# - Invalid YAML frontmatter
# - Missing name or description
# - Files outside skill directory
```

## Reference Files

- **scripts/create-skill.sh** - Automated skill creation workflow
- **scripts/catalog-builder.py** - Generate/update catalog.json
- **scripts/search-skills.py** - Search catalog by keywords/tags
- **scripts/sync-library.sh** - Git pull + push wrapper
- **references/skill-template.md** - Template for new skills
- **references/github-workflow.md** - Detailed GitHub operations
- **references/versioning-guide.md** - Semantic versioning examples
- **assets/catalog-schema.json** - JSON schema for validation

## Related Skills

- **skill-creator** (Anthropic) - Foundation for creating skills
- **vps-deployment-stack** - Example of well-structured skill
- **docker-development-workflow** - Example with multiple reference files
