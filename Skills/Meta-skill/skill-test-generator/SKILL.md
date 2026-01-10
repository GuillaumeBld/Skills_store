---
name: skill-test-generator
description: Automatically generate test cases and validation scripts for skills. Extracts commands from SKILL.md, creates test scripts (bash/pytest), generates test fixtures, validates expected outputs, tests failure modes, and supports CI/CD integration. Use when creating skills, before releases, or establishing regression test suites.
version: 1.0.0
author: Guillaume
created: 2026-01-10
updated: 2026-01-10
tags: [meta-skill, testing, validation, automation, quality]
dependencies: [skill-quality-auditor]
compatibility: [claude.ai, claude-code]
license: MIT
---

# Skill Test Generator

Automatically generate test cases and validation scripts for skills.

## Prerequisites

- Python 3.8+
- Bash (for test scripts)
- pytest (optional, for Python tests): `pip install pytest --break-system-packages`

## Quick Start: Generate Tests

### 1. Generate Test Suite (2 min)

```bash
# Generate tests for a skill
python3 scripts/generate-tests.py ~/Skills_librairie/skills/postgres-backup

# Output:
# Generated tests/test-postgres-backup.sh
# Generated tests/test-postgres-backup.py
# Generated tests/fixtures/
```

### 2. Run Tests (5 min)

```bash
# Run bash tests
cd ~/Skills_librairie/skills/postgres-backup
bash tests/test-postgres-backup.sh

# Run Python tests (if generated)
pytest tests/test-postgres-backup.py -v
```

### 3. Add to CI/CD

```yaml
# .github/workflows/test-skills.yml
- name: Test Skills
  run: |
    bash tests/test-*.sh
```

## Test Generation Modes

### Mode 1: Command Extraction

Extracts all commands from SKILL.md and generates tests:

```bash
python3 scripts/generate-tests.py skill-path --mode commands
```

**Generated:**
```bash
#!/bin/bash
# Auto-generated tests for skill-name

test_command_1() {
    # From SKILL.md step 2
    docker --version || return 1
    echo "✓ Docker installed"
}

test_command_2() {
    # From SKILL.md step 3
    curl -I https://example.com | grep "200 OK" || return 1
    echo "✓ API accessible"
}

# Run all tests
test_command_1
test_command_2
echo "All tests passed"
```

### Mode 2: Workflow Testing

Tests complete workflows end-to-end:

```bash
python3 scripts/generate-tests.py skill-path --mode workflow
```

**Generated:**
```bash
#!/bin/bash
# Workflow test: Quick Start

setup() {
    # Create test environment
    export TEST_DIR="/tmp/test-$$"
    mkdir -p "$TEST_DIR"
    cd "$TEST_DIR"
}

test_quick_start() {
    # Step 1: Install dependencies
    sudo apt install -y postgresql-client
    
    # Step 2: Configure
    export DATABASE_URL="postgres://test:test@localhost"
    
    # Step 3: Run backup
    ./backup.sh
    
    # Verify backup created
    [ -f "backup-$(date +%Y%m%d).sql" ] || return 1
}

cleanup() {
    rm -rf "$TEST_DIR"
}

setup
test_quick_start
cleanup
```

### Mode 3: Failure Mode Testing

Tests documented troubleshooting scenarios:

```bash
python3 scripts/generate-tests.py skill-path --mode failures
```

**Generated:**
```bash
test_connection_refused() {
    # Simulate connection refused error
    export DATABASE_URL="postgres://localhost:9999"
    
    ./backup.sh 2>&1 | grep "connection refused" || return 1
    echo "✓ Handles connection errors correctly"
}

test_disk_full() {
    # Simulate disk full
    export BACKUP_DIR="/dev/full"
    
    ./backup.sh 2>&1 | grep "No space left" || return 1
    echo "✓ Handles disk full gracefully"
}
```

## Test Fixtures

Auto-generates test data:

```bash
# fixtures/test-database.sql
CREATE TABLE users (id INT, name VARCHAR(50));
INSERT INTO users VALUES (1, 'Test User');

# fixtures/test-config.yml
database:
  host: localhost
  port: 5432
  name: testdb
```

**Usage in tests:**
```bash
test_with_fixture() {
    psql $DATABASE_URL < fixtures/test-database.sql
    ./backup.sh
    [ -f "backup.sql" ] || return 1
}
```

## Expected Output Validation

Validates documented expected outputs:

```markdown
# In SKILL.md:
```bash
docker ps
# Expected: CONTAINER   STATUS
#          abc123      Up 2 hours
```
```

**Generated test:**
```bash
test_expected_output() {
    output=$(docker ps --format "{{.Names}}\t{{.Status}}")
    echo "$output" | grep -q "Up" || return 1
}
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Test Skills

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate Tests
        run: python3 meta-skills/skill-test-generator/scripts/generate-tests.py skills/*
      
      - name: Run Tests
        run: |
          for test in skills/*/tests/test-*.sh; do
            bash "$test" || exit 1
          done
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Generate and run tests for changed skills
for skill in $(git diff --cached --name-only | grep SKILL.md | xargs dirname); do
    python3 scripts/generate-tests.py "$skill"
    bash "$skill/tests/test-*.sh" || exit 1
done
```

## Test Coverage Report

```bash
python3 scripts/generate-tests.py skill-path --coverage

# Output:
# Test Coverage Report: postgres-backup
# 
# Commands tested: 12/15 (80%)
# Workflows tested: 2/2 (100%)
# Failure modes tested: 3/5 (60%)
# 
# Untested commands:
# - aws s3 cp (line 45)
# - pg_restore (line 67)
# - crontab -e (line 89)
```

## Reference Files

- **scripts/generate-tests.py** - Main test generator
- **scripts/run-all-tests.sh** - Run all skill tests
- **references/test-patterns.md** - Common test patterns
- **assets/test-template.sh** - Bash test template
- **assets/test-template.py** - Pytest template

## Related Skills

- **skill-quality-auditor** - Quality checks before testing
- **skill-example-validator** - Validate examples work
- **skill-consistency-enforcer** - Enforce test standards
