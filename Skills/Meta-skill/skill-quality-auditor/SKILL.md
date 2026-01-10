---
name: skill-quality-auditor
description: Automatically audit skills for quality, completeness, and best practices. Scans SKILL.md for required sections, validates command executability, checks metadata completeness, analyzes readability metrics, detects broken links, and generates quality scores (0-100) with actionable improvement suggestions. Use when creating new skills, before packaging, during skill reviews, or auditing entire library.
version: 1.0.0
author: Guillaume
created: 2026-01-10
updated: 2026-01-10
tags: [meta-skill, quality, validation, best-practices, automation]
dependencies: []
compatibility: [claude.ai, claude-code]
license: MIT
---

# Skill Quality Auditor

Automatically audit skills for quality, completeness, and adherence to best practices.

## Prerequisites

- Python 3.8+
- Skills library at `~/Skills_librairie` (or custom path)
- Read access to skill files

## Quick Start: Audit a Single Skill

### 1. Run Quality Audit (2 min)

```bash
# Audit specific skill
python3 scripts/audit-skill.py ~/Skills_librairie/skills/postgres-backup

# Output:
# ====== Quality Audit: postgres-backup ======
# 
# Overall Score: 78/100 (Good)
# 
# ✓ Structure (25/25)
# ⚠ Completeness (18/25) - Missing 2 required sections
# ✓ Executability (20/20)
# ⚠ Readability (15/20) - Average sentence too long
# ✗ Links (0/10) - 2 broken links found
# 
# === Detailed Findings ===
# ...
```

### 2. Review Improvement Report

```bash
# Generate detailed report
python3 scripts/audit-skill.py ~/Skills_librairie/skills/postgres-backup --detailed

# Saves to: audit-reports/postgres-backup-YYYYMMDD.md
```

### 3. Apply Auto-Fixes (Optional)

```bash
# Fix automatically fixable issues
python3 scripts/audit-skill.py ~/Skills_librairie/skills/postgres-backup --auto-fix

# Fixes:
# - Adds missing frontmatter fields
# - Standardizes time estimates
# - Fixes heading hierarchy
# - Removes trailing whitespace
```

## Quality Metrics

### Score Breakdown (100 points total)

**1. Structure (25 points)**
- Has SKILL.md: 5 pts
- Valid YAML frontmatter: 5 pts
- Standard section order: 5 pts
- Proper heading hierarchy: 5 pts
- Has CHANGELOG.md: 5 pts

**2. Completeness (25 points)**
- Prerequisites section: 5 pts
- Quick Start workflow: 5 pts
- Validation section: 5 pts
- Troubleshooting section: 5 pts
- Reference files documented: 5 pts

**3. Executability (20 points)**
- All commands executable: 10 pts
- No pseudo-code: 5 pts
- Expected outputs shown: 5 pts

**4. Readability (20 points)**
- Average sentence length <25 words: 5 pts
- Time estimates provided: 5 pts
- Step numbering consistent: 5 pts
- Code blocks have language tags: 5 pts

**5. Links & References (10 points)**
- No broken internal links: 5 pts
- No broken external links: 5 pts

### Quality Grades

- **90-100**: Excellent - Production ready
- **75-89**: Good - Minor improvements needed
- **60-74**: Fair - Several issues to address
- **<60**: Poor - Major revision required

## Audit Entire Library

```bash
# Audit all skills
python3 scripts/audit-library.py ~/Skills_librairie

# Output summary:
# ====== Library Quality Report ======
# Total skills: 12
# Average score: 82/100
# 
# Excellent (90+): 4 skills
# Good (75-89): 6 skills
# Fair (60-74): 2 skills
# Poor (<60): 0 skills
# 
# Top Issues:
# 1. Missing validation sections (8 skills)
# 2. Broken links (5 skills)
# 3. No time estimates (4 skills)
```

## Quality Checks

### Required Sections Check

```python
# Checks for these sections in SKILL.md:
required_sections = [
    "Prerequisites",
    "Quick Start",
    "Validation",  # or "Verification"
    "Troubleshooting",
]
```

**Why these sections:**
- **Prerequisites**: User knows what's needed upfront
- **Quick Start**: Immediate value, 80% use case
- **Validation**: User can verify success
- **Troubleshooting**: Common issues covered

### Metadata Completeness Check

```yaml
# Required frontmatter fields:
required_fields:
  - name
  - description
  - version
  - tags

# Recommended fields:
recommended_fields:
  - author
  - created
  - updated
  - license
  - compatibility
```

### Command Executability Check

```bash
# ✓ Good: Executable command
sudo apt install postgresql-client
export DATABASE_URL="postgres://localhost"

# ✗ Bad: Pseudo-code
Install the PostgreSQL client
Set the database URL variable
```

**Detection:** Looks for imperative verbs without commands:
- "Install X" without package manager command
- "Configure Y" without config file/command
- "Set Z" without export/assignment

### Readability Metrics

**Sentence Length:**
```
Ideal: <20 words
Acceptable: 20-25 words
Long: >25 words
```

**Flesch Reading Ease:**
```
90-100: Very easy (5th grade)
60-70: Standard (8th-9th grade) ← Target
30-50: Difficult (college)
0-30: Very difficult (professional)
```

**Paragraph Length:**
```
Ideal: 3-5 sentences
Maximum: 8 sentences
```

### Link Validation

```bash
# Internal links (to other skills/files)
[See vps-deployment](../vps-deployment-stack/SKILL.md)
# Checks: File exists

# External links
[Docker Docs](https://docs.docker.com)
# Checks: HTTP 200 response
```

## Improvement Suggestions

### Example Output

```markdown
# Quality Audit: postgres-backup
Score: 78/100 (Good)

## Issues Found (6)

### High Priority (2)
1. Missing Validation Section
   Impact: Users can't verify success
   Fix: Add section showing health checks
   Example:
   ```markdown
   ## Validation
   
   ```bash
   # Check backup was created
   ls -lh backup-*.sql
   
   # Verify S3 upload
   aws s3 ls s3://bucket/backups/
   ```
   ```

2. Broken Link: references/s3-config.md
   Impact: Users can't access advanced docs
   Fix: Create file or remove reference

### Medium Priority (3)
3. Average sentence length: 28 words (target: <25)
   Impact: Harder to read
   Fix: Split long sentences
   
4. No time estimates
   Impact: Users can't plan
   Fix: Add estimates to steps:
   ```markdown
   ### 1. Install Dependencies (5 min)
   ### 2. Configure Database (10 min)
   ```

5. Missing CHANGELOG.md
   Impact: Can't track version history
   Fix: Create CHANGELOG.md:
   ```markdown
   # Changelog
   
   ## v1.0.0 - 2026-01-10
   - Initial release
   ```

### Low Priority (1)
6. Some code blocks missing language tags
   Impact: No syntax highlighting
   Fix: Add language identifier:
   ```markdown
   ```bash  ← Add this
   command here
   ```
   ```

## Quick Wins (Auto-fixable)
- Add missing frontmatter fields
- Standardize time format (5 minutes → 5 min)
- Fix heading hierarchy (H1 → H2 → H3)
- Remove trailing whitespace

Run with --auto-fix to apply
```

## Automated Workflows

### Pre-Commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Audit changed skills
for file in $(git diff --cached --name-only | grep "SKILL.md"); do
    skill_dir=$(dirname "$file")
    python3 scripts/audit-skill.py "$skill_dir" --min-score 75 || exit 1
done
```

**Blocks commits if quality <75/100**

### CI/CD Integration

```yaml
# .github/workflows/quality-check.yml
name: Skill Quality Check

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Audit Changed Skills
        run: |
          python3 scripts/audit-library.py . --min-score 75
          
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: quality-report
          path: audit-reports/
```

### Scheduled Audits

```bash
# Cron job: Audit weekly
0 9 * * 1 cd ~/Skills_librairie && python3 meta-skills/skill-quality-auditor/scripts/audit-library.py . --email report@example.com
```

## Comparison Mode

```bash
# Compare skill against best practices
python3 scripts/audit-skill.py postgres-backup --compare-to vps-deployment-stack

# Output:
# postgres-backup vs vps-deployment-stack (benchmark)
# 
# Structure: 20/25 vs 25/25 (-5)
#   Missing: CHANGELOG.md
# 
# Completeness: 18/25 vs 25/25 (-7)
#   Missing: Validation section
#   Missing: Example outputs
# 
# Recommendations:
# 1. Add CHANGELOG.md (see vps-deployment-stack/CHANGELOG.md)
# 2. Add validation section (see vps-deployment-stack#Validation)
```

## Reference Files

- **scripts/audit-skill.py** - Single skill auditor
- **scripts/audit-library.py** - Batch audit all skills
- **scripts/fix-common-issues.py** - Auto-fix common problems
- **references/quality-checklist.md** - Manual review checklist
- **references/best-practices.md** - Skill writing guidelines
- **assets/audit-report-template.md** - Report format

## Related Skills

- **skill-consistency-enforcer** - Enforce style guide
- **skill-test-generator** - Generate executable tests
- **skill-example-validator** - Validate all examples work
