#!/bin/bash

# Configuration
API_URL="http://localhost:8000/api/v1"
# Configuration
API_URL="http://localhost:8000/api/v1"
TIMESTAMP=$(date +%s)
EMAIL="verify_dup_${TIMESTAMP}_$RANDOM@example.com"
PASSWORD="TestPass123!"
ORG_NAME="Unique Farm ${TIMESTAMP}"

echo "1. Registering new user..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'"$EMAIL"'",
    "password": "'"$PASSWORD"'",
    "first_name": "Verify",
    "last_name": "Dup",
    "phone": "+919800000000",
    "preferred_language": "en"
  }')

if [[ "$REGISTER_RESPONSE" != *"id"* ]]; then
  echo "Registration failed or user exists."
fi

echo -e "\n2. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'"$EMAIL"'",
    "password": "'"$PASSWORD"'",
    "remember_me": false
  }')

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "Failed to get access token."
  exit 1
fi
echo "Access Token acquired."

echo -e "\n3. Creating Organization '$ORG_NAME'..."
ORG_RESPONSE=$(curl -s -X POST "$API_URL/organizations" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "'"$ORG_NAME"'",
    "organization_type": "FARMING",
    "description": "Test Org"
  }')

echo "Create Org Response: $ORG_RESPONSE"

if [[ "$ORG_RESPONSE" != *"id"* ]]; then
    echo "❌ Failed to create initial organization."
    exit 1
fi

echo -e "\n4. Verifying 'is_approved' field is FALSE..."
if [[ "$ORG_RESPONSE" == *"\"is_approved\":false"* ]] || [[ "$ORG_RESPONSE" == *"\"is_approved\": false"* ]]; then
    echo "✅ 'is_approved' is FALSE as expected (Pending State)."
else
    echo "❌ 'is_approved' is NOT FALSE. Response: $ORG_RESPONSE"
    exit 1
fi

echo -e "\n5. Registering SECOND user for Duplicate Check..."
EMAIL_2="verify_dup_2_${TIMESTAMP}_$RANDOM@example.com"
REGISTER_RESPONSE_2=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'"$EMAIL_2"'",
    "password": "'"$PASSWORD"'",
    "first_name": "Verify",
    "last_name": "DupTwo",
    "phone": "+919800000002",
    "preferred_language": "en"
  }')

echo -e "\n6. Logging in as SECOND user..."
LOGIN_RESPONSE_2=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'"$EMAIL_2"'",
    "password": "'"$PASSWORD"'",
    "remember_me": false
  }')

ACCESS_TOKEN_2=$(echo $LOGIN_RESPONSE_2 | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN_2" ]; then
    echo "Failed to get access token for User 2."
    exit 1
fi

echo -e "\n7. Attempting to create DUPLICATE Organization '$ORG_NAME' as User 2..."
DUP_RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$API_URL/organizations" \
  -H "Authorization: Bearer $ACCESS_TOKEN_2" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "'"$ORG_NAME"'",
    "organization_type": "FARMING",
    "description": "Duplicate Test"
  }')

echo "Duplicate Create HTTP Code: $DUP_RESPONSE"

if [ "$DUP_RESPONSE" == "409" ]; then
  echo "✅ Verification SUCCESS: Duplicate creation returned 409 Conflict."
  exit 0
elif [ "$DUP_RESPONSE" == "500" ]; then
  echo "❌ Verification FAILED: Duplicate creation returned 500 Internal Server Error."
  exit 1
else
  echo "⚠️ Verification Inconclusive: Returned $DUP_RESPONSE"
  exit 1
fi
