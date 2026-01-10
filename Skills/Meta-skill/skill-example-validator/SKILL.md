---
name: skill-example-validator
description: Validate all commands and examples in skills are executable and produce expected outputs. Tests commands in sandbox, checks HTTP URLs, verifies file paths, validates environment variables, and generates test reports. Use before releases, in CI/CD, or when updating examples.
version: 1.0.0
author: Guillaume
created: 2026-01-10
tags: [meta-skill, validation, testing, quality, automation]
license: MIT
---

# Skill Example Validator

Validate that all commands and examples in skills actually work.

## Quick Start

```bash
# Validate a single skill
python3 scripts/validate-examples.py ~/Skills_librairie/skills/postgres-backup

# Output:
# Validating postgres-backup...
# 
# ✓ Command 1: docker --version (passed)
# ✓ Command 2: curl -I https://example.com (passed)
# ✗ Command 3: invalid-command (failed)
# ✓ URL 1: https://docs.docker.com (200 OK)
# ✗ File reference: ./scripts/missing.sh (not found)
# 
# Results: 3/5 passed (60%)
```

## Validation Types

### 1. Command Syntax
```bash
# Tests that commands are valid
docker ps  # ✓ Valid
dokcer ps  # ✗ Invalid (typo)
```

### 2. Expected Outputs
```bash
# From SKILL.md:
docker ps
# Expected: CONTAINER   STATUS

# Validator checks output contains these strings
```

### 3. HTTP Links
```bash
# Checks all URLs return 200
[Docker Docs](https://docs.docker.com)  # ✓
[Broken](https://example.com/404)       # ✗
```

### 4. File References
```bash
# Verifies files exist
See scripts/backup.sh        # ✓ exists
See scripts/missing.sh       # ✗ not found
```

### 5. Environment Variables
```bash
# Checks variables are defined/documented
export DATABASE_URL="..."  # ✓ defined
echo $UNDEFINED_VAR        # ✗ not set
```

## Sandbox Testing

```bash
# Run commands in isolated environment
python3 scripts/validate-examples.py skill-path --sandbox

# Creates temporary Docker container
# Executes commands safely
# Reports success/failure
# Cleans up automatically
```

## CI/CD Integration

```yaml
# .github/workflows/validate-examples.yml
- name: Validate Examples
  run: |
    python3 scripts/validate-examples.py skills/* --fail-fast
```

## Batch Validation

```bash
# Validate all skills
python3 scripts/validate-examples.py ~/Skills_librairie/skills/*

# Summary report:
# Total skills: 12
# Total commands: 145
# Passed: 138 (95%)
# Failed: 7 (5%)
# 
# Failed commands:
# - postgres-backup: line 45 (connection refused)
# - mysql-backup: line 67 (command not found)
```

## Auto-Fix Suggestions

```bash
python3 scripts/validate-examples.py skill-path --suggest-fixes

# Output:
# Failed: invalid-command
# Suggestion: Did you mean 'docker'?
# 
# Failed: https://example.com/old-link
# Suggestion: Link redirects to https://example.com/new-link
```

## Related Skills

- skill-test-generator
- skill-quality-auditor
