#!/bin/bash

# EXHAUSTIVE API ENDPOINT TESTING - ALL 200+ ENDPOINTS
# Tests every single endpoint listed in the OpenAPI spec

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
CRASH=0

# Results file
RESULTS_FILE="exhaustive_test_results.txt"
CRASH_LOG="crash_log.txt"
> "$RESULTS_FILE"
> "$CRASH_LOG"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   EXHAUSTIVE API TESTING - ALL 200+ ENDPOINTS             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

# Check backend health before starting
echo -e "\n${YELLOW}Checking backend health before testing...${NC}"
if ! curl -s "${BASE_URL}/health" | grep -q "healthy"; then
    echo -e "${RED}✗ Backend is NOT healthy! Aborting tests.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Backend is healthy${NC}"

# Login and get token
echo -e "\n${YELLOW}Logging in to get authentication token...${NC}"
login_response=$(curl -s -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"farmer@greenvalley.com","password":"Farmer@123"}')
TOKEN=$(echo "$login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ Failed to get token!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Token obtained${NC}"

# Get org ID
orgs=$(curl -s -X GET "${API_BASE}/organizations" -H "Authorization: Bearer $TOKEN")
ORG_ID=$(echo "$orgs" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
echo -e "${GREEN}✓ Organization ID: $ORG_ID${NC}"

# Test function
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local expected_codes=$4  # comma-separated like "200,403,404"
    
    ((TOTAL++))
    
    # Check if backend is still running
    if ! curl -s -m 2 "${BASE_URL}/health" > /dev/null 2>&1; then
        ((CRASH++))
        echo -e "${RED}💥 CRASH DETECTED${NC} after testing: $description"
        echo "CRASH | $method $endpoint | Backend stopped responding" >> "$CRASH_LOG"
        return 1
    fi
    
    response=$(curl -s -w "\n%{http_code}" -m 10 -X $method "${API_BASE}${endpoint}" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    
    # Check if we got a valid HTTP code
    if ! [[ "$http_code" =~ ^[0-9]{3}$ ]]; then
        ((FAIL++))
        echo -e "${RED}✗${NC} $description - Connection error"
        echo "FAIL | $method $endpoint | HTTP $http_code | Connection error" >> "$RESULTS_FILE"
        return 1
    fi
    
    # Check if code matches expected
    if echo ",$expected_codes," | grep -q ",$http_code,"; then
        ((PASS++))
        echo -e "${GREEN}✓${NC} $description (HTTP $http_code)"
        echo "PASS | $method $endpoint | HTTP $http_code" >> "$RESULTS_FILE"
        return 0
    else
        ((FAIL++))
        echo -e "${RED}✗${NC} $description (HTTP $http_code)"
        echo "FAIL | $method $endpoint | HTTP $http_code" >> "$RESULTS_FILE"
        return 1
    fi
}

# ============================================================================
# SECTION 1: HEALTH & ROOT (2 endpoints)
# ============================================================================
echo -e "\n${BLUE}[1/33] HEALTH & ROOT${NC}"
curl -s "${BASE_URL}/health" | grep -q "healthy" && ((PASS++)) && echo -e "${GREEN}✓${NC} GET /health" || ((FAIL++)) && echo -e "${RED}✗${NC} GET /health"
((TOTAL++))
curl -s "${BASE_URL}/" > /dev/null && ((PASS++)) && echo -e "${GREEN}✓${NC} GET /" || ((FAIL++)) && echo -e "${RED}✗${NC} GET /"
((TOTAL++))

# ============================================================================
# SECTION 2: AUTHENTICATION (8 endpoints)
# ============================================================================
echo -e "\n${BLUE}[2/33] AUTHENTICATION${NC}"
test_endpoint POST "/auth/register" "Register new user" "200,201,409"
test_endpoint POST "/auth/login" "Login user" "200"
test_endpoint POST "/auth/refresh" "Refresh token" "200,401"
test_endpoint POST "/auth/logout" "Logout user" "200,403"
test_endpoint GET "/auth/me" "Get current user" "200,403"
test_endpoint PUT "/auth/me" "Update user profile" "200,403"
test_endpoint POST "/auth/change-password" "Change password" "200,403"
test_endpoint POST "/auth/switch-organization" "Switch organization" "200,403"

# ============================================================================
# SECTION 3: ADMIN (2 endpoints)
# ============================================================================
echo -e "\n${BLUE}[3/33] ADMIN${NC}"
test_endpoint GET "/admin/organizations" "List all organizations" "200,403"
test_endpoint POST "/admin/organizations/${ORG_ID}/approve" "Approve organization" "200,403,404"

# ============================================================================
# SECTION 4: ORGANIZATIONS (4 endpoints)
# ============================================================================
echo -e "\n${BLUE}[4/33] ORGANIZATIONS${NC}"
test_endpoint POST "/organizations" "Create organization" "200,201,409"
test_endpoint GET "/organizations" "Get user organizations" "200"
test_endpoint GET "/organizations/${ORG_ID}" "Get organization details" "200,403,404"
test_endpoint PUT "/organizations/${ORG_ID}" "Update organization" "200,403,404"

# ============================================================================
# SECTION 5: ROLES (2 endpoints)
# ============================================================================
echo -e "\n${BLUE}[5/33] ROLES${NC}"
test_endpoint GET "/roles" "Get roles" "200"
test_endpoint GET "/roles/dummy-role-id" "Get role details" "200,404"

# ============================================================================
# SECTION 6: MEMBERS (4 endpoints)
# ============================================================================
echo -e "\n${BLUE}[6/33] MEMBERS${NC}"
test_endpoint POST "/organizations/${ORG_ID}/members/invite" "Invite member" "200,201,403,404"
test_endpoint GET "/organizations/${ORG_ID}/members" "Get members" "200,403,404"
test_endpoint PUT "/organizations/${ORG_ID}/members/dummy-user-id/roles" "Update member roles" "200,403,404"
test_endpoint DELETE "/organizations/${ORG_ID}/members/dummy-user-id" "Remove member" "200,204,403,404"

# ============================================================================
# SECTION 7: INVITATIONS (3 endpoints)
# ============================================================================
echo -e "\n${BLUE}[7/33] INVITATIONS${NC}"
test_endpoint GET "/invitations/me" "Get my invitations" "200,403"
test_endpoint POST "/invitations/dummy-invite-id/accept" "Accept invitation" "200,403,404"
test_endpoint POST "/invitations/dummy-invite-id/reject" "Reject invitation" "200,403,404"

# ============================================================================
# SECTION 8: FSP SERVICES (9 endpoints)
# ============================================================================
echo -e "\n${BLUE}[8/33] FSP SERVICES${NC}"
test_endpoint GET "/fsp-services/master-services" "Get master services" "200"
test_endpoint GET "/fsp-services/organizations/${ORG_ID}/services" "Get org services" "200,403"
test_endpoint POST "/fsp-services/organizations/${ORG_ID}/services" "Create service listing" "200,201,403"
test_endpoint PUT "/fsp-services/organizations/${ORG_ID}/services/dummy-service-id" "Update service" "200,403,404"
test_endpoint DELETE "/fsp-services/organizations/${ORG_ID}/services/dummy-service-id" "Delete service" "200,204,403,404"
test_endpoint GET "/fsp-services/fsp-marketplace/services" "Browse marketplace" "200"
test_endpoint POST "/fsp-services/fsp-organizations/${ORG_ID}/documents" "Upload approval doc" "200,201,403"
test_endpoint GET "/fsp-services/fsp-organizations/${ORG_ID}/documents" "Get approval docs" "200,403"
test_endpoint GET "/fsp-services/admin/fsp-approvals" "Get FSP approvals" "200,403"
test_endpoint POST "/fsp-services/admin/fsp-approvals/${ORG_ID}/approve" "Approve FSP" "200,403,404"

# ============================================================================
# SECTION 9: WORK ORDERS (10 endpoints)
# ============================================================================
echo -e "\n${BLUE}[9/33] WORK ORDERS${NC}"
test_endpoint POST "/work-orders" "Create work order" "200,201,403"
test_endpoint GET "/work-orders" "Get work orders" "200,403"
test_endpoint GET "/work-orders/dummy-wo-id" "Get work order details" "200,403,404"
test_endpoint PUT "/work-orders/dummy-wo-id" "Update work order" "200,403,404"
test_endpoint POST "/work-orders/dummy-wo-id/accept" "Accept work order" "200,403,404"
test_endpoint POST "/work-orders/dummy-wo-id/complete" "Complete work order" "200,403,404"
test_endpoint POST "/work-orders/dummy-wo-id/cancel" "Cancel work order" "200,403,404"
test_endpoint GET "/work-orders/dummy-wo-id/scope" "Get work order scope" "200,403,404"
test_endpoint POST "/work-orders/dummy-wo-id/scope" "Add scope items" "200,201,403,404"
test_endpoint PUT "/work-orders/dummy-wo-id/scope/dummy-scope-id" "Update scope permissions" "200,403,404"

# ============================================================================
# SECTION 10: SCHEDULE TEMPLATES (9 endpoints)
# ============================================================================
echo -e "\n${BLUE}[10/33] SCHEDULE TEMPLATES${NC}"
test_endpoint GET "/schedule-templates" "Get templates" "200,403"
test_endpoint POST "/schedule-templates" "Create template" "200,201,403"
test_endpoint GET "/schedule-templates/dummy-template-id" "Get template" "200,403,404"
test_endpoint PUT "/schedule-templates/dummy-template-id" "Update template" "200,403,404"
test_endpoint POST "/schedule-templates/dummy-template-id/copy" "Copy template" "200,201,403,404"
test_endpoint GET "/schedule-templates/dummy-template-id/tasks" "Get template tasks" "200,403,404"
test_endpoint POST "/schedule-templates/dummy-template-id/tasks" "Create template task" "200,201,403,404"
test_endpoint PUT "/schedule-templates/tasks/dummy-task-id" "Update template task" "200,403,404"
test_endpoint DELETE "/schedule-templates/tasks/dummy-task-id" "Delete template task" "200,204,403,404"

# ============================================================================
# SECTION 11: SCHEDULES (9 endpoints)
# ============================================================================
echo -e "\n${BLUE}[11/33] SCHEDULES${NC}"
test_endpoint POST "/schedules/from-template" "Create from template" "200,201,403"
test_endpoint POST "/schedules/from-scratch" "Create from scratch" "200,201,403"
test_endpoint POST "/schedules/dummy-schedule-id/copy" "Copy schedule" "200,201,403,404"
test_endpoint GET "/schedules" "Get schedules" "200,403"
test_endpoint GET "/schedules/dummy-schedule-id" "Get schedule" "200,403,404"
test_endpoint POST "/schedules/dummy-schedule-id/tasks" "Create schedule task" "200,201,403,404"
test_endpoint GET "/schedules/dummy-schedule-id/tasks" "Get schedule tasks" "200,403,404"
test_endpoint PUT "/schedules/tasks/dummy-task-id" "Update schedule task" "200,403,404"
test_endpoint PUT "/schedules/tasks/dummy-task-id/status" "Update task status" "200,403,404"

# ============================================================================
# SECTION 12: TASK ACTUALS (4 endpoints)
# ============================================================================
echo -e "\n${BLUE}[12/33] TASK ACTUALS${NC}"
test_endpoint POST "/task-actuals/planned" "Record planned actual" "200,201,403"
test_endpoint POST "/task-actuals/adhoc" "Record adhoc actual" "200,201,403"
test_endpoint POST "/task-actuals/dummy-actual-id/photos" "Upload task photo" "200,201,403,404"
test_endpoint GET "/task-actuals" "Get task actuals" "200,403"

# ============================================================================
# SECTION 13: SCHEDULE CHANGE LOG (2 endpoints)
# ============================================================================
echo -e "\n${BLUE}[13/33] SCHEDULE CHANGE LOG${NC}"
test_endpoint GET "/schedules/dummy-schedule-id/change-log" "Get change log" "200,403,404"
test_endpoint POST "/schedules/change-log/apply" "Apply changes" "200,403"

# ============================================================================
# SECTION 14: QUERIES (9 endpoints)
# ============================================================================
echo -e "\n${BLUE}[14/33] QUERIES${NC}"
test_endpoint POST "/queries" "Create query" "200,201,403"
test_endpoint GET "/queries" "Get queries" "200,403"
test_endpoint GET "/queries/dummy-query-id" "Get query" "200,403,404"
test_endpoint PUT "/queries/dummy-query-id/status" "Update query status" "200,403,404"
test_endpoint POST "/queries/dummy-query-id/responses" "Create response" "200,201,403,404"
test_endpoint GET "/queries/dummy-query-id/responses" "Get responses" "200,403,404"
test_endpoint POST "/queries/dummy-query-id/propose-changes" "Propose changes" "200,201,403,404"
test_endpoint POST "/queries/dummy-query-id/photos" "Upload query photo" "200,201,403,404"
test_endpoint POST "/queries/responses/dummy-response-id/photos" "Upload response photo" "200,201,403,404"

# ============================================================================
# SECTION 15: NOTIFICATIONS (1 endpoint)
# ============================================================================
echo -e "\n${BLUE}[15/33] NOTIFICATIONS${NC}"
test_endpoint GET "/notifications/unread-count" "Get unread count" "200,403"

# ============================================================================
# SECTION 16: MEASUREMENT UNITS (3 endpoints)
# ============================================================================
echo -e "\n${BLUE}[16/33] MEASUREMENT UNITS${NC}"
test_endpoint GET "/measurement-units/" "Get measurement units" "200,403"
test_endpoint GET "/measurement-units/dummy-unit-id" "Get measurement unit" "200,403,404"
test_endpoint POST "/measurement-units/convert" "Convert quantity" "200,403"

# ============================================================================
# SECTION 17: CROP DATA (4 endpoints)
# ============================================================================
echo -e "\n${BLUE}[17/33] CROP DATA${NC}"
test_endpoint GET "/crop-data/categories" "Get crop categories" "200,403"
test_endpoint GET "/crop-data/types" "Get crop types" "200,403"
test_endpoint GET "/crop-data/varieties" "Get crop varieties" "200,403"
test_endpoint GET "/crop-data/varieties/dummy-variety-id" "Get crop variety" "200,403,404"

# ============================================================================
# SECTION 18: INPUT ITEMS (8 endpoints)
# ============================================================================
echo -e "\n${BLUE}[18/33] INPUT ITEMS${NC}"
test_endpoint GET "/input-items/categories" "Get input categories" "200,403"
test_endpoint POST "/input-items/categories" "Create input category" "200,201,403"
test_endpoint PUT "/input-items/categories/dummy-cat-id" "Update input category" "200,403,404"
test_endpoint DELETE "/input-items/categories/dummy-cat-id" "Delete input category" "200,204,403,404"
test_endpoint GET "/input-items/" "Get input items" "200,403"
test_endpoint POST "/input-items/" "Create input item" "200,201,403"
test_endpoint PUT "/input-items/dummy-item-id" "Update input item" "200,403,404"
test_endpoint DELETE "/input-items/dummy-item-id" "Delete input item" "200,204,403,404"

# ============================================================================
# SECTION 19: FINANCE CATEGORIES (4 endpoints)
# ============================================================================
echo -e "\n${BLUE}[19/33] FINANCE CATEGORIES${NC}"
test_endpoint GET "/finance-categories/" "Get finance categories" "200,403"
test_endpoint POST "/finance-categories/" "Create finance category" "200,201,403"
test_endpoint PUT "/finance-categories/dummy-cat-id" "Update finance category" "200,403,404"
test_endpoint DELETE "/finance-categories/dummy-cat-id" "Delete finance category" "200,204,403,404"

# ============================================================================
# SECTION 20: TASKS (2 endpoints)
# ============================================================================
echo -e "\n${BLUE}[20/33] TASKS${NC}"
test_endpoint GET "/tasks/" "Get tasks" "200,403"
test_endpoint GET "/tasks/dummy-task-id" "Get task" "200,403,404"

# ============================================================================
# SECTION 21: REFERENCE DATA (2 endpoints)
# ============================================================================
echo -e "\n${BLUE}[21/33] REFERENCE DATA${NC}"
test_endpoint GET "/reference-data/types" "Get reference types" "200,403"
test_endpoint GET "/reference-data/dummy-type-code" "Get reference data by type" "200,403,404"

# ============================================================================
# SECTION 22: FARMS (11 endpoints)
# ============================================================================
echo -e "\n${BLUE}[22/33] FARMS${NC}"
test_endpoint POST "/farms/" "Create farm" "200,201,403"
test_endpoint GET "/farms/" "Get farms" "200,403"
test_endpoint GET "/farms/dummy-farm-id" "Get farm" "200,403,404"
test_endpoint PUT "/farms/dummy-farm-id" "Update farm" "200,403,404"
test_endpoint DELETE "/farms/dummy-farm-id" "Delete farm" "200,204,403,404"
test_endpoint POST "/farms/dummy-farm-id/supervisors" "Assign supervisor" "200,201,403,404"
test_endpoint DELETE "/farms/dummy-farm-id/supervisors/dummy-sup-id" "Remove supervisor" "200,204,403,404"
test_endpoint POST "/farms/dummy-farm-id/water-sources" "Add water source" "200,201,403,404"
test_endpoint POST "/farms/dummy-farm-id/soil-types" "Add soil type" "200,201,403,404"
test_endpoint POST "/farms/dummy-farm-id/irrigation-modes" "Add irrigation mode" "200,201,403,404"

# ============================================================================
# SECTION 23: PLOTS (9 endpoints)
# ============================================================================
echo -e "\n${BLUE}[23/33] PLOTS${NC}"
test_endpoint POST "/plots/farms/dummy-farm-id/plots" "Create plot" "200,201,403,404"
test_endpoint GET "/plots/farms/dummy-farm-id/plots" "Get plots by farm" "200,403,404"
test_endpoint GET "/plots/dummy-plot-id" "Get plot" "200,403,404"
test_endpoint PUT "/plots/dummy-plot-id" "Update plot" "200,403,404"
test_endpoint DELETE "/plots/dummy-plot-id" "Delete plot" "200,204,403,404"
test_endpoint POST "/plots/dummy-plot-id/water-sources" "Add water source" "200,201,403,404"
test_endpoint POST "/plots/dummy-plot-id/soil-types" "Add soil type" "200,201,403,404"
test_endpoint POST "/plots/dummy-plot-id/irrigation-modes" "Add irrigation mode" "200,201,403,404"

# ============================================================================
# SECTION 24: CROPS (7 endpoints)
# ============================================================================
echo -e "\n${BLUE}[24/33] CROPS${NC}"
test_endpoint POST "/crops/" "Create crop" "200,201,403"
test_endpoint GET "/crops/" "Get crops" "200,403"
test_endpoint GET "/crops/dummy-crop-id" "Get crop" "200,403,404"
test_endpoint PUT "/crops/dummy-crop-id" "Update crop" "200,403,404"
test_endpoint DELETE "/crops/dummy-crop-id" "Delete crop" "200,204,403,404"
test_endpoint PUT "/crops/dummy-crop-id/lifecycle" "Update lifecycle" "200,403,404"
test_endpoint GET "/crops/plots/dummy-plot-id/crop-history" "Get crop history" "200,403,404"

# ============================================================================
# SECTION 25: CROP YIELDS (7 endpoints)
# ============================================================================
echo -e "\n${BLUE}[25/33] CROP YIELDS${NC}"
test_endpoint POST "/crop-yields/crops/dummy-crop-id/yields" "Create yield" "200,201,403,404"
test_endpoint GET "/crop-yields/crops/dummy-crop-id/yields" "Get yields" "200,403,404"
test_endpoint GET "/crop-yields/dummy-yield-id" "Get yield" "200,403,404"
test_endpoint PUT "/crop-yields/dummy-yield-id" "Update yield" "200,403,404"
test_endpoint DELETE "/crop-yields/dummy-yield-id" "Delete yield" "200,204,403,404"
test_endpoint POST "/crop-yields/dummy-yield-id/photos" "Associate photo" "200,201,403,404"
test_endpoint GET "/crop-yields/crops/dummy-crop-id/yield-comparison" "Yield comparison" "200,403,404"

# ============================================================================
# SECTION 26: CROP PHOTOS (4 endpoints)
# ============================================================================
echo -e "\n${BLUE}[26/33] CROP PHOTOS${NC}"
test_endpoint POST "/crop-photos/crops/dummy-crop-id/photos" "Upload crop photo" "200,201,403,404"
test_endpoint GET "/crop-photos/crops/dummy-crop-id/photos" "Get crop photos" "200,403,404"
test_endpoint GET "/crop-photos/dummy-photo-id" "Get crop photo" "200,403,404"
test_endpoint DELETE "/crop-photos/dummy-photo-id" "Delete crop photo" "200,204,403,404"

# ============================================================================
# SECTION 27: FARM AUDIT - OPTION SETS (8 endpoints)
# ============================================================================
echo -e "\n${BLUE}[27/33] FARM AUDIT - OPTION SETS${NC}"
test_endpoint GET "/farm-audit/option-sets" "Get option sets" "200,403"
test_endpoint POST "/farm-audit/option-sets" "Create option set" "200,201,403"
test_endpoint GET "/farm-audit/option-sets/dummy-set-id" "Get option set" "200,403,404"
test_endpoint PUT "/farm-audit/option-sets/dummy-set-id" "Update option set" "200,403,404"
test_endpoint DELETE "/farm-audit/option-sets/dummy-set-id" "Delete option set" "200,204,403,404"
test_endpoint POST "/farm-audit/option-sets/dummy-set-id/options" "Add option" "200,201,403,404"
test_endpoint PUT "/farm-audit/option-sets/dummy-set-id/options/dummy-opt-id" "Update option" "200,403,404"
test_endpoint DELETE "/farm-audit/option-sets/dummy-set-id/options/dummy-opt-id" "Delete option" "200,204,403,404"

# ============================================================================
# SECTION 28: FARM AUDIT - PARAMETERS (6 endpoints)
# ============================================================================
echo -e "\n${BLUE}[28/33] FARM AUDIT - PARAMETERS${NC}"
test_endpoint GET "/farm-audit/parameters" "Get parameters" "200,403"
test_endpoint POST "/farm-audit/parameters" "Create parameter" "200,201,403"
test_endpoint GET "/farm-audit/parameters/dummy-param-id" "Get parameter" "200,403,404"
test_endpoint PUT "/farm-audit/parameters/dummy-param-id" "Update parameter" "200,403,404"
test_endpoint DELETE "/farm-audit/parameters/dummy-param-id" "Delete parameter" "200,204,403,404"
test_endpoint POST "/farm-audit/parameters/dummy-param-id/copy" "Copy parameter" "200,201,403,404"

# ============================================================================
# SECTION 29: FARM AUDIT - SECTIONS (5 endpoints)
# ============================================================================
echo -e "\n${BLUE}[29/33] FARM AUDIT - SECTIONS${NC}"
test_endpoint GET "/farm-audit/sections" "Get sections" "200,403"
test_endpoint POST "/farm-audit/sections" "Create section" "200,201,403"
test_endpoint GET "/farm-audit/sections/dummy-section-id" "Get section" "200,403,404"
test_endpoint PUT "/farm-audit/sections/dummy-section-id" "Update section" "200,403,404"
test_endpoint DELETE "/farm-audit/sections/dummy-section-id" "Delete section" "200,204,403,404"

# ============================================================================
# SECTION 30: FARM AUDIT - TEMPLATES (10 endpoints)
# ============================================================================
echo -e "\n${BLUE}[30/33] FARM AUDIT - TEMPLATES${NC}"
test_endpoint GET "/farm-audit/templates" "Get templates" "200,403"
test_endpoint POST "/farm-audit/templates" "Create template" "200,201,403"
test_endpoint GET "/farm-audit/templates/dummy-template-id" "Get template" "200,403,404"
test_endpoint PUT "/farm-audit/templates/dummy-template-id" "Update template" "200,403,404"
test_endpoint DELETE "/farm-audit/templates/dummy-template-id" "Delete template" "200,204,403,404"
test_endpoint POST "/farm-audit/templates/dummy-template-id/sections" "Add section" "200,201,403,404"
test_endpoint DELETE "/farm-audit/templates/dummy-template-id/sections/dummy-sec-id" "Remove section" "200,204,403,404"
test_endpoint POST "/farm-audit/templates/dummy-template-id/sections/dummy-sec-id/parameters" "Add parameter" "200,201,403,404"
test_endpoint DELETE "/farm-audit/templates/dummy-template-id/sections/dummy-sec-id/parameters/dummy-param-id" "Remove parameter" "200,204,403,404"
test_endpoint POST "/farm-audit/templates/dummy-template-id/copy" "Copy template" "200,201,403,404"

# ============================================================================
# SECTION 31: FARM AUDIT - AUDITS (29 endpoints)
# ============================================================================
echo -e "\n${BLUE}[31/33] FARM AUDIT - AUDITS${NC}"
test_endpoint POST "/farm-audit/audits" "Create audit" "200,201,403"
test_endpoint GET "/farm-audit/audits" "Get audits" "200,403"
test_endpoint GET "/farm-audit/audits/dummy-audit-id" "Get audit" "200,403,404"
test_endpoint GET "/farm-audit/audits/dummy-audit-id/structure" "Get structure" "200,403,404"
test_endpoint POST "/farm-audit/audits/dummy-audit-id/responses" "Submit response" "200,201,403,404"
test_endpoint GET "/farm-audit/audits/dummy-audit-id/responses" "Get responses" "200,403,404"
test_endpoint PUT "/farm-audit/audits/dummy-audit-id/responses/dummy-resp-id" "Update response" "200,403,404"
test_endpoint POST "/farm-audit/audits/dummy-audit-id/responses/dummy-resp-id/photos" "Upload photo" "200,201,403,404"
test_endpoint GET "/farm-audit/audits/dummy-audit-id/responses/dummy-resp-id/photos" "Get photos" "200,403,404"
test_endpoint DELETE "/farm-audit/audits/dummy-audit-id/responses/dummy-resp-id/photos/dummy-photo-id" "Delete photo" "200,204,403,404"
test_endpoint POST "/farm-audit/audits/dummy-audit-id/capture" "Capture snapshot" "200,201,403,404"
test_endpoint POST "/farm-audit/audits/dummy-audit-id/transition" "Transition status" "200,403,404"
test_endpoint GET "/farm-audit/audits/dummy-audit-id/validation" "Validate submission" "200,403,404"
test_endpoint POST "/farm-audit/audits/dummy-audit-id/reviews" "Create review" "200,201,403,404"
test_endpoint PUT "/farm-audit/audits/dummy-audit-id/reviews/dummy-review-id" "Update review" "200,403,404"
test_endpoint POST "/farm-audit/audits/dummy-audit-id/reviews/dummy-review-id/flag" "Flag response" "200,201,403,404"
test_endpoint POST "/farm-audit/audits/dummy-audit-id/photos/dummy-photo-id/annotate" "Annotate photo" "200,403,404"
test_endpoint POST "/farm-audit/audits/dummy-audit-id/issues" "Create issue" "200,201,403,404"
test_endpoint GET "/farm-audit/audits/dummy-audit-id/issues" "Get issues" "200,403,404"
test_endpoint PUT "/farm-audit/audits/dummy-audit-id/issues/dummy-issue-id" "Update issue" "200,403,404"
test_endpoint DELETE "/farm-audit/audits/dummy-audit-id/issues/dummy-issue-id" "Delete issue" "200,204,403,404"
test_endpoint POST "/farm-audit/audits/dummy-audit-id/recommendations" "Create recommendation" "200,201,403,404"
test_endpoint GET "/farm-audit/audits/dummy-audit-id/recommendations" "Get recommendations" "200,403,404"
test_endpoint PUT "/farm-audit/audits/dummy-audit-id/recommendations/dummy-rec-id" "Update recommendation" "200,403,404"
test_endpoint DELETE "/farm-audit/audits/dummy-audit-id/recommendations/dummy-rec-id" "Delete recommendation" "200,204,403,404"
test_endpoint GET "/farm-audit/recommendations/pending" "Get pending recommendations" "200,403"
test_endpoint POST "/farm-audit/recommendations/dummy-rec-id/approve" "Approve recommendation" "200,403,404"
test_endpoint POST "/farm-audit/recommendations/dummy-rec-id/reject" "Reject recommendation" "200,403,404"
test_endpoint POST "/farm-audit/audits/dummy-audit-id/finalize" "Finalize audit" "200,403,404"
test_endpoint POST "/farm-audit/audits/dummy-audit-id/share" "Share audit" "200,403,404"

# ============================================================================
# SECTION 32: FARM AUDIT - REPORTS (2 endpoints)
# ============================================================================
echo -e "\n${BLUE}[32/33] FARM AUDIT - REPORTS${NC}"
test_endpoint GET "/farm-audit/audits/dummy-audit-id/report" "Get audit report" "200,403,404"
test_endpoint GET "/farm-audit/audits/dummy-audit-id/report/pdf" "Get audit report PDF" "200,403,404"

# ============================================================================
# SECTION 33: BFF DASHBOARD & VIDEO (4 endpoints)
# ============================================================================
echo -e "\n${BLUE}[33/33] BFF DASHBOARD & VIDEO${NC}"
test_endpoint GET "/bff/farming/dashboard" "Get farming dashboard" "200,403"
test_endpoint GET "/bff/fsp/dashboard" "Get FSP dashboard" "200,403"
test_endpoint POST "/video/schedule" "Schedule meeting" "200,201,403"
test_endpoint GET "/video/dummy-session-id/join-url" "Get join URL" "200,403,404"

# ============================================================================
# FINAL BACKEND HEALTH CHECK
# ============================================================================
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           FINAL BACKEND HEALTH CHECK                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

if curl -s "${BASE_URL}/health" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Backend is STILL HEALTHY after all tests!${NC}"
    echo -e "${GREEN}✓ NO CRASHES DETECTED${NC}"
else
    echo -e "${RED}✗ Backend health check FAILED after testing${NC}"
    echo -e "${RED}⚠ BACKEND MAY HAVE CRASHED${NC}"
    ((CRASH++))
fi

# Check logs for errors
echo -e "\n${YELLOW}Checking backend logs for errors...${NC}"
error_count=$(sudo docker compose logs web --tail=200 2>/dev/null | grep -i "error\|exception\|traceback" | grep -v "UserWarning" | wc -l)
if [ "$error_count" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Found $error_count error/exception lines in logs${NC}"
    echo "Recent errors:" >> "$CRASH_LOG"
    sudo docker compose logs web --tail=50 2>/dev/null | grep -i "error\|exception" | head -10 >> "$CRASH_LOG"
else
    echo -e "${GREEN}✓ No errors found in logs${NC}"
fi

# ============================================================================
# FINAL SUMMARY
# ============================================================================
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                 EXHAUSTIVE TEST SUMMARY                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

SUCCESS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASS/$TOTAL)*100}")

echo -e "\n${GREEN}✓ Passed:${NC}  $PASS"
echo -e "${RED}✗ Failed:${NC}  $FAIL"
echo -e "${YELLOW}💥 Crashes:${NC} $CRASH"
echo -e "${BLUE}Total:${NC}    $TOTAL"
echo ""
echo -e "Success Rate: ${GREEN}${SUCCESS_RATE}%${NC}"
echo ""

if [ $CRASH -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ NO BACKEND CRASHES DETECTED - ALL SYSTEMS STABLE!      ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ✗ BACKEND CRASHES DETECTED - CHECK CRASH LOG!            ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
fi

echo ""
echo "Detailed results: $RESULTS_FILE"
if [ -s "$CRASH_LOG" ]; then
    echo "Crash log: $CRASH_LOG"
fi
echo ""
echo -e "${BLUE}API Documentation: ${BASE_URL}/docs${NC}"
echo ""
