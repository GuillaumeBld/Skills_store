# GitHub Workflow Guide

Complete guide for managing your Skills_librairie repository with GitHub CLI.

## Initial Setup

### 1. Install GitHub CLI

**macOS:**
```bash
brew install gh
```

**Linux (Debian/Ubuntu):**
```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

**Windows:**
```bash
winget install --id GitHub.cli
```

### 2. Authenticate

```bash
# Login interactively
gh auth login

# Select prompts:
# - GitHub.com
# - HTTPS
# - Authenticate Git with GitHub credentials: Yes
# - How to authenticate: Login with web browser
# - Copy one-time code and open browser
```

Verify:
```bash
gh auth status
# ✓ Logged in to github.com as GuillaumeBld
```

### 3. Clone Repository

```bash
# Clone to default location
gh repo clone GuillaumeBld/Skills_librairie

# Or specify location
gh repo clone GuillaumeBld/Skills_librairie ~/Skills_librairie
```

## Daily Workflows

### Check Repository Status

```bash
cd ~/Skills_librairie

# View repository info
gh repo view

# Check branches
git branch -a

# Check remote
git remote -v
```

### Pull Latest Changes

```bash
# Pull main branch
git pull origin main

# Pull with tags
git pull origin main --tags

# Or use gh
gh repo sync
```

### Create and Push Changes

```bash
# Stage changes
git add .

# Commit
git commit -m "Add new skill for X"

# Push to GitHub
git push origin main

# Push tags
git push origin main --tags
```

### Create Branches

```bash
# Create feature branch
git checkout -b feature/new-skill

# Push branch
git push -u origin feature/new-skill

# View branches on GitHub
gh pr create
```

## Skill Management

### Add New Skill

```bash
# 1. Create skill
cd ~/Skills_librairie
python3 /mnt/skills/examples/skill-creator/scripts/init_skill.py my-skill --path skills/

# 2. Edit content
code skills/my-skill/SKILL.md

# 3. Package
python3 /mnt/skills/examples/skill-creator/scripts/package_skill.py skills/my-skill packaged/

# 4. Update catalog
python3 scripts/catalog-builder.py

# 5. Commit
git add .
git commit -m "Add my-skill v1.0.0"

# 6. Tag
git tag my-skill-v1.0.0

# 7. Push
git push origin main --tags
```

### Update Existing Skill

```bash
# 1. Make changes
cd ~/Skills_librairie/skills/my-skill
# Edit files...

# 2. Update version in SKILL.md frontmatter
# version: 1.0.0 → 1.1.0

# 3. Update CHANGELOG
echo "## v1.1.0 - $(date +%Y-%m-%d)
- Feature added
- Bug fixed
" >> CHANGELOG.md

# 4. Repackage
cd ~/Skills_librairie
python3 /mnt/skills/examples/skill-creator/scripts/package_skill.py skills/my-skill packaged/

# 5. Update catalog
python3 scripts/catalog-builder.py

# 6. Commit with version
git add .
git commit -m "Update my-skill to v1.1.0

- Feature added
- Bug fixed"

# 7. Tag new version
git tag my-skill-v1.1.0

# 8. Push
git push origin main --tags
```

### Remove Skill

```bash
# 1. Remove from skills/
git rm -r skills/my-skill

# 2. Remove package
git rm packaged/my-skill.skill

# 3. Update catalog
python3 scripts/catalog-builder.py

# 4. Commit
git commit -m "Remove my-skill (deprecated)"

# 5. Push
git push origin main
```

## Tagging Strategy

### Version Tags

Format: `{skill-name}-v{version}`

```bash
# Create tag
git tag postgres-backup-v1.0.0

# Create annotated tag with message
git tag -a postgres-backup-v1.0.0 -m "PostgreSQL backup automation v1.0.0

Features:
- Automated pg_dump
- S3 upload
- Retention policy"

# Push specific tag
git push origin postgres-backup-v1.0.0

# Push all tags
git push origin --tags
```

### List Tags

```bash
# All tags
git tag

# Tags for specific skill
git tag -l "postgres-backup-*"

# Sort by date
git tag --sort=-creatordate

# View tag details
git show postgres-backup-v1.0.0
```

### Delete Tags

```bash
# Delete local tag
git tag -d postgres-backup-v1.0.0

# Delete remote tag
git push origin --delete postgres-backup-v1.0.0
```

## GitHub Releases

### Create Release

```bash
# Create release from tag
gh release create postgres-backup-v1.0.0 \
  --title "PostgreSQL Backup v1.0.0" \
  --notes "Automated PostgreSQL backups with S3 integration

Features:
- pg_dump automation
- S3 upload
- Configurable retention
- Email notifications"

# Attach packaged skill
gh release create postgres-backup-v1.0.0 \
  --title "PostgreSQL Backup v1.0.0" \
  --notes "See CHANGELOG.md" \
  packaged/postgres-backup.skill
```

### List Releases

```bash
# List all releases
gh release list

# View specific release
gh release view postgres-backup-v1.0.0
```

### Download Release

```bash
# Download latest release
gh release download

# Download specific version
gh release download postgres-backup-v1.0.0

# Download specific asset
gh release download postgres-backup-v1.0.0 -p "*.skill"
```

## Issues and Projects

### Create Issue

```bash
# Interactive issue creation
gh issue create

# With parameters
gh issue create \
  --title "Add MySQL backup skill" \
  --body "Need skill for MySQL backups similar to postgres-backup" \
  --label "enhancement,skill-request"
```

### List Issues

```bash
# All open issues
gh issue list

# Filter by label
gh issue list --label skill-request

# Filter by assignee
gh issue list --assignee @me
```

### Close Issue

```bash
# Close with comment
gh issue close 5 --comment "Implemented in v2.0.0"
```

## Collaboration

### Forking

```bash
# Fork repository
gh repo fork GuillaumeBld/Skills_librairie

# Clone your fork
gh repo clone YOUR_USERNAME/Skills_librairie
```

### Pull Requests

```bash
# Create PR from current branch
gh pr create

# With parameters
gh pr create \
  --title "Add Kubernetes deployment skill" \
  --body "New skill for K8s deployments" \
  --base main

# List PRs
gh pr list

# View PR
gh pr view 123

# Checkout PR locally
gh pr checkout 123

# Merge PR
gh pr merge 123 --squash
```

## Repository Management

### View Repository

```bash
# View in terminal
gh repo view GuillaumeBld/Skills_librairie

# Open in browser
gh repo view GuillaumeBld/Skills_librairie --web

# View README
gh repo view GuillaumeBld/Skills_librairie --readme
```

### Clone/Archive

```bash
# Clone
gh repo clone GuillaumeBld/Skills_librairie

# Archive (make read-only)
gh repo archive GuillaumeBld/Skills_librairie

# Unarchive
gh repo unarchive GuillaumeBld/Skills_librairie
```

### Edit Repository Settings

```bash
# Edit description
gh repo edit GuillaumeBld/Skills_librairie \
  --description "Personal collection of Claude AI skills"

# Edit homepage
gh repo edit GuillaumeBld/Skills_librairie \
  --homepage "https://guillaumebld.github.io/skills"

# Enable/disable features
gh repo edit GuillaumeBld/Skills_librairie \
  --enable-issues \
  --enable-projects \
  --enable-wiki
```

## Advanced Git Operations

### Stash Changes

```bash
# Stash current work
git stash

# List stashes
git stash list

# Apply stash
git stash pop

# Apply specific stash
git stash apply stash@{0}
```

### Revert Changes

```bash
# Undo last commit (keep changes)
git reset HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Revert specific commit
git revert abc123def
```

### Cherry-pick

```bash
# Apply commit from another branch
git cherry-pick abc123def
```

### Clean Up

```bash
# Remove untracked files (dry run)
git clean -n

# Remove untracked files
git clean -f

# Remove untracked files and directories
git clean -fd
```

## Backup Strategies

### Clone Backups

```bash
# Clone to backup location
gh repo clone GuillaumeBld/Skills_librairie ~/Backups/Skills_librairie-$(date +%Y%m%d)

# Create archive
cd ~/Skills_librairie
tar -czf ~/Backups/skills-$(date +%Y%m%d).tar.gz .
```

### Mirror Repository

```bash
# Clone with all refs
git clone --mirror https://github.com/GuillaumeBld/Skills_librairie.git

# Update mirror
cd Skills_librairie.git
git fetch --all
```

## Troubleshooting

### Authentication Issues

```bash
# Re-authenticate
gh auth logout
gh auth login

# Check status
gh auth status

# Refresh token
gh auth refresh
```

### Merge Conflicts

```bash
# Pull changes
git pull origin main
# CONFLICT (content): Merge conflict in catalog.json

# View conflicts
git status

# Edit conflicting files
# Look for <<<<<<< HEAD markers

# After resolving
git add catalog.json
git commit -m "Resolve merge conflict in catalog"
```

### Push Rejected

```bash
# If remote has changes you don't have
git pull origin main --rebase
git push origin main
```

### Large Files

```bash
# Check file sizes
git ls-tree -r -t -l --full-name HEAD | sort -n -k 4 | tail -n 10

# Remove large file from history (use with caution)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/large/file' \
  --prune-empty --tag-name-filter cat -- --all
```

## Best Practices

### Commit Messages

Good format:
```
Add postgres-backup skill v1.0.0

- Automated pg_dump backups
- S3 upload with encryption
- Configurable retention (7/30/90 days)
- Email notifications on failure

Closes #42
```

### Branch Naming

```bash
# Feature branches
git checkout -b feature/mysql-backup-skill

# Bug fixes
git checkout -b fix/catalog-validation

# Documentation
git checkout -b docs/update-readme
```

### Tagging Convention

```bash
# Skill version tags
{skill-name}-v{major}.{minor}.{patch}

# Examples
postgres-backup-v1.0.0
postgres-backup-v1.1.0
postgres-backup-v2.0.0

# Library version tags (optional)
library-v1.0.0
```

## Automation Scripts

### Auto-sync Script

```bash
#!/bin/bash
# ~/scripts/sync-skills.sh

cd ~/Skills_librairie
git pull origin main --tags
python3 scripts/catalog-builder.py
echo "Library synced at $(date)"
```

Schedule with cron:
```bash
# Sync daily at 9 AM
0 9 * * * ~/scripts/sync-skills.sh >> ~/logs/sync-skills.log 2>&1
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Rebuild catalog before commit
python3 scripts/catalog-builder.py

# Stage catalog if changed
git add catalog.json
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```
