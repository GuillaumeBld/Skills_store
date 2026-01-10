#!/bin/bash
set -e

# Equip Skills Store Access
# Platform-aware installation of skill-library-manager to enable Skills store capabilities

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_LIBRARY_MANAGER_URL="https://github.com/GuillaumeBld/Skills_librairie/tree/main/Skills/skill-library-manager"
REPO_OWNER="GuillaumeBld"
REPO_NAME="Skills_librairie"
SKILL_PATH="Skills/skill-library-manager"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Equipping Skills Store Access ===${NC}\n"

# Detect platform
echo -e "${CYAN}Detecting platform...${NC}"
PLATFORM_INFO=$(python3 "$SCRIPT_DIR/detect-platform.py" 2>/dev/null || echo "unknown")
PLATFORM=$(echo "$PLATFORM_INFO" | grep "Platform:" | awk '{print $2}' || echo "unknown")

echo -e "Detected platform: ${CYAN}${PLATFORM}${NC}\n"

# Determine skills directory based on platform
if [ "$PLATFORM" = "codex" ] || [ -d "${CODEX_HOME:-$HOME/.codex}/skills" ]; then
    CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
    CODEX_SKILLS_DIR="$CODEX_HOME/skills"
    INSTALL_METHOD="codex"
elif [ -d "$HOME/.cursor/skills" ]; then
    # Cursor-specific location (if different)
    CODEX_SKILLS_DIR="$HOME/.cursor/skills"
    INSTALL_METHOD="cursor"
else
    # Fallback: try to find any skills directory
    CODEX_SKILLS_DIR="${CODEX_HOME:-$HOME/.codex}/skills"
    INSTALL_METHOD="manual"
    echo -e "${YELLOW}Warning: Platform not detected, using default: $CODEX_SKILLS_DIR${NC}"
fi

echo -e "Skills directory: ${CYAN}${CODEX_SKILLS_DIR}${NC}\n"

# Method 1: Use skill-installer if available (Codex/Cursor)
SKILL_INSTALLER="$CODEX_SKILLS_DIR/.system/skill-installer/scripts/install-skill-from-github.py"
if [ -f "$SKILL_INSTALLER" ]; then
    echo -e "${GREEN}Method 1: Using skill-installer (recommended)${NC}"
    python3 "$SKILL_INSTALLER" --url "$SKILL_LIBRARY_MANAGER_URL" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ skill-library-manager installed successfully via skill-installer${NC}"
        python3 "$SCRIPT_DIR/verify-installation.py"
        echo -e "${YELLOW}⚠ Please restart your IDE/Codex to pick up the new skill${NC}"
        exit 0
    else
        echo -e "${YELLOW}Installation via skill-installer failed, trying alternative method...${NC}\n"
    fi
fi

# Method 2: Manual installation from local repository
echo -e "${BLUE}Method 2: Manual installation from repository${NC}"

# Find repository location (try common locations)
LOCAL_REPO=""
POSSIBLE_LOCATIONS=(
    "/Users/guillaumebld/Documents/Skills/Skills_librairie"
    "$HOME/Documents/Skills/Skills_librairie"
    "$HOME/Skills_librairie"
    "$HOME/.skills/Skills_librairie"
    "$(dirname "$SCRIPT_DIR")/../../../.."
)

for loc in "${POSSIBLE_LOCATIONS[@]}"; do
    if [ -d "$loc/Skills/skill-library-manager" ]; then
        LOCAL_REPO="$loc"
        break
    fi
done

# If not found, try to clone
if [ -z "$LOCAL_REPO" ]; then
    echo -e "${YELLOW}Repository not found locally. Attempting to clone...${NC}"
    
    if command -v gh &> /dev/null; then
        DEFAULT_LOCATION="$HOME/Documents/Skills/Skills_librairie"
        mkdir -p "$(dirname "$DEFAULT_LOCATION")"
        gh repo clone "$REPO_OWNER/$REPO_NAME" "$DEFAULT_LOCATION" 2>&1
        if [ $? -eq 0 ] && [ -d "$DEFAULT_LOCATION/Skills/skill-library-manager" ]; then
            LOCAL_REPO="$DEFAULT_LOCATION"
        fi
    elif command -v git &> /dev/null; then
        DEFAULT_LOCATION="$HOME/Documents/Skills/Skills_librairie"
        mkdir -p "$(dirname "$DEFAULT_LOCATION")"
        git clone "https://github.com/$REPO_OWNER/$REPO_NAME.git" "$DEFAULT_LOCATION" 2>&1
        if [ $? -eq 0 ] && [ -d "$DEFAULT_LOCATION/Skills/skill-library-manager" ]; then
            LOCAL_REPO="$DEFAULT_LOCATION"
        fi
    else
        echo -e "${RED}Error: Neither GitHub CLI (gh) nor Git found.${NC}"
        echo -e "Please install one of them:"
        echo -e "  GitHub CLI: brew install gh (macOS), or visit https://cli.github.com"
        echo -e "  Git: brew install git (macOS), apt-get install git (Linux)"
        exit 1
    fi
fi

if [ -z "$LOCAL_REPO" ] || [ ! -d "$LOCAL_REPO/Skills/skill-library-manager" ]; then
    echo -e "${RED}Error: Could not locate or clone repository${NC}"
    echo -e "Please manually clone: git clone https://github.com/$REPO_OWNER/$REPO_NAME.git"
    exit 1
fi

echo -e "Using repository at: ${CYAN}${LOCAL_REPO}${NC}"

# Create skills directory
mkdir -p "$CODEX_SKILLS_DIR"

# Check if already installed
if [ -d "$CODEX_SKILLS_DIR/skill-library-manager" ]; then
    echo -e "${YELLOW}skill-library-manager already exists at $CODEX_SKILLS_DIR/skill-library-manager${NC}"
    read -p "Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled"
        exit 0
    fi
    rm -rf "$CODEX_SKILLS_DIR/skill-library-manager"
fi

# Copy skill-library-manager
echo -e "${BLUE}Copying skill-library-manager...${NC}"
cp -r "$LOCAL_REPO/Skills/skill-library-manager" "$CODEX_SKILLS_DIR/"

# Verify installation
echo -e "\n${BLUE}Verifying installation...${NC}"
python3 "$SCRIPT_DIR/verify-installation.py"

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ skill-library-manager installed successfully!${NC}"
    echo -e "${GREEN}  Location: $CODEX_SKILLS_DIR/skill-library-manager${NC}"
    echo -e "${YELLOW}⚠ Please restart your IDE/Codex to pick up the new skill${NC}"
    echo ""
    echo -e "${BLUE}You now have access to the Skills store!${NC}"
    echo -e "  Repository: $LOCAL_REPO"
    echo -e "  Catalog: $LOCAL_REPO/catalog.json"
    echo -e ""
    echo -e "Use the skill-library-manager skill to:"
    echo -e "  - Create new skills: bash $LOCAL_REPO/Skills/skill-library-manager/scripts/create-skill.sh"
    echo -e "  - Search skills: python3 $LOCAL_REPO/Skills/skill-library-manager/scripts/search-skills.py"
    echo -e "  - Sync with GitHub: bash $LOCAL_REPO/Skills/skill-library-manager/scripts/sync-library.sh"
    exit 0
else
    echo -e "${RED}Installation completed but verification failed. Please check the errors above.${NC}"
    exit 1
fi
