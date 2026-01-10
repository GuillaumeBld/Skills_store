---
name: skill-consistency-enforcer
description: Automatically enforce style guide and formatting standards across all skills. Checks frontmatter completeness, standardizes terminology, fixes formatting inconsistencies, validates tag conventions, and ensures section ordering. Runs on save or commit. Use when maintaining library consistency or onboarding new contributors.
version: 1.0.0
author: Guillaume
created: 2026-01-10
tags: [meta-skill, consistency, formatting, automation, standards]
license: MIT
---

# Skill Consistency Enforcer

Automatically enforce consistent formatting and standards across all skills.

## Quick Start

```bash
# Check skill consistency
python3 scripts/enforce-consistency.py ~/Skills_librairie/skills/postgres-backup

# Auto-fix issues
python3 scripts/enforce-consistency.py ~/Skills_librairie/skills/postgres-backup --fix

# Batch check all skills
python3 scripts/enforce-consistency.py ~/Skills_librairie/skills/* --fix
```

## Consistency Checks

### 1. Frontmatter Fields
- Required: name, description, version, tags
- Format: Proper YAML syntax
- Tags: Lowercase, singular, 3-5 tags

### 2. Naming Conventions
- Skill names: kebab-case
- File names: lowercase with dashes
- Sections: Title Case

### 3. Time Estimates
- Format: "5 min" not "five minutes"
- Placement: In heading "### 1. Step (5 min)"

### 4. Command Formatting
- Consistent flag style (--verbose not -v)
- Comments start with #
- One command per line (use && for chaining)

### 5. Section Order
1. Prerequisites
2. Quick Start
3. Additional workflows
4. Validation
5. Troubleshooting
6. Reference Files
7. Related Skills

## Auto-Fixes

- Converts "5 minutes" → "5 min"
- Reorders sections
- Adds missing frontmatter
- Standardizes tags
- Fixes heading hierarchy

## Configuration

```yaml
# .consistency-config.yml
rules:
  enforce_section_order: true
  standardize_time_format: true
  require_frontmatter_fields: [name, description, version, tags]
  tag_format: lowercase_singular
  max_tags: 5
```

## Related Skills

- skill-quality-auditor
- skill-code-simplifier
