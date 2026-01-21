#!/bin/bash

# Comprehensive API Testing Script for Uzhathunai Farming Platform
# Tests all major endpoints with proper data

BASE_URL="http://localhost:8000"
API_BASE="${BASE_URL}/api/v1"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
    fi
}

print_section() {
    echo -e "\n${BLUE}========== $1 ==========${NC}\n"
}

# Initialize counters
PASS_COUNT=0
FAIL_COUNT=0

print_section "UZHATHUNAI FARMING PLATFORM v2.0 - API TESTING"

# 1. Health Check
print_section "1. HEALTH & BASIC ENDPOINTS"
response=$(curl -s -w "\n%{http_code}" "${BASE_URL}/health")
http_code=$(echo "$response" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /health"

# 2. Register Admin User
print_section "2. USER REGISTRATION & AUTHENTICATION"
echo "Registering Admin User..."
admin_reg=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@uzhathunai.com",
    "password": "Admin@123",
    "full_name": "Platform Admin",
    "phone_number": "+919876543210",
    "preferred_language": "en"
  }')
http_code=$(echo "$admin_reg" | tail -n1)
[ "$http_code" = "200" ] || [ "$http_code" = "201" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ] || [ "$http_code" = "201" ]; echo $?) "POST /auth/register (Admin)"

# 3. Register Farmer User
echo "Registering Farmer User..."
farmer_reg=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@greenvalley.com",
    "password": "Farmer@123",
    "full_name": "John Farmer",
    "phone_number": "+919876543211",
    "preferred_language": "en"
  }')
http_code=$(echo "$farmer_reg" | tail -n1)
[ "$http_code" = "200" ] || [ "$http_code" = "201" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ] || [ "$http_code" = "201" ]; echo $?) "POST /auth/register (Farmer)"

# 4. Register FSP User
echo "Registering FSP Provider..."
fsp_reg=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "fsp@agriservices.com",
    "password": "FSP@123",
    "full_name": "Agri Services Provider",
    "phone_number": "+919876543212",
    "preferred_language": "en"
  }')
http_code=$(echo "$fsp_reg" | tail -n1)
[ "$http_code" = "200" ] || [ "$http_code" = "201" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ] || [ "$http_code" = "201" ]; echo $?) "POST /auth/register (FSP)"

# 5. Login Farmer
echo "Logging in as Farmer..."
farmer_login=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@greenvalley.com",
    "password": "Farmer@123"
  }')
http_code=$(echo "$farmer_login" | tail -n1)
body=$(echo "$farmer_login" | head -n-1)
FARMER_TOKEN=$(echo "$body" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "POST /auth/login (Farmer)"
echo "  Token: ${FARMER_TOKEN:0:30}..."

# 6. Get Current User Profile
profile=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/auth/me" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$profile" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /auth/me"

# 7. Create Farming Organization
print_section "3. ORGANIZATION MANAGEMENT"
echo "Creating Farming Organization..."
farm_org=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/organizations" \
  -H "Authorization: Bearer $FARMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Green Valley Organic Farms",
    "organization_type": "FARMING",
    "description": "Premium organic farming organization",
    "address": "123 Farm Road, Green Valley",
    "city": "Coimbatore",
    "state": "Tamil Nadu",
    "postal_code": "641001",
    "country": "India",
    "contact_email": "contact@greenvalley.com",
    "contact_phone": "+919876543211"
  }')
http_code=$(echo "$farm_org" | tail -n1)
body=$(echo "$farm_org" | head -n-1)
FARM_ORG_ID=$(echo "$body" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
[ "$http_code" = "200" ] || [ "$http_code" = "201" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ] || [ "$http_code" = "201" ]; echo $?) "POST /organizations (FARMING)"
echo "  Organization ID: $FARM_ORG_ID"

# 8. Get Organizations
orgs=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/organizations" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$orgs" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /organizations"

# 9. Get Organization Details
if [ ! -z "$FARM_ORG_ID" ]; then
    org_detail=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/organizations/${FARM_ORG_ID}" \
      -H "Authorization: Bearer $FARMER_TOKEN")
    http_code=$(echo "$org_detail" | tail -n1)
    [ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
    print_result $([ "$http_code" = "200" ]; echo $?) "GET /organizations/{org_id}"
fi

# 10. Get Roles
print_section "4. ROLES & PERMISSIONS"
roles=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/roles" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$roles" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /roles"

# 11. Reference Data
print_section "5. REFERENCE DATA & MASTER DATA"
ref_types=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/reference-data/types" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$ref_types" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /reference-data/types"

# 12. Measurement Units
units=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/measurement-units/" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$units" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /measurement-units/"

# 13. Crop Categories
print_section "6. CROP DATA"
crop_cat=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/crop-data/categories" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$crop_cat" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /crop-data/categories"

# 14. Crop Types
crop_types=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/crop-data/types" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$crop_types" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /crop-data/types"

# 15. Crop Varieties
varieties=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/crop-data/varieties" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$varieties" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /crop-data/varieties"

# 16. Tasks
print_section "7. TASKS & INPUT ITEMS"
tasks=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/tasks/" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$tasks" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /tasks/"

# 17. Input Item Categories
input_cat=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/input-items/categories" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$input_cat" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /input-items/categories"

# 18. Input Items
input_items=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/input-items/" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$input_items" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /input-items/"

# 19. Finance Categories
print_section "8. FINANCE"
finance_cat=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/finance-categories/" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$finance_cat" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /finance-categories/"

# 20. FSP Services
print_section "9. FSP SERVICES & MARKETPLACE"
master_services=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/fsp-services/master-services" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$master_services" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /fsp-services/master-services"

# 21. FSP Marketplace
marketplace=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/fsp-services/fsp-marketplace/services" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$marketplace" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /fsp-services/fsp-marketplace/services"

# 22. Schedule Templates
print_section "10. SCHEDULES & TEMPLATES"
templates=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/schedule-templates" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$templates" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /schedule-templates"

# 23. Schedules
schedules=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/schedules" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$schedules" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /schedules"

# 24. Work Orders
print_section "11. WORK ORDERS"
work_orders=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/work-orders" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$work_orders" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /work-orders"

# 25. Queries
print_section "12. QUERIES & NOTIFICATIONS"
queries=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/queries" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$queries" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /queries"

# 26. Notifications
notif=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/notifications/unread-count" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$notif" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /notifications/unread-count"

# 27. Farms
print_section "13. FARMS & PLOTS"
farms=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/farms/" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$farms" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /farms/"

# 28. Crops
print_section "14. CROPS & YIELDS"
crops=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/crops/" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$crops" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /crops/"

# 29. Farm Audit - Option Sets
print_section "15. FARM AUDIT SYSTEM"
option_sets=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/farm-audit/option-sets" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$option_sets" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /farm-audit/option-sets"

# 30. Farm Audit - Parameters
parameters=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/farm-audit/parameters" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$parameters" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /farm-audit/parameters"

# 31. Farm Audit - Sections
sections=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/farm-audit/sections" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$sections" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /farm-audit/sections"

# 32. Farm Audit - Templates
audit_templates=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/farm-audit/templates" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$audit_templates" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /farm-audit/templates"

# 33. Farm Audit - Audits
audits=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/farm-audit/audits" \
  -H "Authorization: Bearer $FARMER_TOKEN")
http_code=$(echo "$audits" | tail -n1)
[ "$http_code" = "200" ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
print_result $([ "$http_code" = "200" ]; echo $?) "GET /farm-audit/audits"

# Summary
print_section "TEST SUMMARY"
TOTAL=$((PASS_COUNT + FAIL_COUNT))
echo -e "${GREEN}Passed: $PASS_COUNT${NC}"
echo -e "${RED}Failed: $FAIL_COUNT${NC}"
echo -e "Total Tests: $TOTAL"
echo ""
echo "Success Rate: $(awk "BEGIN {printf \"%.1f\", ($PASS_COUNT/$TOTAL)*100}")%"
echo ""
echo -e "${BLUE}=========================================${NC}"
echo "User Credentials Created:"
echo "  Admin: admin@uzhathunai.com / Admin@123"
echo "  Farmer: farmer@greenvalley.com / Farmer@123"
echo "  FSP: fsp@agriservices.com / FSP@123"
echo ""
if [ ! -z "$FARM_ORG_ID" ]; then
    echo "Organization Created:"
    echo "  Name: Green Valley Organic Farms"
    echo "  ID: $FARM_ORG_ID"
    echo "  Type: FARMING"
    echo ""
fi
echo "API Documentation: ${BASE_URL}/docs"
echo "API Base URL: ${API_BASE}"
echo -e "${BLUE}=========================================${NC}"
