#!/bin/bash
# Sync Skills Library with GitHub
# Pulls latest changes and optionally pushes local changes

set -e

LIBRARY_ROOT="${LIBRARY_ROOT:-$HOME/Skills_librairie}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Skills Library Sync ===${NC}\n"

# Check if library exists
if [ ! -d "$LIBRARY_ROOT" ]; then
    echo -e "${YELLOW}Library not found at $LIBRARY_ROOT${NC}"
    echo "Cloning from GitHub..."
    gh repo clone GuillaumeBld/Skills_librairie "$LIBRARY_ROOT"
    exit 0
fi

cd "$LIBRARY_ROOT"

# Check if we're in a git repo
if [ ! -d .git ]; then
    echo -e "${YELLOW}Not a git repository!${NC}"
    exit 1
fi

# Check GitHub CLI auth
if ! gh auth status &>/dev/null; then
    echo -e "${YELLOW}GitHub CLI not authenticated${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo "Current location: $LIBRARY_ROOT"
echo ""

# Show current status
echo -e "${BLUE}Current status:${NC}"
git status --short

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "\n${YELLOW}You have uncommitted changes${NC}"
    read -p "Commit them now? (y/n): " COMMIT_CONFIRM
    
    if [ "$COMMIT_CONFIRM" = "y" ]; then
        read -p "Commit message: " COMMIT_MSG
        git add .
        git commit -m "$COMMIT_MSG"
        echo -e "${GREEN}✓ Changes committed${NC}"
    fi
fi

# Pull latest changes
echo -e "\n${BLUE}Pulling latest changes from GitHub...${NC}"
git pull origin main --tags

# Check if we should push
if [ "$(git rev-list @{u}..HEAD --count)" -gt 0 ]; then
    echo -e "\n${YELLOW}You have unpushed commits${NC}"
    read -p "Push to GitHub now? (y/n): " PUSH_CONFIRM
    
    if [ "$PUSH_CONFIRM" = "y" ]; then
        git push origin main --tags
        echo -e "${GREEN}✓ Pushed to GitHub${NC}"
    fi
else
    echo -e "${GREEN}✓ Already up to date${NC}"
fi

# Rebuild catalog
echo -e "\n${BLUE}Rebuilding catalog...${NC}"
if [ -f "$LIBRARY_ROOT/scripts/catalog-builder.py" ]; then
    python3 "$LIBRARY_ROOT/scripts/catalog-builder.py"
else
    echo -e "${YELLOW}catalog-builder.py not found, skipping${NC}"
fi

echo -e "\n${GREEN}=== Sync Complete ===${NC}"
