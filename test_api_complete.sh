#!/bin/bash

# Complete API Testing with Admin Approval Flow
BASE_URL="http://localhost:8000"
API_BASE="${BASE_URL}/api/v1"

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_section() {
    echo -e "\n${BLUE}========== $1 ==========${NC}\n"
}

PASS=0
FAIL=0

print_section "COMPLETE API TESTING WITH APPROVAL FLOW"

# 1. Login as existing farmer
echo "Logging in as Farmer..."
farmer_login=$(curl -s -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"farmer@greenvalley.com","password":"Farmer@123"}')
FARMER_TOKEN=$(echo "$farmer_login" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Farmer Token: ${FARMER_TOKEN:0:30}..."

# 2. Get farmer's organizations
echo "Getting farmer's organizations..."
orgs=$(curl -s -X GET "${API_BASE}/organizations" \
  -H "Authorization: Bearer $FARMER_TOKEN")
ORG_ID=$(echo "$orgs" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
ORG_STATUS=$(echo "$orgs" | grep -o '"status":"[^"]*' | head -1 | cut -d'"' -f4)
echo "Organization ID: $ORG_ID"
echo "Organization Status: $ORG_STATUS"

# 3. Login as Admin
echo -e "\nLogging in as Admin..."
admin_login=$(curl -s -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@uzhathunai.com","password":"Admin@123"}')
ADMIN_TOKEN=$(echo "$admin_login" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Admin Token: ${ADMIN_TOKEN:0:30}..."

# 4. Admin: Get all organizations
echo -e "\nAdmin getting all organizations..."
admin_orgs=$(curl -s -X GET "${API_BASE}/admin/organizations" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
echo "$admin_orgs" | jq '.' 2>/dev/null || echo "$admin_orgs"

# 5. Admin: Approve the organization
if [ ! -z "$ORG_ID" ] && [ "$ORG_STATUS" = "PENDING" ]; then
    echo -e "\nApproving organization $ORG_ID..."
    approve=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/admin/organizations/${ORG_ID}/approve" \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"approved": true, "notes": "Organization approved for testing"}')
    http_code=$(echo "$approve" | tail -n1)
    body=$(echo "$approve" | head -n-1)
    echo "Approval Status: HTTP $http_code"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
fi

# 6. Farmer: Switch to organization context
echo -e "\nSwitching to organization context..."
switch=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/switch-organization" \
  -H "Authorization: Bearer $FARMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"organization_id\": \"$ORG_ID\"}")
http_code=$(echo "$switch" | tail -n1)
body=$(echo "$switch" | head -n-1)
echo "Switch Status: HTTP $http_code"
if [ "$http_code" = "200" ]; then
    FARMER_TOKEN=$(echo "$body" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "New Token with Org Context: ${FARMER_TOKEN:0:30}..."
fi

print_section "TESTING ENDPOINTS WITH APPROVED ORG CONTEXT"

# Test Reference Data
echo "Testing Reference Data Types..."
ref=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/reference-data/types" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$ref" | tail -n1)
[ "$http_code" = "200" ] && ((PASS++)) && echo -e "${GREEN}✓${NC} Reference Data Types" || ((FAIL++)) && echo -e "${RED}✗${NC} Reference Data Types (HTTP $http_code)"

# Test Measurement Units
echo "Testing Measurement Units..."
units=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/measurement-units/" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$units" | tail -n1)
[ "$http_code" = "200" ] && ((PASS++)) && echo -e "${GREEN}✓${NC} Measurement Units" || ((FAIL++)) && echo -e "${RED}✗${NC} Measurement Units (HTTP $http_code)"

# Test Crop Categories
echo "Testing Crop Categories..."
crop_cat=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/crop-data/categories" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$crop_cat" | tail -n1)
[ "$http_code" = "200" ] && ((PASS++)) && echo -e "${GREEN}✓${NC} Crop Categories" || ((FAIL++)) && echo -e "${RED}✗${NC} Crop Categories (HTTP $http_code)"

# Test Crop Types
echo "Testing Crop Types..."
crop_types=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/crop-data/types" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$crop_types" | tail -n1)
[ "$http_code" = "200" ] && ((PASS++)) && echo -e "${GREEN}✓${NC} Crop Types" || ((FAIL++)) && echo -e "${RED}✗${NC} Crop Types (HTTP $http_code)"

# Test Tasks
echo "Testing Tasks..."
tasks=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/tasks/" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$tasks" | tail -n1)
[ "$http_code" = "200" ] && ((PASS++)) && echo -e "${GREEN}✓${NC} Tasks" || ((FAIL++)) && echo -e "${RED}✗${NC} Tasks (HTTP $http_code)"

# Test Input Items
echo "Testing Input Items..."
input=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/input-items/" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$input" | tail -n1)
[ "$http_code" = "200" ] && ((PASS++)) && echo -e "${GREEN}✓${NC} Input Items" || ((FAIL++)) && echo -e "${RED}✗${NC} Input Items (HTTP $http_code)"

# Test Farms
echo "Testing Farms..."
farms=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/farms/" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$farms" | tail -n1)
[ "$http_code" = "200" ] && ((PASS++)) && echo -e "${GREEN}✓${NC} Farms" || ((FAIL++)) && echo -e "${RED}✗${NC} Farms (HTTP $http_code)"

# Test Crops
echo "Testing Crops..."
crops=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/crops/" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$crops" | tail -n1)
[ "$http_code" = "200" ] && ((PASS++)) && echo -e "${GREEN}✓${NC} Crops" || ((FAIL++)) && echo -e "${RED}✗${NC} Crops (HTTP $http_code)"

# Test Schedules
echo "Testing Schedules..."
schedules=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/schedules" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$schedules" | tail -n1)
[ "$http_code" = "200" ] && ((PASS++)) && echo -e "${GREEN}✓${NC} Schedules" || ((FAIL++)) && echo -e "${RED}✗${NC} Schedules (HTTP $http_code)"

# Test Work Orders
echo "Testing Work Orders..."
wo=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/work-orders" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$wo" | tail -n1)
[ "$http_code" = "200" ] && ((PASS++)) && echo -e "${GREEN}✓${NC} Work Orders" || ((FAIL++)) && echo -e "${RED}✗${NC} Work Orders (HTTP $http_code)"

# Test Queries
echo "Testing Queries..."
queries=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/queries" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$queries" | tail -n1)
[ "$http_code" = "200" ] && ((PASS++)) && echo -e "${GREEN}✓${NC} Queries" || ((FAIL++)) && echo -e "${RED}✗${NC} Queries (HTTP $http_code)"

# Test Notifications
echo "Testing Notifications..."
notif=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/notifications/unread-count" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$notif" | tail -n1)
[ "$http_code" = "200" ] && ((PASS++)) && echo -e "${GREEN}✓${NC} Notifications" || ((FAIL++)) && echo -e "${RED}✗${NC} Notifications (HTTP $http_code)"

# Test Farm Audit
echo "Testing Farm Audit - Audits..."
audits=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/farm-audit/audits" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$audits" | tail -n1)
[ "$http_code" = "200" ] && ((PASS++)) && echo -e "${GREEN}✓${NC} Farm Audit - Audits" || ((FAIL++)) && echo -e "${RED}✗${NC} Farm Audit - Audits (HTTP $http_code)"

print_section "SUMMARY"
TOTAL=$((PASS + FAIL))
echo -e "${GREEN}Passed: $PASS / $TOTAL${NC}"
echo -e "${RED}Failed: $FAIL / $TOTAL${NC}"
echo "Success Rate: $(awk "BEGIN {printf \"%.1f\", ($PASS/$TOTAL)*100}")%"

echo -e "\n${BLUE}Test Users Created:${NC}"
echo "  Admin: admin@uzhathunai.com / Admin@123"
echo "  Farmer: farmer@greenvalley.com / Farmer@123"
echo -e "\n${BLUE}Organization:${NC}"
echo "  ID: $ORG_ID"
echo "  Status: APPROVED"
echo -e "\n${BLUE}Access URLs:${NC}"
echo "  API Docs: ${BASE_URL}/docs"
echo "  Health: ${BASE_URL}/health"
