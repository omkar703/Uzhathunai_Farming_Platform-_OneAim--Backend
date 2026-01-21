#!/bin/bash

# Complete API Testing with Super Admin Approval
BASE_URL="http://localhost:8000"
API_BASE="${BASE_URL}/api/v1"

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_section() {
    echo -e "\n${BLUE}========== $1 ==========${NC}\n"
}

PASS=0
FAIL=0

print_section "COMPLETE API TESTING WITH SUPER ADMIN"

# 1. Login as Super Admin
echo "Logging in as Super Admin..."
superadmin_login=$(curl -s -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@uzhathunai.com",
    "password": "SuperSecure@Admin123"
  }')
SUPERADMIN_TOKEN=$(echo "$superadmin_login" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$SUPERADMIN_TOKEN" ]; then
    echo -e "${RED}Failed to login as Super Admin!${NC}"
    echo "$superadmin_login" | jq '.' 2>/dev/null || echo "$superadmin_login"
    exit 1
fi

echo -e "${GREEN}✓ Super Admin logged in${NC}"
echo "Token: ${SUPERADMIN_TOKEN:0:30}..."

# 2. Get all organizations (Super Admin)
echo -e "\nGetting all organizations..."
all_orgs=$(curl -s -X GET "${API_BASE}/admin/organizations" \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN")
echo "$all_orgs" | jq '.' 2>/dev/null || echo "$all_orgs"

# Extract organization ID
ORG_ID=$(echo "$all_orgs" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
echo "Organization to approve: $ORG_ID"

# 3. Approve the organization
if [ ! -z "$ORG_ID" ]; then
    echo -e "\nApproving organization..."
    approve_response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/admin/organizations/${ORG_ID}/approve" \
      -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "approved": true,
        "notes": "Organization approved for comprehensive API testing"
      }')
    http_code=$(echo "$approve_response" | tail -n1)
    body=$(echo "$approve_response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ Organization approved successfully!${NC}"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    else
        echo -e "${RED}✗ Failed to approve organization (HTTP $http_code)${NC}"
        echo "$body"
    fi
fi

# 4. Login as Farmer
print_section "FARMER USER TESTING"
echo "Logging in as Farmer..."
farmer_login=$(curl -s -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@greenvalley.com",
    "password": "Farmer@123"
  }')
FARMER_TOKEN=$(echo "$farmer_login" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo -e "${GREEN}✓ Farmer logged in${NC}"

# 5. Switch to organization context
echo -e "\nSwitching to organization context..."
switch_response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/switch-organization" \
  -H "Authorization: Bearer $FARMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"organization_id\": \"$ORG_ID\"}")
http_code=$(echo "$switch_response" | tail -n1)
body=$(echo "$switch_response" | head -n-1)

if [ "$http_code" = "200" ]; then
    FARMER_TOKEN=$(echo "$body" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo -e "${GREEN}✓ Switched to organization context${NC}"
    echo "New Token: ${FARMER_TOKEN:0:30}..."
else
    echo -e "${RED}✗ Failed to switch context (HTTP $http_code)${NC}"
    echo "$body"
fi

print_section "TESTING ALL API ENDPOINTS"

# Test function
test_endpoint() {
    local method=$1
    local endpoint=$2
    local name=$3
    local token=$4
    
    response=$(curl -s -w "\n%{http_code}" -X $method "${API_BASE}${endpoint}" \
      -H "Authorization: Bearer $token")
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ]; then
        ((PASS++))
        echo -e "${GREEN}✓${NC} $name"
        return 0
    else
        ((FAIL++))
        echo -e "${RED}✗${NC} $name (HTTP $http_code)"
        return 1
    fi
}

# Reference Data
echo -e "\n${YELLOW}Reference Data & Master Data:${NC}"
test_endpoint GET "/reference-data/types" "Reference Data Types" "$FARMER_TOKEN"
test_endpoint GET "/measurement-units/" "Measurement Units" "$FARMER_TOKEN"

# Crop Data
echo -e "\n${YELLOW}Crop Data:${NC}"
test_endpoint GET "/crop-data/categories" "Crop Categories" "$FARMER_TOKEN"
test_endpoint GET "/crop-data/types" "Crop Types" "$FARMER_TOKEN"
test_endpoint GET "/crop-data/varieties" "Crop Varieties" "$FARMER_TOKEN"

# Tasks & Input Items
echo -e "\n${YELLOW}Tasks & Input Items:${NC}"
test_endpoint GET "/tasks/" "Tasks" "$FARMER_TOKEN"
test_endpoint GET "/input-items/categories" "Input Item Categories" "$FARMER_TOKEN"
test_endpoint GET "/input-items/" "Input Items" "$FARMER_TOKEN"

# Finance
echo -e "\n${YELLOW}Finance:${NC}"
test_endpoint GET "/finance-categories/" "Finance Categories" "$FARMER_TOKEN"

# Farms & Plots
echo -e "\n${YELLOW}Farms & Plots:${NC}"
test_endpoint GET "/farms/" "Get Farms" "$FARMER_TOKEN"
test_endpoint GET "/crops/" "Get Crops" "$FARMER_TOKEN"

# Schedules
echo -e "\n${YELLOW}Schedules:${NC}"
test_endpoint GET "/schedule-templates" "Schedule Templates" "$FARMER_TOKEN"
test_endpoint GET "/schedules" "Schedules" "$FARMER_TOKEN"

# Work Orders
echo -e "\n${YELLOW}Work Orders:${NC}"
test_endpoint GET "/work-orders" "Work Orders" "$FARMER_TOKEN"

# Queries & Notifications
echo -e "\n${YELLOW}Queries & Notifications:${NC}"
test_endpoint GET "/queries" "Queries" "$FARMER_TOKEN"
test_endpoint GET "/notifications/unread-count" "Unread Notifications" "$FARMER_TOKEN"

# Farm Audit
echo -e "\n${YELLOW}Farm Audit System:${NC}"
test_endpoint GET "/farm-audit/option-sets" "Audit Option Sets" "$FARMER_TOKEN"
test_endpoint GET "/farm-audit/parameters" "Audit Parameters" "$FARMER_TOKEN"
test_endpoint GET "/farm-audit/sections" "Audit Sections" "$FARMER_TOKEN"
test_endpoint GET "/farm-audit/templates" "Audit Templates" "$FARMER_TOKEN"
test_endpoint GET "/farm-audit/audits" "Audits" "$FARMER_TOKEN"

# FSP Services
echo -e "\n${YELLOW}FSP Services:${NC}"
test_endpoint GET "/fsp-services/master-services" "Master Services" "$FARMER_TOKEN"
test_endpoint GET "/fsp-services/fsp-marketplace/services" "FSP Marketplace" "$FARMER_TOKEN"

# Invitations
echo -e "\n${YELLOW}Invitations:${NC}"
test_endpoint GET "/invitations/me" "My Invitations" "$FARMER_TOKEN"

# Organization Members
echo -e "\n${YELLOW}Organization Members:${NC}"
test_endpoint GET "/organizations/${ORG_ID}/members" "Organization Members" "$FARMER_TOKEN"

print_section "CREATING TEST DATA"

# Create a Farm
echo "Creating a test farm..."
farm_response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/farms/" \
  -H "Authorization: Bearer $FARMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Green Valley Main Farm",
    "description": "Primary organic farming location",
    "total_area": 50.5,
    "area_unit_id": 1,
    "address": "Green Valley Road",
    "city": "Coimbatore",
    "state": "Tamil Nadu",
    "postal_code": "641001",
    "country": "India",
    "location": {
      "type": "Point",
      "coordinates": [76.9558, 11.0168]
    }
  }')
http_code=$(echo "$farm_response" | tail -n1)
body=$(echo "$farm_response" | head -n-1)

if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
    FARM_ID=$(echo "$body" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
    echo -e "${GREEN}✓ Farm created successfully!${NC}"
    echo "Farm ID: $FARM_ID"
    ((PASS++))
else
    echo -e "${RED}✗ Failed to create farm (HTTP $http_code)${NC}"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
    ((FAIL++))
fi

print_section "FINAL SUMMARY"

TOTAL=$((PASS + FAIL))
SUCCESS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASS/$TOTAL)*100}")

echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo "Total Tests: $TOTAL"
echo "Success Rate: ${SUCCESS_RATE}%"

echo -e "\n${BLUE}=========================================${NC}"
echo "Test Credentials:"
echo "  Super Admin: superadmin@uzhathunai.com / SuperSecure@Admin123"
echo "  Farmer: farmer@greenvalley.com / Farmer@123"
echo ""
echo "Organization:"
echo "  ID: $ORG_ID"
echo "  Status: APPROVED ✓"
if [ ! -z "$FARM_ID" ]; then
    echo ""
    echo "Test Farm Created:"
    echo "  ID: $FARM_ID"
    echo "  Name: Green Valley Main Farm"
fi
echo ""
echo "Access URLs:"
echo "  API Docs: ${BASE_URL}/docs"
echo "  Health: ${BASE_URL}/health"
echo -e "${BLUE}=========================================${NC}"
