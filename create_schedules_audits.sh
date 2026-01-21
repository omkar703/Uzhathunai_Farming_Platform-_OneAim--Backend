#!/bin/bash

# Create Schedules and Audits for Farmer's Farm
# This script creates test data as FSP for the farmer to view

set -e

BASE_URL="http://localhost:8000"
API_BASE="${BASE_URL}/api/v1"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "\n${BLUE}========== $1 ==========${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ SUCCESS${NC}: $1"
}

print_error() {
    echo -e "${RED}✗ ERROR${NC}: $1"
}

# Known IDs from work order
WORK_ORDER_ID="4cd672bd-dc23-48fb-bcb7-216f3b82679d"
FARMING_ORG_ID="fd3f4e7a-b1a0-41f3-8ed3-aca6b6b87843"
FSP_ORG_ID="3353a42a-15e9-4d01-816e-bc4d0b1f8f48"

print_step "CREATING SCHEDULES AND AUDITS FOR FARMER"

# Step 1: Login as FSP
print_step "1. LOGGING IN AS FSP"

login_response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testfsp@aggroconnect.com",
    "password": "TestFSP@123"
  }')

http_code=$(echo "$login_response" | tail -n1)
body=$(echo "$login_response" | head -n-1)

if [ "$http_code" != "200" ]; then
    print_error "FSP login failed (HTTP $http_code)"
    exit 1
fi

FSP_TOKEN=$(echo "$body" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
print_success "FSP logged in"

# Step 2: Get farmer's farms
print_step "2. GETTING FARMER'S FARMS"

# First, we need to login as farmer to get farms
# Try to find farmer credentials from the work order
echo "Attempting to get farmer farms..."

# We'll use the FSP token to get work order details and extract farm info
wo_response=$(curl -s -X GET "${API_BASE}/work-orders/${WORK_ORDER_ID}" \
  -H "Authorization: Bearer $FSP_TOKEN")

echo "Work order details retrieved"

# Step 3: Create Schedule (using FSP org)
print_step "3. CREATING SCHEDULE FOR WORK ORDER"

schedule_response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/schedules" \
  -H "Authorization: Bearer $FSP_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"organization_id\": \"$FSP_ORG_ID\",
    \"title\": \"Pest Control Service - WO-2026-0001\",
    \"description\": \"Execute pest control service for farmer's fields\",
    \"start_date\": \"2026-01-22\",
    \"end_date\": \"2026-01-25\",
    \"is_template\": false,
    \"work_order_id\": \"$WORK_ORDER_ID\"
  }")

http_code=$(echo "$schedule_response" | tail -n1)
body=$(echo "$schedule_response" | head -n-1)

if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
    SCHEDULE_ID=$(echo "$body" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
    print_success "Schedule created!"
    echo "Schedule ID: $SCHEDULE_ID"
    echo "Title: Pest Control Service - WO-2026-0001"
    echo "Dates: Jan 22-25, 2026"
else
    echo -e "${YELLOW}Schedule creation response (HTTP $http_code):${NC}"
    echo "$body" | head -20
fi

# Step 4: Create another schedule
print_step "4. CREATING FOLLOW-UP SCHEDULE"

schedule2_response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/schedules" \
  -H "Authorization: Bearer $FSP_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"organization_id\": \"$FSP_ORG_ID\",
    \"title\": \"Follow-up Inspection - WO-2026-0001\",
    \"description\": \"Post-treatment inspection and effectiveness check\",
    \"start_date\": \"2026-02-05\",
    \"end_date\": \"2026-02-05\",
    \"is_template\": false,
    \"work_order_id\": \"$WORK_ORDER_ID\"
  }")

http_code=$(echo "$schedule2_response" | tail -n1)
body=$(echo "$schedule2_response" | head -n-1)

if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
    SCHEDULE2_ID=$(echo "$body" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
    print_success "Follow-up schedule created!"
    echo "Schedule ID: $SCHEDULE2_ID"
else
    echo -e "${YELLOW}Follow-up schedule response (HTTP $http_code):${NC}"
    echo "$body" | head -20
fi

# Step 5: Try to get audit templates
print_step "5. GETTING AUDIT TEMPLATES"

templates_response=$(curl -s -X GET "${API_BASE}/farm-audit/templates" \
  -H "Authorization: Bearer $FSP_TOKEN")

echo "Audit templates response:"
echo "$templates_response" | python3 -m json.tool 2>/dev/null | head -30 || echo "$templates_response" | head -30

# Extract first template ID if available
TEMPLATE_ID=$(echo "$templates_response" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ ! -z "$TEMPLATE_ID" ]; then
    echo "Found template ID: $TEMPLATE_ID"
fi

# Step 6: Get farmer's farms (need to check scope)
print_step "6. CHECKING WORK ORDER SCOPE"

scope_response=$(curl -s -X GET "${API_BASE}/work-orders/${WORK_ORDER_ID}/scope" \
  -H "Authorization: Bearer $FSP_TOKEN")

echo "Work order scope:"
echo "$scope_response" | python3 -m json.tool 2>/dev/null || echo "$scope_response"

# Step 7: List all schedules
print_step "7. LISTING ALL SCHEDULES"

all_schedules=$(curl -s -X GET "${API_BASE}/schedules?work_order_id=${WORK_ORDER_ID}" \
  -H "Authorization: Bearer $FSP_TOKEN")

echo "Schedules for work order:"
echo "$all_schedules" | python3 -m json.tool 2>/dev/null | head -50 || echo "$all_schedules" | head -50

print_step "SUMMARY"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Test Data Creation Attempted${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Work Order: $WORK_ORDER_ID"
echo "FSP Organization: $FSP_ORG_ID"
echo "Farming Organization: $FARMING_ORG_ID"
echo ""
echo "Created:"
echo "  - Schedule 1: Pest Control Service (Jan 22-25)"
echo "  - Schedule 2: Follow-up Inspection (Feb 5)"
echo ""
echo "Note: Audit creation requires farm access."
echo "Farmer needs to grant FSP access to farms via scope."
echo ""
echo "Farmer can view schedules with:"
echo "  GET /api/v1/schedules?work_order_id=$WORK_ORDER_ID"
echo ""
echo -e "${GREEN}========================================${NC}"
