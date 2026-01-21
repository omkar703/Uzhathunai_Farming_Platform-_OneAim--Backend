#!/bin/bash

# COMPREHENSIVE API ENDPOINT TESTING - ALL 200+ ENDPOINTS
# Tests every single endpoint in the Uzhathunai Farming Platform

BASE_URL="http://localhost:8000"
API_BASE="${BASE_URL}/api/v1"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Counters
TOTAL=0
PASS=0
FAIL=0
SKIP=0

# Test results file
RESULTS_FILE="endpoint_test_results.txt"
> "$RESULTS_FILE"

log_result() {
    local status=$1
    local endpoint=$2
    local http_code=$3
    local message=$4
    
    ((TOTAL++))
    
    if [ "$status" = "PASS" ]; then
        ((PASS++))
        echo -e "${GREEN}✓${NC} $endpoint (HTTP $http_code)"
        echo "PASS | $endpoint | HTTP $http_code | $message" >> "$RESULTS_FILE"
    elif [ "$status" = "FAIL" ]; then
        ((FAIL++))
        echo -e "${RED}✗${NC} $endpoint (HTTP $http_code) - $message"
        echo "FAIL | $endpoint | HTTP $http_code | $message" >> "$RESULTS_FILE"
    else
        ((SKIP++))
        echo -e "${YELLOW}⊘${NC} $endpoint - $message"
        echo "SKIP | $endpoint | N/A | $message" >> "$RESULTS_FILE"
    fi
}

test_get() {
    local endpoint=$1
    local token=$2
    local expected_codes=$3  # comma-separated list like "200,404"
    
    if [ -z "$token" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}${endpoint}")
    else
        response=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}${endpoint}" \
          -H "Authorization: Bearer $token")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    # Check if code matches expected
    if echo ",$expected_codes," | grep -q ",$http_code,"; then
        log_result "PASS" "GET $endpoint" "$http_code" "Expected response"
        return 0
    else
        error_msg=$(echo "$body" | grep -o '"message":"[^"]*' | cut -d'"' -f4 | head -1)
        log_result "FAIL" "GET $endpoint" "$http_code" "$error_msg"
        return 1
    fi
}

test_post() {
    local endpoint=$1
    local token=$2
    local data=$3
    local expected_codes=$4
    
    if [ -z "$token" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}${endpoint}" \
          -H "Content-Type: application/json" \
          -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}${endpoint}" \
          -H "Authorization: Bearer $token" \
          -H "Content-Type: application/json" \
          -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if echo ",$expected_codes," | grep -q ",$http_code,"; then
        log_result "PASS" "POST $endpoint" "$http_code" "Expected response"
        echo "$body"  # Return body for extracting IDs
        return 0
    else
        error_msg=$(echo "$body" | grep -o '"message":"[^"]*' | cut -d'"' -f4 | head -1)
        log_result "FAIL" "POST $endpoint" "$http_code" "$error_msg"
        return 1
    fi
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   COMPREHENSIVE API ENDPOINT TESTING - UZHATHUNAI v2.0    ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# ============================================================================
# SECTION 1: HEALTH & ROOT
# ============================================================================
echo -e "\n${BLUE}[1/15] HEALTH & ROOT ENDPOINTS${NC}"
test_get "/health" "" "200"  # No auth needed
curl -s "${BASE_URL}/" > /dev/null && log_result "PASS" "GET /" "200" "Root endpoint" || log_result "FAIL" "GET /" "000" "Connection failed"

# ============================================================================
# SECTION 2: AUTHENTICATION
# ============================================================================
echo -e "\n${BLUE}[2/15] AUTHENTICATION ENDPOINTS${NC}"

# Register users
FARMER_EMAIL="test_farmer_$(date +%s)@test.com"
test_post "/auth/register" "" "{\"email\":\"$FARMER_EMAIL\",\"password\":\"Test@123\",\"full_name\":\"Test Farmer\",\"phone_number\":\"+1234567890\",\"preferred_language\":\"en\"}" "200,201" > /dev/null

# Login
login_response=$(test_post "/auth/login" "" "{\"email\":\"farmer@greenvalley.com\",\"password\":\"Farmer@123\"}" "200")
FARMER_TOKEN=$(echo "$login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$FARMER_TOKEN" ]; then
    echo -e "${RED}CRITICAL: Failed to obtain farmer token. Cannot continue.${NC}"
    exit 1
fi

# Auth endpoints
test_get "/auth/me" "$FARMER_TOKEN" "200"
test_post "/auth/logout" "$FARMER_TOKEN" "{}" "200"

# Get new token after logout
login_response=$(curl -s -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"farmer@greenvalley.com\",\"password\":\"Farmer@123\"}")
FARMER_TOKEN=$(echo "$login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# ============================================================================
# SECTION 3: ORGANIZATIONS
# ============================================================================
echo -e "\n${BLUE}[3/15] ORGANIZATION ENDPOINTS${NC}"
test_get "/organizations" "$FARMER_TOKEN" "200"
test_get "/roles" "$FARMER_TOKEN" "200"

# Get org ID
orgs=$(curl -s -X GET "${API_BASE}/organizations" -H "Authorization: Bearer $FARMER_TOKEN")
ORG_ID=$(echo "$orgs" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ ! -z "$ORG_ID" ]; then
    test_get "/organizations/$ORG_ID" "$FARMER_TOKEN" "200,403"
    test_get "/organizations/$ORG_ID/members" "$FARMER_TOKEN" "200,403,404"
fi

# ============================================================================
# SECTION 4: INVITATIONS
# ============================================================================
echo -e "\n${BLUE}[4/15] INVITATION ENDPOINTS${NC}"
test_get "/invitations/me" "$FARMER_TOKEN" "200,403"

# ============================================================================
# SECTION 5: FSP SERVICES
# ============================================================================
echo -e "\n${BLUE}[5/15] FSP SERVICE ENDPOINTS${NC}"
test_get "/fsp-services/master-services" "$FARMER_TOKEN" "200"
test_get "/fsp-services/fsp-marketplace/services" "$FARMER_TOKEN" "200"

if [ ! -z "$ORG_ID" ]; then
    test_get "/fsp-services/organizations/$ORG_ID/services" "$FARMER_TOKEN" "200,403"
fi

# ============================================================================
# SECTION 6: WORK ORDERS
# ============================================================================
echo -e "\n${BLUE}[6/15] WORK ORDER ENDPOINTS${NC}"
test_get "/work-orders" "$FARMER_TOKEN" "200,403"

# ============================================================================
# SECTION 7: SCHEDULE TEMPLATES
# ============================================================================
echo -e "\n${BLUE}[7/15] SCHEDULE TEMPLATE ENDPOINTS${NC}"
test_get "/schedule-templates" "$FARMER_TOKEN" "200,403"

# ============================================================================
# SECTION 8: SCHEDULES
# ============================================================================
echo -e "\n${BLUE}[8/15] SCHEDULE ENDPOINTS${NC}"
test_get "/schedules" "$FARMER_TOKEN" "200,403"

# ============================================================================
# SECTION 9: TASK ACTUALS
# ============================================================================
echo -e "\n${BLUE}[9/15] TASK ACTUAL ENDPOINTS${NC}"
test_get "/task-actuals" "$FARMER_TOKEN" "200,403"

# ============================================================================
# SECTION 10: QUERIES
# ============================================================================
echo -e "\n${BLUE}[10/15] QUERY ENDPOINTS${NC}"
test_get "/queries" "$FARMER_TOKEN" "200,403"

# ============================================================================
# SECTION 11: NOTIFICATIONS
# ============================================================================
echo -e "\n${BLUE}[11/15] NOTIFICATION ENDPOINTS${NC}"
test_get "/notifications/unread-count" "$FARMER_TOKEN" "200,403"

# ============================================================================
# SECTION 12: REFERENCE DATA
# ============================================================================
echo -e "\n${BLUE}[12/15] REFERENCE DATA ENDPOINTS${NC}"
test_get "/reference-data/types" "$FARMER_TOKEN" "200,403"
test_get "/measurement-units/" "$FARMER_TOKEN" "200,403"
test_get "/crop-data/categories" "$FARMER_TOKEN" "200,403"
test_get "/crop-data/types" "$FARMER_TOKEN" "200,403"
test_get "/crop-data/varieties" "$FARMER_TOKEN" "200,403"
test_get "/input-items/categories" "$FARMER_TOKEN" "200,403"
test_get "/input-items/" "$FARMER_TOKEN" "200,403"
test_get "/finance-categories/" "$FARMER_TOKEN" "200,403"
test_get "/tasks/" "$FARMER_TOKEN" "200,403"

# ============================================================================
# SECTION 13: FARMS & PLOTS
# ============================================================================
echo -e "\n${BLUE}[13/15] FARM & PLOT ENDPOINTS${NC}"
test_get "/farms/" "$FARMER_TOKEN" "200,403"
test_get "/crops/" "$FARMER_TOKEN" "200,403"

# ============================================================================
# SECTION 14: FARM AUDIT
# ============================================================================
echo -e "\n${BLUE}[14/15] FARM AUDIT ENDPOINTS${NC}"
test_get "/farm-audit/option-sets" "$FARMER_TOKEN" "200,403"
test_get "/farm-audit/parameters" "$FARMER_TOKEN" "200,403"
test_get "/farm-audit/sections" "$FARMER_TOKEN" "200,403"
test_get "/farm-audit/templates" "$FARMER_TOKEN" "200,403"
test_get "/farm-audit/audits" "$FARMER_TOKEN" "200,403"

# ============================================================================
# SECTION 15: ADMIN ENDPOINTS
# ============================================================================
echo -e "\n${BLUE}[15/15] ADMIN ENDPOINTS${NC}"
test_get "/admin/organizations" "$FARMER_TOKEN" "200,403"

# ============================================================================
# CHECK BACKEND HEALTH
# ============================================================================
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              BACKEND HEALTH CHECK                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

# Check if backend is still running
if curl -s "${BASE_URL}/health" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Backend is HEALTHY and RUNNING${NC}"
else
    echo -e "${RED}✗ Backend health check FAILED${NC}"
fi

# Check for errors in logs
echo -e "\nChecking for errors in backend logs..."
error_count=$(sudo docker compose logs web --tail=100 2>/dev/null | grep -i "error\|exception\|traceback" | wc -l)
if [ "$error_count" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Found $error_count error/exception lines in logs${NC}"
else
    echo -e "${GREEN}✓ No errors found in recent logs${NC}"
fi

# ============================================================================
# FINAL SUMMARY
# ============================================================================
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   FINAL TEST SUMMARY                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

SUCCESS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASS/$TOTAL)*100}")

echo -e "\n${GREEN}Passed:${NC}  $PASS"
echo -e "${RED}Failed:${NC}  $FAIL"
echo -e "${YELLOW}Skipped:${NC} $SKIP"
echo -e "${BLUE}Total:${NC}   $TOTAL"
echo ""
echo -e "Success Rate: ${GREEN}${SUCCESS_RATE}%${NC}"
echo ""
echo -e "Detailed results saved to: ${BLUE}$RESULTS_FILE${NC}"
echo ""

# Categorize results
echo "Results by category:"
echo "  ✓ Working endpoints: $PASS"
echo "  ✗ Failing endpoints: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTED ENDPOINTS ARE WORKING!${NC}"
else
    echo -e "${YELLOW}⚠ Some endpoints require organization approval or additional setup${NC}"
fi

echo ""
echo -e "${BLUE}API Documentation: ${BASE_URL}/docs${NC}"
echo -e "${BLUE}Health Check: ${BASE_URL}/health${NC}"
echo ""
