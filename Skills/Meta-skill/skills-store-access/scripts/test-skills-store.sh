#!/bin/bash
set -e

# Test Skills Store Access
# Comprehensive test suite to verify Skills store is working correctly

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

PASSED=0
FAILED=0

test_check() {
    local name="$1"
    local command="$2"
    
    echo -n "Testing $name... "
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
        return 1
    fi
}

echo -e "${BLUE}=== Testing Skills Store Access ===${NC}\n"

# Test 1: Platform Detection
echo -e "${CYAN}Test 1: Platform Detection${NC}"
test_check "Platform detection script exists" "[ -f '$SCRIPT_DIR/detect-platform.py' ]"
test_check "Platform detection runs" "python3 '$SCRIPT_DIR/detect-platform.py' > /dev/null 2>&1"

# Test 2: Verification Script
echo -e "\n${CYAN}Test 2: Verification Script${NC}"
test_check "Verification script exists" "[ -f '$SCRIPT_DIR/verify-installation.py' ]"
test_check "Verification script runs" "python3 '$SCRIPT_DIR/verify-installation.py' > /dev/null 2>&1"

# Test 3: Equip Script
echo -e "\n${CYAN}Test 3: Equip Script${NC}"
test_check "Equip script exists" "[ -f '$SCRIPT_DIR/equip-skills-store.sh' ]"
test_check "Equip script is executable" "[ -x '$SCRIPT_DIR/equip-skills-store.sh' ]"

# Test 4: Skill Installation (if on Codex/Cursor)
echo -e "\n${CYAN}Test 4: Skill Installation${NC}"
CODEX_SKILLS="${CODEX_HOME:-$HOME/.codex}/skills"
if [ -d "$CODEX_SKILLS" ]; then
    test_check "Skills directory exists" "[ -d '$CODEX_SKILLS' ]"
    test_check "skill-library-manager installed" "[ -d '$CODEX_SKILLS/skill-library-manager' ]"
    if [ -d "$CODEX_SKILLS/skill-library-manager" ]; then
        test_check "SKILL.md exists" "[ -f '$CODEX_SKILLS/skill-library-manager/SKILL.md' ]"
        test_check "Scripts directory exists" "[ -d '$CODEX_SKILLS/skill-library-manager/scripts' ]"
    else
        echo -e "${YELLOW}  ⚠ skill-library-manager not installed (run equip-skills-store.sh)${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠ Skills directory not found (may be on different platform)${NC}"
fi

# Test 5: Repository Access
echo -e "\n${CYAN}Test 5: Repository Access${NC}"
REPO_LOCATIONS=(
    "/Users/guillaumebld/Documents/Skills/Skills_librairie"
    "$HOME/Documents/Skills/Skills_librairie"
    "$HOME/Skills_librairie"
)
REPO_FOUND=0
for repo in "${REPO_LOCATIONS[@]}"; do
    if [ -d "$repo/Skills/skill-library-manager" ]; then
        REPO_FOUND=1
        REPO_PATH="$repo"
        break
    fi
done

if [ $REPO_FOUND -eq 1 ]; then
    test_check "Repository exists" "[ -d '$REPO_PATH' ]"
    test_check "skill-library-manager in repo" "[ -d '$REPO_PATH/Skills/skill-library-manager' ]"
    test_check "Scripts in repo" "[ -d '$REPO_PATH/Skills/skill-library-manager/scripts' ]"
    test_check "catalog-builder.py exists" "[ -f '$REPO_PATH/Skills/skill-library-manager/scripts/catalog-builder.py' ]"
    test_check "search-skills.py exists" "[ -f '$REPO_PATH/Skills/skill-library-manager/scripts/search-skills.py' ]"
else
    echo -e "${YELLOW}  ⚠ Repository not found locally (may need to clone)${NC}"
fi

# Test 6: Required Tools
echo -e "\n${CYAN}Test 6: Required Tools${NC}"
test_check "Python 3 available" "python3 --version > /dev/null 2>&1"
test_check "Git available" "git --version > /dev/null 2>&1"
if command -v gh &> /dev/null; then
    test_check "GitHub CLI available" "gh --version > /dev/null 2>&1"
    test_check "GitHub CLI authenticated" "gh auth status > /dev/null 2>&1"
else
    echo -e "${YELLOW}  ⚠ GitHub CLI (gh) not found (optional but recommended)${NC}"
fi

# Test 7: Skill Functionality (if repository available)
if [ $REPO_FOUND -eq 1 ]; then
    echo -e "\n${CYAN}Test 7: Skill Functionality${NC}"
    cd "$REPO_PATH"
    
    # Test catalog builder (if Python deps available)
    if python3 -c "import yaml, json" 2>/dev/null; then
        test_check "Catalog builder can import dependencies" "python3 -c 'import yaml, json' > /dev/null 2>&1"
    else
        echo -e "${YELLOW}  ⚠ Python dependencies missing (pip install pyyaml)${NC}"
    fi
    
    # Test search script (if catalog exists)
    if [ -f "catalog.json" ]; then
        test_check "Search script works" "python3 Skills/skill-library-manager/scripts/search-skills.py --all > /dev/null 2>&1"
    else
        echo -e "${YELLOW}  ⚠ catalog.json not found (run catalog-builder.py to generate)${NC}"
    fi
fi

# Summary
echo -e "\n${BLUE}=== Test Summary ===${NC}"
echo -e "Passed: ${GREEN}${PASSED}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed! Skills Store Access is ready to use.${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠ Some tests failed. Please review the errors above.${NC}"
    echo -e "Run verification: python3 '$SCRIPT_DIR/verify-installation.py'"
    exit 1
fi
