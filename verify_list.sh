#!/bin/bash

# Configuration
API_URL="http://localhost:8000/api/v1"
TIMESTAMP=$(date +%s)
EMAIL="list_verify_${TIMESTAMP}_$RANDOM@example.com"
PASSWORD="TestPass123!"
ORG_NAME="List Test Farm ${TIMESTAMP}"

echo "1. Registering new user..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'"$EMAIL"'",
    "password": "'"$PASSWORD"'",
    "first_name": "List",
    "last_name": "User",
    "phone": "+919000000000",
    "preferred_language": "en"
  }')

echo "2. Logging in..."
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

echo "3. Creating Organization..."
curl -s -o /dev/null -X POST "$API_URL/organizations" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "'"$ORG_NAME"'",
    "organization_type": "FARMING",
    "description": "Test Org for List"
  }'

echo "4. Fetching Organization List..."
LIST_RESPONSE=$(curl -s -X GET "$API_URL/organizations" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

echo "List Response: $LIST_RESPONSE"

if [[ "$LIST_RESPONSE" == *"\"is_approved\":true"* ]] || [[ "$LIST_RESPONSE" == *"\"is_approved\": true"* ]]; then
  echo "✅ 'is_approved' is TRUE (auto-approved), and List Access is GRANTED."
else
  echo "❌ List Access Failed or Unexpected Response."
  echo "Response: $LIST_RESPONSE"
  exit 1
fi
