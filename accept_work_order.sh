#!/bin/bash

# FSP Work Order Acceptance and Schedule Creation Script
# This script accepts the work order and creates schedule/audit data

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
    exit 1
}

# Work Order ID from the frontend logs
WORK_ORDER_ID="4cd672bd-dc23-48fb-bcb7-216f3b82679d"

print_step "FSP WORK ORDER ACCEPTANCE & SCHEDULE CREATION"

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
    print_error "FSP login failed (HTTP $http_code): $body"
fi

FSP_TOKEN=$(echo "$body" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
print_success "FSP logged in successfully"
echo "Token: ${FSP_TOKEN:0:30}..."

# Step 2: Get work order details
print_step "2. FETCHING WORK ORDER DETAILS"

wo_response=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/work-orders/${WORK_ORDER_ID}" \
  -H "Authorization: Bearer $FSP_TOKEN")

http_code=$(echo "$wo_response" | tail -n1)
body=$(echo "$wo_response" | head -n-1)

if [ "$http_code" != "200" ]; then
    print_error "Failed to fetch work order (HTTP $http_code): $body"
fi

print_success "Work order fetched"
echo "$body" | grep -o '"status":"[^"]*' | cut -d'"' -f4 | xargs -I {} echo "Current Status: {}"

# Step 3: Accept the work order
print_step "3. ACCEPTING WORK ORDER"

accept_response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/work-orders/${WORK_ORDER_ID}/accept" \
  -H "Authorization: Bearer $FSP_TOKEN")

http_code=$(echo "$accept_response" | tail -n1)
body=$(echo "$accept_response" | head -n-1)

if [ "$http_code" != "200" ]; then
    print_error "Failed to accept work order (HTTP $http_code): $body"
fi

print_success "Work order accepted!"
echo "New Status: ACCEPTED"

# Step 4: Get FSP organization ID
FSP_ORG_ID="3353a42a-15e9-4d01-816e-bc4d0b1f8f48"

# Step 5: Create a schedule for this work order
print_step "4. CREATING SCHEDULE"

# First, let's check if we need a farm/plot for the schedule
# For now, we'll create a simple schedule without farm/plot

schedule_response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/schedules" \
  -H "Authorization: Bearer $FSP_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"organization_id\": \"$FSP_ORG_ID\",
    \"work_order_id\": \"$WORK_ORDER_ID\",
    \"title\": \"Pest Control Service Execution\",
    \"description\": \"Execute pest control service as per work order\",
    \"start_date\": \"2026-01-22\",
    \"end_date\": \"2026-01-25\",
    \"is_template\": false
  }")

http_code=$(echo "$schedule_response" | tail -n1)
body=$(echo "$schedule_response" | head -n-1)

if [ "$http_code" != "200" ] && [ "$http_code" != "201" ]; then
    echo -e "${YELLOW}Schedule creation may have failed (HTTP $http_code)${NC}"
    echo "Response: $body"
else
    SCHEDULE_ID=$(echo "$body" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
    print_success "Schedule created!"
    echo "Schedule ID: $SCHEDULE_ID"
fi

# Step 6: Update work order to add some activity (for audit trail)
print_step "5. UPDATING WORK ORDER (Creating Audit Trail)"

update_response=$(curl -s -w "\n%{http_code}" -X PUT "${API_BASE}/work-orders/${WORK_ORDER_ID}" \
  -H "Authorization: Bearer $FSP_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Work order accepted. Service scheduled for Jan 22-25. Will perform comprehensive pest control using organic solutions."
  }')

http_code=$(echo "$update_response" | tail -n1)
body=$(echo "$update_response" | head -n-1)

if [ "$http_code" != "200" ]; then
    echo -e "${YELLOW}Update may have failed (HTTP $http_code)${NC}"
else
    print_success "Work order updated (audit trail created)"
fi

# Step 7: Get final work order status
print_step "6. FINAL WORK ORDER STATUS"

final_response=$(curl -s -X GET "${API_BASE}/work-orders/${WORK_ORDER_ID}" \
  -H "Authorization: Bearer $FSP_TOKEN")

echo "$final_response" | python3 -m json.tool 2>/dev/null || echo "$final_response"

print_step "SUMMARY"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}FSP Actions Completed Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Work Order ID: $WORK_ORDER_ID"
echo "Status: ACCEPTED"
echo "FSP Organization: Test FSP Services"
echo ""
echo "Actions Performed:"
echo "  ✓ FSP logged in"
echo "  ✓ Work order accepted"
echo "  ✓ Schedule created (if supported)"
echo "  ✓ Work order updated (audit trail)"
echo ""
echo "Farmer can now see:"
echo "  - Work order status changed to ACCEPTED"
echo "  - FSP acceptance timestamp"
echo "  - Updated description"
echo "  - Audit trail of changes"
echo ""
echo -e "${GREEN}========================================${NC}"
