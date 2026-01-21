#!/bin/bash

# FSP Test Data Seeding Script for Uzhathunai v2.0
# Creates FSP user, organization, and 5 test services

set -e  # Exit on error

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

# Extract JSON value helper
extract_json() {
    local json=$1
    local key=$2
    echo "$json" | grep -o "\"$key\":\"[^\"]*" | cut -d'"' -f4
}

print_step "FSP TEST DATA SEEDING"

# Step 1: Register FSP User
print_step "1. REGISTERING FSP USER"
echo "Email: testfsp@aggroconnect.com"

register_response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testfsp@aggroconnect.com",
    "password": "TestFSP@123",
    "first_name": "Test",
    "last_name": "FSP",
    "phone": "+919876543210",
    "preferred_language": "en"
  }')

http_code=$(echo "$register_response" | tail -n1)
body=$(echo "$register_response" | head -n-1)

if [ "$http_code" != "200" ] && [ "$http_code" != "201" ]; then
    # Check if user already exists
    if echo "$body" | grep -q "already exists\|already registered"; then
        echo -e "${YELLOW}User already exists, continuing with login...${NC}"
    else
        print_error "User registration failed (HTTP $http_code): $body"
    fi
else
    print_success "User registered successfully"
fi

USER_ID=$(extract_json "$body" "id")
echo "User ID: $USER_ID"

# Step 2: Login to get access token
print_step "2. LOGGING IN"

login_response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testfsp@aggroconnect.com",
    "password": "TestFSP@123"
  }')

http_code=$(echo "$login_response" | tail -n1)
body=$(echo "$login_response" | head -n-1)

if [ "$http_code" != "200" ]; then
    print_error "Login failed (HTTP $http_code): $body"
fi

ACCESS_TOKEN=$(extract_json "$body" "access_token")
if [ -z "$ACCESS_TOKEN" ]; then
    print_error "Failed to extract access token from response"
fi

print_success "Login successful"
echo "Token: ${ACCESS_TOKEN:0:30}..."

# Get user ID from login response if not set
if [ -z "$USER_ID" ]; then
    USER_ID=$(echo "$body" | grep -o '"user":{[^}]*"id":"[^"]*' | grep -o '"id":"[^"]*' | cut -d'"' -f4)
fi

# Step 3: Get master services to find service IDs
print_step "3. FETCHING MASTER SERVICES"

master_services_response=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/fsp-services/master-services" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$master_services_response" | tail -n1)
body=$(echo "$master_services_response" | head -n-1)

if [ "$http_code" != "200" ]; then
    print_error "Failed to fetch master services (HTTP $http_code): $body"
fi

print_success "Master services fetched"

# Extract first 5 service IDs (we'll use these for our services)
SERVICE_IDS=($(echo "$body" | grep -o '"id":"[^"]*' | cut -d'"' -f4 | head -5))

if [ ${#SERVICE_IDS[@]} -lt 5 ]; then
    echo -e "${YELLOW}Warning: Only ${#SERVICE_IDS[@]} master services found. Will use available services.${NC}"
fi

# Use the first (and possibly only) master service ID for all service listings
# Each listing will have different title, description, and pricing
MASTER_SERVICE_ID="${SERVICE_IDS[0]}"

if [ -z "$MASTER_SERVICE_ID" ]; then
    print_error "No master services found in the system. Please seed master services first."
fi

echo "Using master service ID for all listings: $MASTER_SERVICE_ID"
echo "Note: All 5 service listings will use the same master service but with different customizations"

# Step 4: Create FSP Organization with services
print_step "4. CREATING FSP ORGANIZATION"

org_response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/organizations" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Test FSP Services\",
    \"organization_type\": \"FSP\",
    \"contact_email\": \"testfsp@aggroconnect.com\",
    \"contact_phone\": \"+919876543210\",
    \"address\": \"123 Service Street\",
    \"district\": \"Coimbatore\",
    \"pincode\": \"641001\",
    \"description\": \"Professional agricultural service provider for testing\",
    \"services\": [
      {
        \"service_id\": \"$MASTER_SERVICE_ID\",
        \"title\": \"Soil Testing\",
        \"description\": \"Comprehensive soil analysis including pH, NPK, and micronutrients\",
        \"pricing_model\": \"FIXED\",
        \"base_price\": 500,
        \"service_area_districts\": [\"Coimbatore\", \"Erode\", \"Tiruppur\"]
      },
      {
        \"service_id\": \"$MASTER_SERVICE_ID\",
        \"title\": \"Pest Control\",
        \"description\": \"Integrated pest management with organic solutions\",
        \"pricing_model\": \"PER_ACRE\",
        \"base_price\": 2000,
        \"service_area_districts\": [\"Coimbatore\", \"Erode\"]
      },
      {
        \"service_id\": \"$MASTER_SERVICE_ID\",
        \"title\": \"Crop Advisory\",
        \"description\": \"Expert consultation on crop selection and cultivation practices\",
        \"pricing_model\": \"FIXED\",
        \"base_price\": 1500,
        \"service_area_districts\": [\"Coimbatore\", \"Tiruppur\", \"Salem\"]
      },
      {
        \"service_id\": \"$MASTER_SERVICE_ID\",
        \"title\": \"Irrigation Setup\",
        \"description\": \"Drip irrigation system installation and maintenance\",
        \"pricing_model\": \"PER_ACRE\",
        \"base_price\": 15000,
        \"service_area_districts\": [\"Coimbatore\"]
      },
      {
        \"service_id\": \"$MASTER_SERVICE_ID\",
        \"title\": \"Fertilizer Application\",
        \"description\": \"Precision fertilizer application based on soil test results\",
        \"pricing_model\": \"PER_ACRE\",
        \"base_price\": 3000,
        \"service_area_districts\": [\"Coimbatore\", \"Erode\", \"Tiruppur\", \"Salem\"]
      }
    ]
  }")

http_code=$(echo "$org_response" | tail -n1)
body=$(echo "$org_response" | head -n-1)

if [ "$http_code" != "200" ] && [ "$http_code" != "201" ]; then
    print_error "Organization creation failed (HTTP $http_code): $body"
fi

ORG_ID=$(extract_json "$body" "id")
if [ -z "$ORG_ID" ]; then
    print_error "Failed to extract organization ID from response"
fi

print_success "FSP Organization created"
echo "Organization ID: $ORG_ID"
echo "Organization Name: Test FSP Services"
echo "Status: ACTIVE (auto-approved)"

# Step 5: Get organization services to verify and get service IDs
print_step "5. FETCHING CREATED SERVICES"

services_response=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/fsp-services/organizations/${ORG_ID}/services" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$services_response" | tail -n1)
body=$(echo "$services_response" | head -n-1)

if [ "$http_code" != "200" ]; then
    print_error "Failed to fetch organization services (HTTP $http_code): $body"
fi

print_success "Services fetched successfully"

# Extract service listing IDs and names
SERVICE_LISTING_IDS=($(echo "$body" | grep -o '"id":"[^"]*' | cut -d'"' -f4))
SERVICE_NAMES=($(echo "$body" | grep -o '"title":"[^"]*' | cut -d'"' -f4))

echo "Created ${#SERVICE_LISTING_IDS[@]} services:"
for i in "${!SERVICE_LISTING_IDS[@]}"; do
    echo "  $((i+1)). ${SERVICE_NAMES[$i]:-Service $((i+1))}: ${SERVICE_LISTING_IDS[$i]}"
done

# Step 6: Verify services in marketplace
print_step "6. VERIFYING MARKETPLACE VISIBILITY"

marketplace_response=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/fsp-services/fsp-marketplace/services?district=Coimbatore" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

http_code=$(echo "$marketplace_response" | tail -n1)
body=$(echo "$marketplace_response" | head -n-1)

if [ "$http_code" != "200" ]; then
    echo -e "${YELLOW}Warning: Marketplace check failed (HTTP $http_code)${NC}"
else
    marketplace_count=$(echo "$body" | grep -o '"total":[0-9]*' | cut -d':' -f2)
    print_success "Services visible in marketplace (Total: ${marketplace_count:-0})"
fi

# Final Output
print_step "SEEDING COMPLETE"

# Create JSON output
cat << EOF

{
  "user_id": "$USER_ID",
  "organization_id": "$ORG_ID",
  "access_token": "$ACCESS_TOKEN",
  "services": [
    {"id": "${SERVICE_LISTING_IDS[0]:-N/A}", "name": "Soil Testing"},
    {"id": "${SERVICE_LISTING_IDS[1]:-N/A}", "name": "Pest Control"},
    {"id": "${SERVICE_LISTING_IDS[2]:-N/A}", "name": "Crop Advisory"},
    {"id": "${SERVICE_LISTING_IDS[3]:-N/A}", "name": "Irrigation Setup"},
    {"id": "${SERVICE_LISTING_IDS[4]:-N/A}", "name": "Fertilizer Application"}
  ]
}

EOF

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}FSP Test Data Created Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Login Credentials:"
echo "  Email: testfsp@aggroconnect.com"
echo "  Password: TestFSP@123"
echo ""
echo "Organization:"
echo "  Name: Test FSP Services"
echo "  ID: $ORG_ID"
echo "  Type: FSP"
echo "  Status: ACTIVE"
echo ""
echo "Services Created: ${#SERVICE_LISTING_IDS[@]}"
echo ""
echo "View logs with:"
echo "  docker-compose logs -f --tail=100 app"
echo ""
echo -e "${GREEN}========================================${NC}"
