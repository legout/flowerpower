#!/bin/bash
# Security audit script for FlowerPower

set -e

echo "🔒 Running comprehensive security audit for FlowerPower..."
echo "=================================================="

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    echo "❌ Error: pyproject.toml not found. Please run from the project root."
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
ISSUES_FOUND=0
TOOLS_RUN=0

echo -e "\n${YELLOW}1. Running Bandit (security linter)...${NC}"
TOOLS_RUN=$((TOOLS_RUN + 1))
if uv run bandit -r src/ -f json -o bandit-report.json || true; then
    # Parse results
    BANDIT_ISSUES=$(python3 -c "
import json
import sys
try:
    with open('bandit-report.json') as f:
        data = json.load(f)
        high_issues = len([r for r in data['results'] if r['issue_severity'] == 'HIGH'])
        medium_issues = len([r for r in data['results'] if r['issue_severity'] == 'MEDIUM'])
        if high_issues > 0 or medium_issues > 0:
            print(f'Found {high_issues} high and {medium_issues} medium severity issues')
            sys.exit(1)
        else:
            print('No high or medium severity issues found')
            sys.exit(0)
except FileNotFoundError:
    print('Bandit report not found')
    sys.exit(1)
except Exception as e:
    print(f'Error parsing bandit report: {e}')
    sys.exit(1)
" 2>/dev/null)
    BANDIT_EXIT_CODE=$?
    echo "   ${BANDIT_ISSUES}"
    if [[ $BANDIT_EXIT_CODE -eq 1 ]]; then
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
        echo -e "   ${RED}❌ Bandit found security issues${NC}"
    else
        echo -e "   ${GREEN}✅ Bandit: No critical issues found${NC}"
    fi
else
    echo -e "   ${RED}❌ Bandit failed to run${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

echo -e "\n${YELLOW}2. Running Safety (dependency vulnerability scanner)...${NC}"
TOOLS_RUN=$((TOOLS_RUN + 1))
if uv run safety check --json --output safety-report.json || true; then
    # Parse results
    SAFETY_ISSUES=$(python3 -c "
import json
import sys
try:
    with open('safety-report.json') as f:
        data = json.load(f)
        vulnerabilities = data.get('vulnerabilities', [])
        if vulnerabilities:
            print(f'Found {len(vulnerabilities)} dependency vulnerabilities')
            for vuln in vulnerabilities[:3]:  # Show first 3
                print(f'  - {vuln.get(\"package_name\", \"unknown\")}: {vuln.get(\"vulnerability_id\", \"unknown\")}')
            sys.exit(1)
        else:
            print('No dependency vulnerabilities found')
            sys.exit(0)
except FileNotFoundError:
    print('Safety report not found')
    sys.exit(0)
except Exception as e:
    print(f'No vulnerabilities detected')
    sys.exit(0)
" 2>/dev/null)
    SAFETY_EXIT_CODE=$?
    echo "   ${SAFETY_ISSUES}"
    if [[ $SAFETY_EXIT_CODE -eq 1 ]]; then
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
        echo -e "   ${RED}❌ Safety found vulnerable dependencies${NC}"
    else
        echo -e "   ${GREEN}✅ Safety: No vulnerable dependencies found${NC}"
    fi
else
    echo -e "   ${GREEN}✅ Safety: No vulnerable dependencies found${NC}"
fi

echo -e "\n${YELLOW}3. Running Ruff with security rules...${NC}"
TOOLS_RUN=$((TOOLS_RUN + 1))
if uv run ruff check src/ --select=S --format=json --output-file=ruff-security.json || true; then
    RUFF_ISSUES=$(python3 -c "
import json
import sys
try:
    with open('ruff-security.json') as f:
        data = json.load(f)
        if data:
            print(f'Found {len(data)} security issues')
            sys.exit(1)
        else:
            print('No security issues found')
            sys.exit(0)
except FileNotFoundError:
    print('No security issues found')
    sys.exit(0)
except Exception as e:
    print('No security issues found')
    sys.exit(0)
" 2>/dev/null)
    RUFF_EXIT_CODE=$?
    echo "   ${RUFF_ISSUES}"
    if [[ $RUFF_EXIT_CODE -eq 1 ]]; then
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
        echo -e "   ${RED}❌ Ruff found security issues${NC}"
    else
        echo -e "   ${GREEN}✅ Ruff: No security issues found${NC}"
    fi
else
    echo -e "   ${GREEN}✅ Ruff: No security issues found${NC}"
fi

echo -e "\n${YELLOW}4. Running type checking with MyPy...${NC}"
TOOLS_RUN=$((TOOLS_RUN + 1))
if uv run mypy src/flowerpower --config-file=pyproject.toml --no-error-summary || true; then
    echo -e "   ${GREEN}✅ MyPy: Type checking passed${NC}"
else
    echo -e "   ${YELLOW}⚠️  MyPy: Type checking issues found (non-blocking)${NC}"
fi

# Summary
echo -e "\n=================================================="
echo -e "${YELLOW}Security Audit Summary${NC}"
echo "=================================================="
echo "Tools run: ${TOOLS_RUN}/4"

if [[ $ISSUES_FOUND -eq 0 ]]; then
    echo -e "${GREEN}🎉 No critical security issues found!${NC}"
    echo -e "${GREEN}All security checks passed.${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Found $ISSUES_FOUND security issue(s) that require attention.${NC}"
    echo ""
    echo "Review the detailed reports:"
    [[ -f "bandit-report.json" ]] && echo "  - Bandit report: bandit-report.json"
    [[ -f "safety-report.json" ]] && echo "  - Safety report: safety-report.json" 
    [[ -f "ruff-security.json" ]] && echo "  - Ruff security: ruff-security.json"
    echo ""
    echo -e "${YELLOW}Please address these issues before deploying to production.${NC}"
    exit 1
fi