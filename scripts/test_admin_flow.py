import requests
import time
import subprocess
import json

BASE_URL = "http://localhost:8000/api/v1"

def run_test():
    print("--- 1. Registering Admin User ---")
    admin_email = f"admin_{int(time.time())}@example.com"
    payload = {
        "email": admin_email,
        "password": "Password123",
        "first_name": "System",
        "last_name": "Admin"
    }
    resp = requests.post(f"{BASE_URL}/auth/register", json=payload)
    if resp.status_code != 201:
        print(f"Register failed: {resp.text}")
        return
    user_id = resp.json()["data"]["user"]["id"]
    print(f"User registered with ID: {user_id}")

    print("\n--- 2. Upgrading User to SUPER_ADMIN via DB ---")
    cmd = f'docker exec farm_db psql -U postgres -d uzhathunai_db_v2 -c "INSERT INTO org_member_roles (id, user_id, role_id, is_primary) VALUES (gen_random_uuid(), \'{user_id}\', (SELECT id FROM roles WHERE code = \'SUPER_ADMIN\'), true);"'
    subprocess.run(cmd, shell=True)
    
    print("\n--- 3. Logging in as Admin ---")
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": admin_email, "password": "Password123"})
    token = login_resp.json()["data"]["tokens"]["access_token"]
    
    print("\n--- 4. Listing Organizations (Admin Service) ---")
    headers = {"Authorization": f"Bearer {token}"}
    list_resp = requests.get(f"{BASE_URL}/admin/organizations", headers=headers)
    
    if list_resp.status_code == 200:
        print("SUCCESS: Admin listing works!")
        print(json.dumps(list_resp.json(), indent=2))
    else:
        print(f"FAILED: Status {list_resp.status_code}")
        print(list_resp.text)

if __name__ == "__main__":
    run_test()
