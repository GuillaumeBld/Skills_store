#!/bin/bash
set -euo pipefail

# Automated Skill Creation Workflow
# Creates a new skill in Skills/<Category>/<skill-name>, validates/package option,
# updates catalog/index, and offers optional git commit/push.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

detect_library_root() {
  if [ -n "${LIBRARY_ROOT:-}" ] && [ -d "${LIBRARY_ROOT}/Skills" ]; then
    echo "$LIBRARY_ROOT"
    return 0
  fi

  local current="$SCRIPT_DIR"
  while [ "$current" != "/" ]; do
    if [ -d "$current/Skills" ] || [ -d "$current/skills" ]; then
      echo "$current"
      return 0
    fi
    current="$(dirname "$current")"
  done

  local candidates=(
    "$HOME/Skills_librairie"
    "$HOME/Skills_store"
    "$HOME/Documents/Skills/Skills_librairie"
    "$HOME/Documents/Skills/Skills_store"
  )
  local c
  for c in "${candidates[@]}"; do
    if [ -d "$c/Skills" ] || [ -d "$c/skills" ]; then
      echo "$c"
      return 0
    fi
  done

  return 1
}

to_kebab() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g; s/--+/-/g'
}

echo -e "${BLUE}=== Skill Library Manager: Create New Skill ===${NC}\n"

if ! LIBRARY_ROOT="$(detect_library_root)"; then
  echo -e "${RED}Could not locate a Skills repository.${NC}"
  echo "Set LIBRARY_ROOT to your repository path and re-run."
  exit 1
fi

if [ ! -d "$LIBRARY_ROOT/.git" ]; then
  echo -e "${YELLOW}Warning: $LIBRARY_ROOT is not a git repo. Continuing anyway.${NC}"
fi

SKILLS_DIR="$LIBRARY_ROOT/Skills"
mkdir -p "$SKILLS_DIR" "$LIBRARY_ROOT/packaged"

echo "Repository: $LIBRARY_ROOT"
echo ""

read -r -p "Skill name (kebab-case, e.g., postgres-backup): " RAW_SKILL_NAME
SKILL_NAME="$(to_kebab "$RAW_SKILL_NAME")"
if [ -z "$SKILL_NAME" ]; then
  echo -e "${RED}Skill name cannot be empty.${NC}"
  exit 1
fi

read -r -p "Category (default: Development): " CATEGORY
CATEGORY="${CATEGORY:-Development}"
read -r -p "Short description: " DESCRIPTION
read -r -p "Author name: " AUTHOR
read -r -p "Tags (comma-separated, e.g., database,backup,postgresql): " TAGS_INPUT
read -r -p "Version (default: 1.0.0): " VERSION
VERSION="${VERSION:-1.0.0}"

TARGET_DIR="$SKILLS_DIR/$CATEGORY"
SKILL_DIR="$TARGET_DIR/$SKILL_NAME"
SKILL_MD="$SKILL_DIR/SKILL.md"

if [ -d "$SKILL_DIR" ]; then
  echo -e "${YELLOW}$SKILL_DIR already exists.${NC}"
  read -r -p "Overwrite SKILL.md metadata and continue? (y/N): " OVERWRITE
  if [[ ! "${OVERWRITE:-}" =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
  fi
fi

mkdir -p "$SKILL_DIR/scripts" "$SKILL_DIR/references" "$SKILL_DIR/assets"

INIT_SCRIPT="$LIBRARY_ROOT/Skills/Meta-skill/skill-creator/scripts/init_skill.py"
if [ -f "$INIT_SCRIPT" ]; then
  echo "Initializing structure with skill-creator..."
  python3 "$INIT_SCRIPT" "$SKILL_NAME" --path "$TARGET_DIR" >/dev/null 2>&1 || true
fi

# Normalize tags list.
IFS=',' read -r -a TAGS <<< "$TAGS_INPUT"
TAGS_JSON=""
for t in "${TAGS[@]}"; do
  t="$(echo "$t" | xargs)"
  [ -z "$t" ] && continue
  if [ -n "$TAGS_JSON" ]; then
    TAGS_JSON="$TAGS_JSON, "
  fi
  TAGS_JSON="$TAGS_JSON\"$t\""
done

cat > "$SKILL_MD" <<EOF
---
name: "$SKILL_NAME"
description: "${DESCRIPTION//\"/\\\"}"
version: "$VERSION"
author: "${AUTHOR//\"/\\\"}"
created: "$(date +%Y-%m-%d)"
updated: "$(date +%Y-%m-%d)"
category: "$CATEGORY"
tags: [${TAGS_JSON}]
license: "MIT"
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

cat > "$SKILL_DIR/CHANGELOG.md" <<EOF
# Changelog

## v$VERSION - $(date +%Y-%m-%d)
- Initial release
EOF

echo -e "\n${YELLOW}Opening editor for SKILL.md...${NC}"
echo "Close the editor when done."
"${EDITOR:-nano}" "$SKILL_MD"

PACKAGE_SCRIPT="$LIBRARY_ROOT/Skills/Meta-skill/skill-creator/scripts/package_skill.py"
if [ -f "$PACKAGE_SCRIPT" ]; then
  echo -e "\n${BLUE}Packaging skill...${NC}"
  if python3 "$PACKAGE_SCRIPT" "$SKILL_DIR" "$LIBRARY_ROOT/packaged"; then
    echo -e "${GREEN}✓ Skill packaged successfully${NC}"
  else
    echo -e "${YELLOW}⚠ Packaging failed. You can rerun manually:${NC}"
    echo "python3 \"$PACKAGE_SCRIPT\" \"$SKILL_DIR\" \"$LIBRARY_ROOT/packaged\""
  fi
else
  echo -e "${YELLOW}⚠ package_skill.py not found; skipping packaging.${NC}"
fi

CATALOG_BUILDER="$LIBRARY_ROOT/Skills/skill-library-manager/scripts/catalog-builder.py"
INDEX_BUILDER="$LIBRARY_ROOT/Skills/Meta-skill/skills-store-access/scripts/generate-skills-index.py"

if [ -f "$CATALOG_BUILDER" ]; then
  echo -e "\n${BLUE}Updating catalog...${NC}"
  python3 "$CATALOG_BUILDER"
fi

if [ -f "$INDEX_BUILDER" ]; then
  echo -e "${BLUE}Updating lightweight index...${NC}"
  python3 "$INDEX_BUILDER"
fi

if [ -d "$LIBRARY_ROOT/.git" ]; then
  echo -e "\n${BLUE}Git summary:${NC}"
  git -C "$LIBRARY_ROOT" status --short

  read -r -p "Create commit now? (y/N): " COMMIT_CONFIRM
  if [[ "${COMMIT_CONFIRM:-}" =~ ^[Yy]$ ]]; then
    git -C "$LIBRARY_ROOT" add "$SKILL_DIR" "$LIBRARY_ROOT/catalog.json" "$LIBRARY_ROOT/skills-index.json" 2>/dev/null || true
    git -C "$LIBRARY_ROOT" commit -m "Add $SKILL_NAME skill v$VERSION"
    read -r -p "Push current branch now? (y/N): " PUSH_CONFIRM
    if [[ "${PUSH_CONFIRM:-}" =~ ^[Yy]$ ]]; then
      git -C "$LIBRARY_ROOT" push
      echo -e "${GREEN}✓ Pushed${NC}"
    fi
  fi
fi

echo -e "\n${GREEN}=== Skill Created ===${NC}"
echo "Skill: $SKILL_NAME"
echo "Category: $CATEGORY"
echo "Location: $SKILL_DIR"
echo "Package: $LIBRARY_ROOT/packaged/$SKILL_NAME.skill"
