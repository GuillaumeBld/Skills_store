#!/bin/bash
set -e

# Automated Skill Creation Workflow
# Creates skill, validates, packages, updates catalog, commits to Git

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LIBRARY_ROOT="${LIBRARY_ROOT:-$HOME/Skills_librairie}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Skill Library Manager: Create New Skill ===${NC}\n"

# Check if library exists
if [ ! -d "$LIBRARY_ROOT" ]; then
    echo -e "${YELLOW}Skills library not found at $LIBRARY_ROOT${NC}"
    echo "Cloning from GitHub..."
    gh repo clone GuillaumeBld/Skills_librairie "$LIBRARY_ROOT"
fi

cd "$LIBRARY_ROOT"

# Ensure directories exist
mkdir -p skills packaged scripts

# Prompt for skill information
read -p "Skill name (kebab-case, e.g., postgres-backup): " SKILL_NAME
read -p "Short description: " DESCRIPTION
read -p "Author name: " AUTHOR
read -p "Tags (comma-separated, e.g., database,backup,postgresql): " TAGS_INPUT
read -p "Version (default: 1.0.0): " VERSION
VERSION=${VERSION:-1.0.0}

# Convert tags to array
IFS=',' read -ra TAGS <<< "$TAGS_INPUT"

echo -e "\n${BLUE}Creating skill: $SKILL_NAME${NC}"

# 1. Initialize skill structure
echo "Step 1: Initializing skill structure..."
python3 /mnt/skills/examples/skill-creator/scripts/init_skill.py "$SKILL_NAME" --path "$LIBRARY_ROOT/skills"

# 2. Update SKILL.md frontmatter with metadata
SKILL_MD="$LIBRARY_ROOT/skills/$SKILL_NAME/SKILL.md"
echo "Step 2: Adding metadata to SKILL.md..."

# Create enhanced frontmatter
cat > "$SKILL_MD.tmp" << EOF
---
name: $SKILL_NAME
description: $DESCRIPTION
version: $VERSION
author: $AUTHOR
created: $(date +%Y-%m-%d)
updated: $(date +%Y-%m-%d)
tags: [$(echo "${TAGS[@]}" | sed 's/ /, /g')]
license: MIT
---

# ${SKILL_NAME}

TODO: Add skill content here

## Prerequisites

TODO: List prerequisites

## Quick Start

TODO: Add quick start guide

## Reference Files

TODO: Document reference files if any
EOF

mv "$SKILL_MD.tmp" "$SKILL_MD"

# 3. Create CHANGELOG
echo "Step 3: Creating CHANGELOG..."
cat > "$LIBRARY_ROOT/skills/$SKILL_NAME/CHANGELOG.md" << EOF
# Changelog

## v$VERSION - $(date +%Y-%m-%d)
- Initial release
EOF

# 4. Open editor for user to fill in content
echo -e "\n${YELLOW}Opening editor for you to add skill content...${NC}"
echo "Press Enter when ready to edit SKILL.md"
read

${EDITOR:-nano} "$SKILL_MD"

# 5. Validate skill
echo -e "\n${BLUE}Step 4: Validating skill...${NC}"
if python3 /mnt/skills/examples/skill-creator/scripts/package_skill.py "$LIBRARY_ROOT/skills/$SKILL_NAME" "$LIBRARY_ROOT/packaged"; then
    echo -e "${GREEN}✓ Skill validated and packaged successfully${NC}"
else
    echo -e "${YELLOW}⚠ Validation failed. Please fix errors and run:${NC}"
    echo "  python3 /mnt/skills/examples/skill-creator/scripts/package_skill.py $LIBRARY_ROOT/skills/$SKILL_NAME $LIBRARY_ROOT/packaged"
    exit 1
fi

# 6. Update catalog
echo "Step 5: Updating catalog..."
if [ -f "$LIBRARY_ROOT/scripts/catalog-builder.py" ]; then
    python3 "$LIBRARY_ROOT/scripts/catalog-builder.py"
else
    echo -e "${YELLOW}⚠ catalog-builder.py not found, skipping catalog update${NC}"
fi

# 7. Git operations
echo "Step 6: Committing to Git..."
git add .
git commit -m "Add $SKILL_NAME skill v$VERSION

- $DESCRIPTION
- Tags: ${TAGS[*]}"

# Create Git tag
git tag "$SKILL_NAME-v$VERSION"

# 8. Push to GitHub
echo "Step 7: Pushing to GitHub..."
read -p "Push to GitHub now? (y/n): " PUSH_CONFIRM
if [ "$PUSH_CONFIRM" = "y" ]; then
    git push origin main --tags
    echo -e "${GREEN}✓ Pushed to GitHub${NC}"
else
    echo -e "${YELLOW}Skipped push. Run manually: git push origin main --tags${NC}"
fi

echo -e "\n${GREEN}=== Skill Created Successfully ===${NC}"
echo "Skill name: $SKILL_NAME"
echo "Version: $VERSION"
echo "Location: $LIBRARY_ROOT/skills/$SKILL_NAME/"
echo "Package: $LIBRARY_ROOT/packaged/$SKILL_NAME.skill"
echo ""
echo "Next steps:"
echo "1. Test the skill in Claude.ai (upload .skill file)"
echo "2. Iterate on content as needed"
echo "3. Update version when making changes"
