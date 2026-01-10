# Skill Template

Use this template when creating new skills for your library.

## SKILL.md Template

```markdown
---
name: skill-name-here
description: Brief one-sentence description of what the skill does and when to use it
version: 1.0.0
author: Your Name
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2, tag3]
dependencies: []
compatibility: [claude.ai, claude-code]
license: MIT
---

# Skill Name Here

One paragraph overview of what this skill accomplishes.

## Prerequisites

- Requirement 1
- Requirement 2
- Requirement 3

## Quick Start: Main Workflow

### 1. First Step (Est. time)

Brief explanation of what this step does.

\`\`\`bash
# Commands to execute
command here
\`\`\`

Expected output or result.

### 2. Second Step (Est. time)

Continue with numbered steps...

\`\`\`bash
more commands
\`\`\`

## Common Workflows

### Workflow 1: Specific Use Case

Step-by-step instructions for this workflow.

### Workflow 2: Another Use Case

Alternative workflow for different scenario.

## Validation

How to verify the skill worked correctly:

\`\`\`bash
# Check commands
validation command
\`\`\`

Expected results.

## Troubleshooting

### Issue 1: Common Problem

**Symptoms:** What user sees

**Fix:**
\`\`\`bash
solution commands
\`\`\`

### Issue 2: Another Problem

**Diagnosis:**
\`\`\`bash
diagnostic commands
\`\`\`

**Resolution:**
Steps to fix.

## Reference Files

- **scripts/script-name.sh** - Brief description
- **references/guide-name.md** - Brief description
- **assets/file-name** - Brief description

## Related Skills

- **related-skill-1** - Brief description of relationship
- **related-skill-2** - How they work together
```

## Directory Structure

```
skill-name/
├── SKILL.md              # Main instructions (required)
├── CHANGELOG.md          # Version history (recommended)
├── README.md             # Extended documentation (optional)
├── scripts/              # Executable scripts (optional)
│   ├── script1.sh
│   ├── script2.py
│   └── helper.js
├── references/           # Extended guides (optional)
│   ├── advanced-guide.md
│   ├── api-reference.md
│   └── examples.md
└── assets/               # Templates, configs (optional)
    ├── config-template.yml
    ├── example-data.json
    └── diagram.png
```

## Frontmatter Fields

### Required Fields

```yaml
name: skill-name           # Kebab-case, matches directory name
description: "..."         # One-sentence summary, 100-200 chars
```

### Recommended Fields

```yaml
version: 1.0.0            # Semantic versioning
author: Your Name         # Creator
created: 2026-01-10       # ISO date
updated: 2026-01-10       # Last modified
tags: [tag1, tag2]        # 3-5 relevant tags
license: MIT              # License type
```

### Optional Fields

```yaml
dependencies: [skill1]     # Other skills required
compatibility: [claude.ai] # Where skill works
status: stable            # stable|beta|experimental
homepage: https://...     # Documentation URL
```

## Content Guidelines

### 1. Be Executable

Every command should be copy-paste ready:

✅ **Good:**
```bash
sudo apt install postgresql-client
export DATABASE_URL="postgres://user:pass@localhost:5432/db"
pg_dump $DATABASE_URL > backup.sql
```

❌ **Bad:**
```bash
Install PostgreSQL client
Set database URL
Run pg_dump
```

### 2. Include Time Estimates

Help users plan their time:

```markdown
### 3. Configure Database (5 min)
```

### 3. Show Expected Outputs

```bash
docker ps
# Expected:
# CONTAINER ID   IMAGE     STATUS
# abc123def456   nginx     Up 2 hours
```

### 4. Provide Validation Steps

Always include "how do I know it worked":

```markdown
## Validation

\`\`\`bash
curl -I https://app.example.com
# Expected: HTTP/2 200
\`\`\`
```

### 5. Handle Failure Modes

Top 3-5 common issues with fixes:

```markdown
## Troubleshooting

### Connection Refused

**Symptoms:** `curl: (7) Failed to connect`

**Fix:**
\`\`\`bash
sudo systemctl start nginx
sudo systemctl status nginx
\`\`\`
```

## Best Practices

### Naming

- **Skill names:** Use kebab-case (postgres-backup, not Postgres_Backup)
- **File names:** Lowercase with dashes (backup-script.sh, not BackupScript.sh)
- **Tags:** Lowercase, singular (database not databases)

### Structure

- Start with Quick Start for 80% use case
- Advanced topics in separate sections or reference files
- Keep SKILL.md focused, move details to references/

### Examples

Include real, tested examples:

```bash
# Example: Backup production database
export DB_NAME="production"
export S3_BUCKET="backups-prod"
./scripts/backup-to-s3.sh $DB_NAME $S3_BUCKET
```

### Documentation

- **Prerequisites:** Be specific (versions, access requirements)
- **Commands:** Include both command and expected output
- **Errors:** Document common errors with solutions
- **Links:** Reference official docs when relevant

## Common Patterns

### Configuration Files

Provide templates in assets/:

```markdown
## Setup

Copy the configuration template:

\`\`\`bash
cp assets/config-template.yml config.yml
nano config.yml  # Edit with your values
\`\`\`
```

### Multi-Step Workflows

Break into numbered sections:

```markdown
## Complete Workflow

### 1. Preparation (10 min)
### 2. Installation (5 min)
### 3. Configuration (15 min)
### 4. Validation (5 min)

Total time: ~35 minutes
```

### Interactive Scripts

Explain what prompts users will see:

```markdown
Run the setup script:

\`\`\`bash
./scripts/setup.sh
\`\`\`

You'll be prompted for:
- Database password (input hidden)
- Backup schedule (cron format)
- S3 bucket name
```

### Reference Files

Keep SKILL.md concise, move details:

```markdown
## Advanced Topics

See **references/advanced-config.md** for:
- Custom scheduling
- Multi-region replication
- Encryption at rest
```

## Version Control

### CHANGELOG.md Format

```markdown
# Changelog

## v1.1.0 - 2026-01-15
### Added
- S3 encryption support
- Automated restore testing

### Changed
- Improved error messages
- Updated dependencies

### Fixed
- Backup retention bug

## v1.0.0 - 2026-01-10
- Initial release
```

### Git Tags

Format: `{skill-name}-v{version}`

```bash
git tag postgres-backup-v1.1.0
git push origin main --tags
```

## Testing Your Skill

Before publishing:

1. **Validate syntax:**
   ```bash
   python3 /mnt/skills/examples/skill-creator/scripts/package_skill.py skill-name
   ```

2. **Test commands:** Run every command in a fresh environment

3. **Test on colleague:** Have someone else follow your instructions

4. **Check completeness:**
   - [ ] All prerequisites listed
   - [ ] Time estimates provided
   - [ ] Expected outputs shown
   - [ ] Failure modes documented
   - [ ] Scripts tested
   - [ ] Links work

## Examples from Library

**Good examples to study:**

- `vps-deployment-stack` - Comprehensive deployment guide
- `docker-development-workflow` - Multi-environment patterns
- `vps-daily-operations` - Automation scripts + runbooks

**What makes them good:**

- Executable commands
- Clear validation steps
- Troubleshooting sections
- Well-organized reference files
- Real-world examples
