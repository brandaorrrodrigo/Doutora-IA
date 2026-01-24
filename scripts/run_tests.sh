#!/bin/bash

# ============================================
# DOUTORA IA - TEST RUNNER
# ============================================

set -e

cd "$(dirname "$0")/.."

echo "================================"
echo "DOUTORA IA - Running Tests"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if in API directory
if [ ! -f "api/pytest.ini" ]; then
    echo -e "${RED}Error: Must run from project root${NC}"
    exit 1
fi

# Install test dependencies if needed
echo -e "${YELLOW}1/4 Installing test dependencies...${NC}"
cd api
pip install -q -r requirements-test.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Run linting (optional)
if command -v flake8 &> /dev/null; then
    echo -e "${YELLOW}2/4 Running linter...${NC}"
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
    echo -e "${GREEN}✓ Linting complete${NC}"
    echo ""
else
    echo -e "${YELLOW}2/4 Skipping linter (flake8 not installed)${NC}"
    echo ""
fi

# Run tests
echo -e "${YELLOW}3/4 Running test suite...${NC}"
pytest tests/ \
    --verbose \
    --cov=. \
    --cov-report=html \
    --cov-report=term-missing \
    --junit-xml=test-results.xml \
    "$@"

TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi
echo ""

# Generate coverage report
echo -e "${YELLOW}4/4 Generating coverage report...${NC}"
if [ -f "htmlcov/index.html" ]; then
    echo -e "${GREEN}✓ Coverage report generated: api/htmlcov/index.html${NC}"

    # Try to open in browser (optional)
    if command -v xdg-open &> /dev/null; then
        xdg-open htmlcov/index.html 2>/dev/null || true
    elif command -v open &> /dev/null; then
        open htmlcov/index.html 2>/dev/null || true
    fi
fi
echo ""

echo "================================"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}TEST SUITE PASSED ✓${NC}"
else
    echo -e "${RED}TEST SUITE FAILED ✗${NC}"
fi
echo "================================"

exit $TEST_EXIT_CODE
