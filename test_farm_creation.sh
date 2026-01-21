#!/bin/bash
# Test farm creation with authenticated user

echo "=== Testing Farm Creation API ==="
echo ""

# Step 1: Login to get JWT token
echo "Step 1: Logging in to get JWT token..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"userfar@gmail.com","password":"userFarm*1234"}')

echo "Login response: $LOGIN_RESPONSE"
echo ""

# Extract access token
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.data.tokens.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Failed to get access token"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "✅ Successfully obtained access token"
echo ""

# Step 2: Create farm
echo "Step 2: Creating farm..."
FARM_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/farms/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Farm Migration",
    "address": "123 Farm Road",
    "city": "Khandwa",
    "district": "Khandwa",
    "state": "MP",
    "pincode": "450001",
    "location": {
      "type": "Point",
      "coordinates": [76.3512, 21.8245]
    },
    "area": 50,
    "description": "Test farm to verify city column fix"
  }')

echo "Farm creation response:"
echo "$FARM_RESPONSE" | jq '.'
echo ""

# Check if farm was created successfully
FARM_ID=$(echo $FARM_RESPONSE | jq -r '.id // .data.id // empty')
SUCCESS=$(echo $FARM_RESPONSE | jq -r '.success // empty')

if [ "$SUCCESS" == "true" ] || [ ! -z "$FARM_ID" ]; then
    echo "✅ Farm created successfully!"
    echo "Farm ID: $FARM_ID"
    exit 0
else
    ERROR_MSG=$(echo $FARM_RESPONSE | jq -r '.message // .detail // "Unknown error"')
    echo "❌ Farm creation failed: $ERROR_MSG"
    exit 1
fi
