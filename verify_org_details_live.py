
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def log(msg, color=None):
    print(msg)

def verify():
    timestamp = int(datetime.now().timestamp())
    email = f"verify_{timestamp}@example.com"
    password = "TestPass123!"
    
    # 1. Register
    log(f"Registering {email}...")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Verify User",
        "phone_number": f"+91{timestamp}"[:13],
        "preferred_language": "en"
    })
    if resp.status_code not in [200, 201]:
        log(f"Registration failed: {resp.text}")
        return False
        
    # 2. Login
    log("Logging in...")
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password,
        "remember_me": False
    })
    if resp.status_code != 200:
        log(f"Login failed: {resp.text}")
        return False
    
    log(f"Login Response: {resp.text}")
    
    data = resp.json()
    token = None
    if "tokens" in data:
        token = data["tokens"]["access_token"]
    elif "access_token" in data:
        token = data["access_token"]
    elif "data" in data and "access_token" in data["data"]:
        token = data["data"]["access_token"]
    elif "data" in data and "tokens" in data["data"] and "access_token" in data["data"]["tokens"]:
        token = data["data"]["tokens"]["access_token"]
    else:
        log("Could not find access_token in response")
        return False
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create Organization
    org_name = f"Verify Org {timestamp}"
    log(f"Creating Organization {org_name}...")
    resp = requests.post(f"{BASE_URL}/organizations", headers=headers, json={
        "name": org_name,
        "organization_type": "FARMING",
        "description": "Test Org for Details Verification",
        "district": "Test District",
        "pincode": "123456"
    })
    
    if resp.status_code not in [200, 201]:
        log(f"Org creation failed: {resp.text}")
        return False
        
    org_data = resp.json()["data"]
    org_id = org_data["id"]
    log(f"Organization ID: {org_id}")
    
    # 4. Get Organization Details
    log("Fetching Organization Details...")
    resp = requests.get(f"{BASE_URL}/organizations/{org_id}", headers=headers)
    
    if resp.status_code != 200:
        log(f"Get details failed: {resp.text}")
        return False
        
    details = resp.json()["data"]
    # log(json.dumps(details, indent=2))
    
    # 5. Verify Fields
    failures = []
    
    if "members" not in details:
        failures.append("Missing 'members' field")
    else:
        if len(details["members"]) < 1:
            failures.append("Members list is empty (should have at least creator)")
        else:
            log("Members found: OK")
            
    if "recent_audits" not in details:
        failures.append("Missing 'recent_audits' field")
    else:
        log("Recent Audits found: OK")
        
    if "recent_work_orders" not in details:
        failures.append("Missing 'recent_work_orders' field")
    else:
        log("Recent Work Orders found: OK")
        
    if "stats" not in details:
        failures.append("Missing 'stats' field")
    else:
        log("Stats info found: OK")
        
    if failures:
        log(f"Verification FAILED: {', '.join(failures)}")
        return False
    
    log("Verification PASSED!")
    return True

if __name__ == "__main__":
    try:
        success = verify()
        if not success:
            sys.exit(1)
    except Exception as e:
        log(f"Exception: {e}")
        sys.exit(1)
