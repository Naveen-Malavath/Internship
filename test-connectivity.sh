#!/bin/bash

# Backend-Frontend Connectivity Test Script

echo "=========================================="
echo "Backend-Frontend Connectivity Test"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Backend Root Endpoint
echo "Test 1: Backend Root Endpoint"
echo "----------------------------"
if curl -s http://localhost:8000/ > /dev/null; then
    echo -e "${GREEN}✓ Backend is running on port 8000${NC}"
    curl -s http://localhost:8000/ | head -1
else
    echo -e "${RED}✗ Backend is NOT running on port 8000${NC}"
    echo "   Start backend with: cd autoagents-backend && uvicorn app.main:app --reload"
fi
echo ""

# Test 2: Frontend Accessibility
echo "Test 2: Frontend Accessibility"
echo "----------------------------"
if curl -s http://localhost:4200/ > /dev/null; then
    echo -e "${GREEN}✓ Frontend is running on port 4200${NC}"
else
    echo -e "${RED}✗ Frontend is NOT running on port 4200${NC}"
    echo "   Start frontend with: cd autoagents-frontend && npm start"
fi
echo ""

# Test 3: CORS Configuration
echo "Test 3: CORS Configuration"
echo "----------------------------"
CORS_RESPONSE=$(curl -s -X OPTIONS -H "Origin: http://localhost:4200" \
    -H "Access-Control-Request-Method: GET" \
    -H "Access-Control-Request-Headers: Content-Type" \
    -w "\n%{http_code}" \
    http://localhost:8000/projects 2>&1)

HTTP_CODE=$(echo "$CORS_RESPONSE" | tail -1)
if [ "$HTTP_CODE" = "204" ] || [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ CORS preflight request successful (HTTP $HTTP_CODE)${NC}"
    
    # Check for CORS headers
    CORS_HEADERS=$(curl -s -X OPTIONS -H "Origin: http://localhost:4200" \
        -H "Access-Control-Request-Method: GET" \
        -I http://localhost:8000/projects 2>&1 | grep -i "access-control")
    
    if [ -n "$CORS_HEADERS" ]; then
        echo -e "${GREEN}✓ CORS headers present:${NC}"
        echo "$CORS_HEADERS" | sed 's/^/   /'
    else
        echo -e "${YELLOW}⚠ CORS headers not found in response${NC}"
    fi
else
    echo -e "${RED}✗ CORS preflight request failed (HTTP $HTTP_CODE)${NC}"
fi
echo ""

# Test 4: API Documentation
echo "Test 4: API Documentation"
echo "----------------------------"
if curl -s http://localhost:8000/docs | grep -q "Swagger UI"; then
    echo -e "${GREEN}✓ API documentation available at http://localhost:8000/docs${NC}"
else
    echo -e "${YELLOW}⚠ API documentation not accessible${NC}"
fi
echo ""

# Test 5: Environment Configuration
echo "Test 5: Environment Configuration Check"
echo "----------------------------"
if [ -f "autoagents-frontend/src/environments/environment.ts" ]; then
    API_URL=$(grep -o "apiUrl: '[^']*'" autoagents-frontend/src/environments/environment.ts | cut -d"'" -f2)
    echo "Frontend API URL: $API_URL"
    if [ "$API_URL" = "http://localhost:8000" ]; then
        echo -e "${GREEN}✓ Frontend API URL is correctly configured${NC}"
    else
        echo -e "${YELLOW}⚠ Frontend API URL is set to: $API_URL${NC}"
        echo "   Expected: http://localhost:8000"
    fi
else
    echo -e "${RED}✗ Environment file not found${NC}"
fi
echo ""

# Test 6: Network Connectivity
echo "Test 6: Network Connectivity"
echo "----------------------------"
if ping -c 1 localhost > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Localhost connectivity OK${NC}"
else
    echo -e "${RED}✗ Localhost connectivity issues${NC}"
fi
echo ""

# Summary
echo "=========================================="
echo "Summary"
echo "=========================================="
echo "If all tests pass, the connectivity should be working."
echo "If any test fails, check:"
echo "  1. Backend is running: cd autoagents-backend && uvicorn app.main:app --reload"
echo "  2. Frontend is running: cd autoagents-frontend && npm start"
echo "  3. Check browser console (F12) for errors"
echo "  4. Check browser Network tab for failed requests"
echo ""

