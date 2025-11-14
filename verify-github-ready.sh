#!/bin/bash

# Repository Pre-Upload Verification Script
# SmartCitySense - GitHub Upload Readiness Check

set -e

echo "🔍 SmartCitySense - GitHub Upload Readiness Check"
echo "================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
checks_passed=0
checks_failed=0
warnings=0

# Check function
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((checks_passed++))
    else
        echo -e "${RED}✗${NC} $1"
        ((checks_failed++))
    fi
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((warnings++))
}

# 1. Git Repository Check
echo "1. Checking Git Repository..."
if [ -d .git ]; then
    check "Git repository initialized"
else
    echo -e "${RED}✗${NC} Git repository not initialized"
    ((checks_failed++))
    exit 1
fi

# 2. Branch Check
current_branch=$(git branch --show-current)
if [ "$current_branch" = "main" ]; then
    check "On main branch"
else
    warn "Not on main branch (current: $current_branch)"
fi

# 3. Commit Check
commit_count=$(git rev-list --count HEAD)
if [ "$commit_count" -gt 0 ]; then
    check "Repository has commits ($commit_count total)"
else
    echo -e "${RED}✗${NC} No commits found"
    ((checks_failed++))
fi

# 4. File Structure Check
echo ""
echo "2. Checking Project Structure..."

required_files=(
    "README.md"
    "LICENSE"
    ".gitignore"
    "CONTRIBUTING.md"
    "ai-ml/main.py"
    "backend/app/main.py"
    "data-ingestion/main_realtime.py"
    "data-processing/main.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        check "Found: $file"
    else
        echo -e "${RED}✗${NC} Missing: $file"
        ((checks_failed++))
    fi
done

# 5. Sensitive Files Check
echo ""
echo "3. Checking for Sensitive Files..."

sensitive_patterns=(
    "firebase-credentials.json"
    ".env"
)

found_sensitive=false
for pattern in "${sensitive_patterns[@]}"; do
    # Check if any sensitive files are staged
    staged_files=$(git diff --cached --name-only | grep "$pattern" || true)
    if [ ! -z "$staged_files" ]; then
        echo -e "${RED}✗${NC} DANGER: Sensitive file staged: $staged_files"
        found_sensitive=true
        ((checks_failed++))
    fi
done

if [ "$found_sensitive" = false ]; then
    check "No sensitive files in staging area"
fi

# 6. .gitignore Check
echo ""
echo "4. Checking .gitignore Configuration..."

gitignore_patterns=(
    "firebase-credentials.json"
    ".env"
    "__pycache__"
    "node_modules"
    "*.log"
)

for pattern in "${gitignore_patterns[@]}"; do
    if grep -q "$pattern" .gitignore; then
        check "Pattern in .gitignore: $pattern"
    else
        echo -e "${RED}✗${NC} Missing pattern in .gitignore: $pattern"
        ((checks_failed++))
    fi
done

# 7. Requirements Files Check
echo ""
echo "5. Checking Requirements Files..."

requirement_files=(
    "ai-ml/requirements.txt"
    "backend/requirements.txt"
    "data-ingestion/requirements.txt"
    "data-processing/requirements.txt"
)

for req_file in "${requirement_files[@]}"; do
    if [ -f "$req_file" ]; then
        line_count=$(wc -l < "$req_file")
        if [ "$line_count" -gt 0 ]; then
            check "Valid: $req_file ($line_count packages)"
        else
            warn "Empty: $req_file"
        fi
    else
        echo -e "${RED}✗${NC} Missing: $req_file"
        ((checks_failed++))
    fi
done

# 8. Documentation Check
echo ""
echo "6. Checking Documentation..."

if [ -f "README.md" ]; then
    readme_size=$(wc -l < README.md)
    if [ "$readme_size" -gt 50 ]; then
        check "README.md is comprehensive ($readme_size lines)"
    else
        warn "README.md seems short ($readme_size lines)"
    fi
fi

module_readmes=(
    "ai-ml/README.md"
    "backend/README.md"
    "data-ingestion/README.md"
    "data-processing/README.md"
)

for readme in "${module_readmes[@]}"; do
    if [ -f "$readme" ]; then
        check "Found: $readme"
    else
        warn "Missing module README: $readme"
    fi
done

# 9. Check for uncommitted changes
echo ""
echo "7. Checking Working Directory..."

if git diff-index --quiet HEAD --; then
    check "No uncommitted changes"
else
    warn "You have uncommitted changes"
    echo "   Run: git status"
fi

# 10. Remote Check
echo ""
echo "8. Checking Git Remote..."

remote_url=$(git remote get-url origin 2>/dev/null || echo "")
if [ -z "$remote_url" ]; then
    warn "No remote 'origin' configured"
    echo "   Add remote: git remote add origin <URL>"
else
    check "Remote 'origin' configured: $remote_url"
fi

# 11. File Count
echo ""
echo "9. Repository Statistics..."

total_files=$(git ls-files | wc -l)
echo -e "${GREEN}✓${NC} Total tracked files: $total_files"

python_files=$(git ls-files | grep -c "\.py$" || true)
echo -e "${GREEN}✓${NC} Python files: $python_files"

typescript_files=$(git ls-files | grep -c "\.tsx\?$" || true)
echo -e "${GREEN}✓${NC} TypeScript/TSX files: $typescript_files"

# 12. Check for large files
echo ""
echo "10. Checking File Sizes..."

large_files=$(git ls-files | xargs ls -l 2>/dev/null | awk '$5 > 10485760 {print $9, $5}' || true)
if [ -z "$large_files" ]; then
    check "No files larger than 10MB"
else
    warn "Large files found (>10MB):"
    echo "$large_files" | while read file size; do
        size_mb=$((size / 1048576))
        echo "   - $file (${size_mb}MB)"
    done
fi

# 13. Code Quality Check (if available)
echo ""
echo "11. Quick Code Quality Check..."

if command -v flake8 &> /dev/null; then
    python_errors=$(find . -name "*.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" | xargs flake8 --count --select=E9,F63,F7,F82 --show-source --statistics 2>/dev/null || echo "0")
    if [ "$python_errors" = "0" ]; then
        check "No critical Python syntax errors"
    else
        warn "Found Python syntax errors"
    fi
else
    warn "flake8 not installed (optional check skipped)"
fi

# Summary
echo ""
echo "================================================="
echo "📊 VERIFICATION SUMMARY"
echo "================================================="
echo -e "Checks Passed: ${GREEN}$checks_passed${NC}"
echo -e "Checks Failed: ${RED}$checks_failed${NC}"
echo -e "Warnings: ${YELLOW}$warnings${NC}"
echo ""

if [ $checks_failed -eq 0 ]; then
    echo -e "${GREEN}✅ REPOSITORY IS READY FOR GITHUB!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Create repository on GitHub"
    echo "2. Run: git remote add origin <your-repo-url>"
    echo "3. Run: git push -u origin main"
    echo ""
    echo "See GITHUB_UPLOAD_GUIDE.md for detailed instructions"
    exit 0
else
    echo -e "${RED}❌ REPOSITORY HAS ISSUES${NC}"
    echo ""
    echo "Please fix the failed checks before uploading to GitHub"
    echo "Review the errors above and make necessary corrections"
    exit 1
fi
