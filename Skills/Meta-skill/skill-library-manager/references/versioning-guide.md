# Semantic Versioning Guide for Skills

Complete guide to versioning your skills using Semantic Versioning (semver).

## Semantic Versioning Overview

Format: `MAJOR.MINOR.PATCH` (e.g., `2.1.3`)

**Rules:**
- **MAJOR**: Incompatible API changes (breaking changes)
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

**Starting version:** `1.0.0` for production-ready skills, `0.1.0` for beta/experimental

## When to Increment

### MAJOR Version (X.0.0)

Increment when making **breaking changes** that require users to modify their usage.

**Examples:**
- Renamed skill
- Removed commands or scripts
- Changed script parameters (incompatible)
- Restructured directory layout
- Changed required prerequisites
- Removed or renamed environment variables

**Example commit:**
```bash
git commit -m "postgres-backup v2.0.0: Breaking changes

BREAKING CHANGES:
- Renamed backup-db.sh → backup.sh
- Changed --retention flag to --keep-days
- Moved config from .env to config.yml
- Requires PostgreSQL 14+ (was 12+)

Migration guide in CHANGELOG.md"

git tag postgres-backup-v2.0.0
```

### MINOR Version (1.X.0)

Increment when adding **new features** without breaking existing functionality.

**Examples:**
- New scripts added
- New reference documentation
- New optional features
- Enhanced existing features (backward compatible)
- New environment variables (optional)
- Additional validation checks

**Example commit:**
```bash
git commit -m "postgres-backup v1.1.0: Add S3 encryption

Features:
- Added AES-256 encryption for S3 uploads
- New --encrypt flag (optional, defaults to false)
- Enhanced error messages
- Added encryption guide in references/

All existing usage continues to work unchanged."

git tag postgres-backup-v1.1.0
```

### PATCH Version (1.0.X)

Increment for **bug fixes** and minor improvements.

**Examples:**
- Fixed typos in documentation
- Fixed script bugs
- Improved error messages
- Updated dependencies (patch versions)
- Performance improvements
- Better examples/comments

**Example commit:**
```bash
git commit -m "postgres-backup v1.0.1: Fix retention policy bug

Fixes:
- Retention policy now correctly deletes backups >30 days
- Fixed typo in error message
- Updated example with correct S3 path"

git tag postgres-backup-v1.0.1
```

## Version Lifecycle

### Development (0.x.x)

Use `0.x.x` for skills under development:

- `0.1.0`: Initial prototype
- `0.2.0`: Added core features
- `0.3.0`: Beta release (testing)
- `1.0.0`: First stable release

**In development:**
- Breaking changes OK without MAJOR bump
- Frequent iterations expected
- Mark as `status: experimental` in frontmatter

```yaml
version: 0.3.0
status: experimental
```

### Stable (1.x.x+)

Version `1.0.0` signals production-ready:

- Follow semver strictly
- Maintain backward compatibility for MINOR/PATCH
- Document breaking changes clearly
- Provide migration guides

### End of Life

Mark deprecated skills:

```yaml
version: 3.5.2
status: deprecated
deprecated: "Use postgres-advanced-backup instead"
```

## Practical Examples

### Example 1: Initial Release

```bash
# Create skill
python3 init_skill.py postgres-backup
# ... develop skill ...

# SKILL.md frontmatter:
# version: 1.0.0

# CHANGELOG.md:
# ## v1.0.0 - 2026-01-15
# - Initial release
# - Basic pg_dump automation
# - Local backup storage

git commit -m "Add postgres-backup v1.0.0"
git tag postgres-backup-v1.0.0
```

### Example 2: Add Feature

```bash
# Add S3 upload feature
# ... modify scripts ...

# Update SKILL.md:
# version: 1.0.0 → 1.1.0

# Update CHANGELOG.md:
# ## v1.1.0 - 2026-01-20
# ### Added
# - S3 upload support
# - Configurable retention policy

git commit -m "postgres-backup v1.1.0: Add S3 upload"
git tag postgres-backup-v1.1.0
```

### Example 3: Fix Bug

```bash
# Fix deletion bug
# ... fix script ...

# Update SKILL.md:
# version: 1.1.0 → 1.1.1

# Update CHANGELOG.md:
# ## v1.1.1 - 2026-01-22
# ### Fixed
# - Old backups now deleted correctly

git commit -m "postgres-backup v1.1.1: Fix deletion bug"
git tag postgres-backup-v1.1.1
```

### Example 4: Breaking Change

```bash
# Complete rewrite with new architecture
# ... major changes ...

# Update SKILL.md:
# version: 1.1.1 → 2.0.0

# Update CHANGELOG.md:
# ## v2.0.0 - 2026-02-01
# ### BREAKING CHANGES
# - Renamed backup.sh → postgres-backup.sh
# - Config format changed from .env to YAML
# - Requires PostgreSQL 14+ (was 12+)
#
# ### Migration Guide
# 1. Rename backup.sh to postgres-backup.sh
# 2. Convert .env to config.yml (see template)
# 3. Upgrade PostgreSQL if < v14

git commit -m "postgres-backup v2.0.0: Rewrite with YAML config

BREAKING CHANGES:
- See CHANGELOG.md for migration guide"

git tag postgres-backup-v2.0.0
```

## CHANGELOG.md Format

### Standard Format

```markdown
# Changelog

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Feature in development

## [2.0.0] - 2026-02-01
### BREAKING CHANGES
- Renamed backup.sh → postgres-backup.sh
- Config format: .env → config.yml

### Added
- New YAML configuration
- Health check endpoint

### Changed
- Improved error handling
- Updated PostgreSQL requirement: 14+

### Migration Guide
1. Rename backup.sh
2. Convert config (see template)
3. Update PostgreSQL

## [1.1.1] - 2026-01-22
### Fixed
- Retention policy deletion bug
- S3 connection timeout

## [1.1.0] - 2026-01-20
### Added
- S3 upload support
- Configurable retention (7/30/90 days)
- Email notifications

## [1.0.0] - 2026-01-15
- Initial stable release
```

### Categories

Use these standard sections:

- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes

## Pre-release Versions

### Alpha (Development)

```
1.0.0-alpha.1
1.0.0-alpha.2
```

Use for early testing, unstable.

### Beta (Testing)

```
1.0.0-beta.1
1.0.0-beta.2
```

Use for feature-complete, testing phase.

### Release Candidate

```
1.0.0-rc.1
1.0.0-rc.2
```

Use for final testing before stable release.

**Example workflow:**
```
0.1.0 → 0.2.0 → ... → 0.9.0 (development)
1.0.0-alpha.1 → 1.0.0-alpha.2 (early testing)
1.0.0-beta.1 → 1.0.0-beta.2 (feature freeze)
1.0.0-rc.1 → 1.0.0-rc.2 (final testing)
1.0.0 (stable release)
```

## Version in Files

### SKILL.md Frontmatter

```yaml
---
name: postgres-backup
version: 2.1.3
---
```

### Git Tags

```bash
# Format: {skill-name}-v{version}
git tag postgres-backup-v2.1.3

# Annotated tag (recommended)
git tag -a postgres-backup-v2.1.3 -m "PostgreSQL Backup v2.1.3

Bug fixes:
- Fixed S3 upload timeout
- Improved error messages"
```

### Catalog Entry

Automatically extracted by catalog-builder.py:

```json
{
  "name": "postgres-backup",
  "version": "2.1.3",
  "updated": "2026-02-15"
}
```

## Version Comparison

### Valid Version Sequences

✅ **Correct:**
```
1.0.0 → 1.0.1 (patch)
1.0.1 → 1.1.0 (minor)
1.1.0 → 2.0.0 (major)
```

❌ **Incorrect:**
```
1.0.0 → 1.0.2 (skipped 1.0.1)
1.1.0 → 1.0.1 (downgrade)
1.0.0 → 2.0.0 (skipped minor versions OK, but document why)
```

### Checking Versions

```bash
# List all versions
git tag -l "postgres-backup-*"

# Sort by version
git tag -l "postgres-backup-*" | sort -V

# Latest version
git tag -l "postgres-backup-*" | sort -V | tail -1
```

## Automation

### Version Bump Script

```bash
#!/bin/bash
# bump-version.sh

SKILL_NAME=$1
BUMP_TYPE=$2  # major, minor, patch

# Get current version
CURRENT=$(grep "^version:" "skills/$SKILL_NAME/SKILL.md" | cut -d' ' -f2)

# Calculate new version
case $BUMP_TYPE in
  major)
    NEW=$(echo $CURRENT | awk -F. '{print $1+1".0.0"}')
    ;;
  minor)
    NEW=$(echo $CURRENT | awk -F. '{print $1"."$2+1".0"}')
    ;;
  patch)
    NEW=$(echo $CURRENT | awk -F. '{print $1"."$2"."$3+1}')
    ;;
esac

echo "Bumping $SKILL_NAME: $CURRENT → $NEW"

# Update SKILL.md
sed -i "s/^version: .*/version: $NEW/" "skills/$SKILL_NAME/SKILL.md"

# Update CHANGELOG
echo "## v$NEW - $(date +%Y-%m-%d)
### TODO: Document changes
" >> "skills/$SKILL_NAME/CHANGELOG.md"

echo "Updated to v$NEW. Edit CHANGELOG.md and commit."
```

Usage:
```bash
./bump-version.sh postgres-backup minor
# Bumping postgres-backup: 1.1.3 → 1.2.0
```

## Best Practices

### 1. Always Update CHANGELOG

Never increment version without updating CHANGELOG.md.

### 2. Document Breaking Changes

Make breaking changes obvious:

```markdown
## v2.0.0 - 2026-02-01

### ⚠️ BREAKING CHANGES
- Changed X to Y
- Removed Z

### Migration Guide
Steps to upgrade from v1.x.x to v2.0.0...
```

### 3. Use Annotated Tags

```bash
# Good: Annotated tag with message
git tag -a postgres-backup-v1.1.0 -m "Add S3 encryption support"

# Avoid: Lightweight tag
git tag postgres-backup-v1.1.0
```

### 4. Version Before Packaging

Always update version in SKILL.md before running package_skill.py.

### 5. Batch Related Changes

Group related changes in one version bump:

✅ **Good:**
```
v1.1.0: Add S3 support + encryption + notifications
```

❌ **Bad:**
```
v1.1.0: Add S3 support
v1.2.0: Add encryption (should be in 1.1.0)
v1.3.0: Add notifications (should be in 1.1.0)
```

### 6. Test Before Tagging

```bash
# Test skill works
# ... testing ...

# Only then tag
git tag postgres-backup-v1.1.0
```

### 7. Never Delete Tags

If you release wrong version:

```bash
# Don't delete tag
# Instead, create patch version

# Wrong: v1.1.0 (has bug)
# Right: v1.1.1 (fixes bug)
```

## Common Scenarios

### Scenario 1: Forgot to Update Version

```bash
# Already committed without version bump
git tag -d postgres-backup-v1.1.0  # Delete wrong tag
git reset HEAD~1  # Undo commit

# Update version
# ... edit SKILL.md version: 1.0.0 → 1.1.0 ...

# Commit again
git add .
git commit -m "postgres-backup v1.1.0: Add feature"
git tag postgres-backup-v1.1.0
```

### Scenario 2: Multiple Skills in One Commit

```bash
# Update multiple skills together
git commit -m "Batch update: Fix dependency versions

- postgres-backup v1.1.1: Update pg_dump flags
- mysql-backup v2.0.1: Fix retention bug
- docker-workflow v1.3.2: Update Docker version"

# Tag each separately
git tag postgres-backup-v1.1.1
git tag mysql-backup-v2.0.1
git tag docker-workflow-v1.3.2
```

### Scenario 3: Hotfix for Old Version

```bash
# Current: v2.1.0
# Need to fix: v1.5.0 (still in use)

# Create branch from old tag
git checkout -b hotfix/v1.5.1 postgres-backup-v1.5.0

# Fix bug
# ... make changes ...

# Commit and tag
git commit -m "postgres-backup v1.5.1: Critical security fix"
git tag postgres-backup-v1.5.1

# Merge fix into main if applicable
git checkout main
git cherry-pick <commit-hash>
```

## Version FAQs

**Q: Can I skip versions?**
A: Technically yes, but avoid it. Users expect continuous versioning.

**Q: Should I start at 0.1.0 or 1.0.0?**
A: Use 0.x.x for development, 1.0.0 for first stable release.

**Q: What if I make multiple breaking changes?**
A: Still just bump MAJOR once: 1.5.0 → 2.0.0 (not 3.0.0).

**Q: Can I change version format?**
A: No, stick to semver for compatibility with tools.

**Q: How to version documentation-only changes?**
A: PATCH bump (1.0.0 → 1.0.1) for significant doc updates.
