"""
Test script for user endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Get auth token (using existing test credentials)
auth_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "admin@example.com",
        "password": "admin123"
    }
)

if auth_response.status_code == 200:
    token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✓ Authentication successful\n")
    
    # Test 1: Search freelancers endpoint
    print("=" * 60)
    print("TEST 1: GET /api/v1/users/freelancers")
    print("=" * 60)
    
    response = requests.get(
        f"{BASE_URL}/users/freelancers",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Users Found: {len(data.get('data', []))}")
        if data.get('data'):
            print("\nSample User:")
            print(json.dumps(data['data'][0], indent=2))
    else:
        print(f"Error: {response.text}")
    
    # Test 2: Search with query
    print("\n" + "=" * 60)
    print("TEST 2: GET /api/v1/users/freelancers?q=test")
    print("=" * 60)
    
    response = requests.get(
        f"{BASE_URL}/users/freelancers?q=test",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Users Found: {len(data.get('data', []))}")
    
    # Test 3: Get organization members (need org_id)
    print("\n" + "=" * 60)
    print("TEST 3: Checking member endpoint structure")
    print("=" * 60)
    
    # First get user's organizations
    orgs_response = requests.get(
        f"{BASE_URL}/organizations",
        headers=headers
    )
    
    if orgs_response.status_code == 200:
        orgs = orgs_response.json()
        if orgs.get('items'):
            org_id = orgs['items'][0]['id']
            print(f"Testing with Organization ID: {org_id}")
            
            # Get members
            members_response = requests.get(
                f"{BASE_URL}/organizations/{org_id}/members",
                headers=headers
            )
            
            print(f"Status Code: {members_response.status_code}")
            if members_response.status_code == 200:
                members_data = members_response.json()
                print(f"Members Found: {len(members_data.get('items', []))}")
                if members_data.get('items'):
                    print("\nSample Member Structure:")
                    member = members_data['items'][0]
                    print(json.dumps({
                        "id": member.get('id'),
                        "user_id": member.get('user_id'),
                        "user_name": member.get('user_name'),
                        "user_email": member.get('user_email'),
                        "status": member.get('status'),
                        "roles": member.get('roles', [])
                    }, indent=2))
                    
                    # Verify user_name and user_email are present
                    if member.get('user_name'):
                        print("\n✓ user_name field is populated")
                    else:
                        print("\n✗ user_name field is missing or null")
                    
                    if member.get('user_email'):
                        print("✓ user_email field is populated")
                    else:
                        print("✗ user_email field is missing or null")
            else:
                print(f"Error: {members_response.text}")
        else:
            print("No organizations found for testing")
    
else:
    print(f"Authentication failed: {auth_response.status_code}")
    print(auth_response.text)
