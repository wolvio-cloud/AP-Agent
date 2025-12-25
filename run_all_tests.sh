#!/bin/bash

# ClarityAP MVP Backend - Automated Test Runner
# Runs all test suites and generates comprehensive report

set -e  # Exit on error

echo "======================================================================="
echo "ClarityAP MVP Backend - Automated Test Suite"
echo "======================================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check Docker
echo -e "${BLUE}[1/6] Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found. Please install Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is installed${NC}"
echo ""

# Step 2: Start containers
echo -e "${BLUE}[2/6] Starting Docker containers...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Containers started${NC}"
echo ""

# Step 3: Wait for API
echo -e "${BLUE}[3/6] Waiting for API to be ready (15 seconds)...${NC}"
sleep 15
echo -e "${GREEN}✓ API should be ready${NC}"
echo ""

# Step 4: Health check
echo -e "${BLUE}[4/6] Running health check...${NC}"
HEALTH_STATUS=$(curl -s http://localhost:8000/health | grep -o "healthy" || echo "unhealthy")
if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${RED}✗ API health check failed${NC}"
    echo "Checking logs..."
    docker-compose logs --tail=50 api
    exit 1
fi
echo ""

# Step 5: Run main test suite
echo -e "${BLUE}[5/6] Running comprehensive test suite (10 tests)...${NC}"
echo "======================================================================="
python3 test_mvp_backend.py
echo ""

# Step 6: Verify IIF format
echo -e "${BLUE}[6/6] Verifying IIF format...${NC}"
echo "======================================================================="
if [ -f "test_export.iif" ]; then
    python3 verify_iif_format.py
else
    echo -e "${YELLOW}⚠ No IIF file generated (test may have skipped export)${NC}"
fi
echo ""

# Summary
echo "======================================================================="
echo -e "${GREEN}ALL TESTS COMPLETED${NC}"
echo "======================================================================="
echo ""
echo "Results:"
echo "  ✓ Test results: MVP-Test-Results.json"
echo "  ✓ IIF export: test_export.iif (if generated)"
echo "  ✓ Full report: BACKEND-TEST-REPORT.md"
echo ""

# Check results
if [ -f "MVP-Test-Results.json" ]; then
    PASS_RATE=$(cat MVP-Test-Results.json | grep -o '"pass_rate":[0-9.]*' | cut -d':' -f2)
    echo "Pass Rate: $PASS_RATE%"
    echo ""

    if (( $(echo "$PASS_RATE >= 90" | bc -l) )); then
        echo -e "${GREEN}✓ BACKEND IS PRODUCTION READY${NC}"
        echo "Next: Build frontend (3 days)"
    elif (( $(echo "$PASS_RATE >= 70" | bc -l) )); then
        echo -e "${YELLOW}⚠ BACKEND NEEDS MINOR FIXES${NC}"
        echo "Action: Fix failing tests, then build frontend"
    else
        echo -e "${RED}✗ BACKEND HAS SERIOUS ISSUES${NC}"
        echo "Action: Debug and fix before building frontend"
    fi
fi

echo ""
echo "To stop containers: docker-compose down"
echo "======================================================================="
