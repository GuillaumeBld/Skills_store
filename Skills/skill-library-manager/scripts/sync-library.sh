#!/bin/bash
# Sync Skills library with remote, rebuild catalog/index.

set -euo pipefail

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

echo -e "${BLUE}=== Skills Library Sync ===${NC}\n"

if ! LIBRARY_ROOT="$(detect_library_root)"; then
  echo -e "${RED}Could not locate a Skills repository.${NC}"
  echo "Set LIBRARY_ROOT=/path/to/repo and rerun."
  exit 1
fi

if [ ! -d "$LIBRARY_ROOT/.git" ]; then
  echo -e "${RED}$LIBRARY_ROOT is not a git repository.${NC}"
  exit 1
fi

cd "$LIBRARY_ROOT"
echo "Repository: $LIBRARY_ROOT"

if ! command -v git >/dev/null 2>&1; then
  echo -e "${RED}Git is required but not available.${NC}"
  exit 1
fi

if command -v gh >/dev/null 2>&1 && ! gh auth status >/dev/null 2>&1; then
  echo -e "${YELLOW}GitHub CLI detected but not authenticated (optional).${NC}"
fi

echo -e "\n${BLUE}Current status:${NC}"
git status --short

if ! git diff-index --quiet HEAD --; then
  echo -e "\n${YELLOW}You have uncommitted changes.${NC}"
  read -r -p "Commit them now? (y/N): " COMMIT_CONFIRM
  if [[ "${COMMIT_CONFIRM:-}" =~ ^[Yy]$ ]]; then
    read -r -p "Commit message: " COMMIT_MSG
    COMMIT_MSG="${COMMIT_MSG:-chore: sync local changes}"
    git add -A
    git commit -m "$COMMIT_MSG"
    echo -e "${GREEN}✓ Changes committed${NC}"
  fi
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo -e "\n${BLUE}Pulling latest changes for ${CURRENT_BRANCH}...${NC}"
if git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >/dev/null 2>&1; then
  git pull --rebase --tags
else
  echo -e "${YELLOW}No upstream set for ${CURRENT_BRANCH}; skipping pull.${NC}"
fi

if git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >/dev/null 2>&1; then
  if [ "$(git rev-list @{u}..HEAD --count)" -gt 0 ]; then
    echo -e "\n${YELLOW}You have unpushed commits.${NC}"
    read -r -p "Push now? (y/N): " PUSH_CONFIRM
    if [[ "${PUSH_CONFIRM:-}" =~ ^[Yy]$ ]]; then
      git push
      echo -e "${GREEN}✓ Pushed${NC}"
    fi
  else
    echo -e "${GREEN}✓ Branch is up to date with upstream${NC}"
  fi
fi

CATALOG_BUILDER="$LIBRARY_ROOT/Skills/skill-library-manager/scripts/catalog-builder.py"
INDEX_BUILDER="$LIBRARY_ROOT/Skills/Meta-skill/skills-store-access/scripts/generate-skills-index.py"

if [ -f "$CATALOG_BUILDER" ]; then
  echo -e "\n${BLUE}Rebuilding catalog...${NC}"
  python3 "$CATALOG_BUILDER"
else
  echo -e "\n${YELLOW}catalog-builder.py not found; skipping catalog rebuild.${NC}"
fi

if [ -f "$INDEX_BUILDER" ]; then
  echo -e "${BLUE}Rebuilding lightweight index...${NC}"
  python3 "$INDEX_BUILDER"
fi

echo -e "\n${GREEN}=== Sync Complete ===${NC}"
