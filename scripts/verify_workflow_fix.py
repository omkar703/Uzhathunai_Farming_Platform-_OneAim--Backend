
import requests
import json
import uuid
import time
from datetime import date
import subprocess

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

def upgrade_user_to_super_admin(user_id):
    print(f"--- Upgrading user {user_id} to SUPER_ADMIN via Docker ---")
    try:
        # Use docker exec psql to upgrade the user
        check_role_cmd = "docker exec aggroconnect_db psql -U postgres -d farm_db -t -c \"SELECT id FROM roles WHERE code = 'SUPER_ADMIN'\""
        role_id_raw = subprocess.check_output(check_role_cmd, shell=True).decode().strip()
        role_id = role_id_raw.split()[0] if role_id_raw.split() else None
        
        if not role_id:
            print("SUPER_ADMIN role not found")
            return False
        
        upgrade_cmd = f"docker exec aggroconnect_db psql -U postgres -d farm_db -c \"INSERT INTO org_member_roles (id, user_id, role_id, is_primary) VALUES (gen_random_uuid(), '{user_id}', '{role_id}', true)\" "
        subprocess.check_call(upgrade_cmd, shell=True)
        print(f"Successfully upgraded user to SUPER_ADMIN (Role ID: {role_id})")
        return True
    except Exception as e:
        print(f"Upgrade failed: {e}")
        return False

def setup_auth():
    print("--- Setting up Auth ---")
    email = f"test_workflow_{int(time.time())}@example.com"
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email, "password": "Password123", "first_name": "Workflow", "last_name": "Test"
    })
    if resp.status_code != 201:
        print(f"Register failed: {resp.text}")
        return None, None
    
    user_id = resp.json()["data"]["user"]["id"]
    if not upgrade_user_to_super_admin(user_id):
        print("Continuing without SUPER_ADMIN (might fail)...")
    
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "Password123"})
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.text}")
        return None, None
        
    token = login_resp.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}, user_id

def log_and_extract(resp, entity_name):
    if resp.status_code not in [200, 201]:
        print(f"❌ Failed to create {entity_name}: {resp.status_code} - {resp.text}")
        return None
    data = resp.json()
    obj_id = data.get("id") or (data.get("data", {}).get("id") if isinstance(data.get("data"), dict) else None)
    if not obj_id:
        print(f"✅ {entity_name} created but no ID in response")
        return "OK"
    print(f"✅ Created {entity_name}: {obj_id}")
    return obj_id

def main():
    headers, user_id = setup_auth()
    if not headers: return

    suffix = int(time.time())
    
    fsp_org_id = log_and_extract(requests.post(f"{BASE_URL}/organizations", json={
        "name": f"FSP Org {suffix}", "organization_type": "FSP", "description": "Test FSP", "district": "Shimoga", "pincode": "577201"
    }, headers=headers), "FSP Org")
    
    farming_org_id = log_and_extract(requests.post(f"{BASE_URL}/organizations", json={
        "name": f"Farming Org {suffix}", "organization_type": "FARMING", "description": "Test Farming", "district": "Shimoga", "pincode": "577201"
    }, headers=headers), "Farming Org")

    if not fsp_org_id or not farming_org_id: return

    farm_id = log_and_extract(requests.post(f"{BASE_URL}/farms", json={
        "name": f"Farm {suffix}", "area": 10.0, "location": {"type": "Point", "coordinates": [75.5, 13.9]}
    }, headers=headers), "Farm")
    
    if not farm_id: return
    
    plot_id = log_and_extract(requests.post(f"{BASE_URL}/plots/farms/{farm_id}/plots", json={
        "name": f"Plot {suffix}", "area": 5.0
    }, headers=headers), "Plot")
    
    if not plot_id: return

    crop_id = log_and_extract(requests.post(f"{BASE_URL}/crops", json={
        "farm_id": farm_id, "plot_id": plot_id, "name": f"Crop {suffix}",
        "crop_type": "VEGETABLE", "sowing_date": str(date.today()), "status": "ACTIVE"
    }, headers=headers), "Crop")

    if not crop_id: return

    print("--- Getting Template ---")
    resp = requests.get(f"{BASE_URL}/farm-audit/templates", headers=headers)
    if resp.status_code == 200 and resp.json()["data"]["items"]:
        template_id = resp.json()["data"]["items"][0]["id"]
    else:
        template_id = log_and_extract(requests.post(f"{BASE_URL}/farm-audit/templates", json={
            "code": f"TPL_{suffix}",
            "translations": [{"language_code": "en", "name": f"Template {suffix}", "description": "Test"}],
            "sections": [{"code": f"SEC_{suffix}", "sort_order": 1, "translations": [{"language_code": "en", "name": "Section 1"}]}]
        }, headers=headers), "Template")

    if not template_id: return

    print("\n--- 2. Creating Audit ---")
    resp = requests.post(f"{BASE_URL}/farm-audit/audits", json={
        "template_id": template_id, "crop_id": crop_id, "fsp_organization_id": fsp_org_id,
        "name": f"Audit {suffix}", "audit_date": str(date.today())
    }, headers=headers)
    
    audit_id = log_and_extract(resp, "Audit")
    if not audit_id: return

    print("\n--- 3. Testing Transition: DRAFT -> IN_PROGRESS ---")
    resp = requests.post(f"{BASE_URL}/farm-audit/audits/{audit_id}/transition", json={"to_status": "IN_PROGRESS"}, headers=headers)
    if resp.status_code == 200:
        print("✅ SUCCESS: DRAFT -> IN_PROGRESS")
    else:
        print(f"❌ FAILED: DRAFT -> IN_PROGRESS: {resp.status_code} - {resp.text}")

    print("\n--- 4. Testing Transition: IN_PROGRESS -> SUBMITTED_FOR_REVIEW ---")
    resp = requests.post(f"{BASE_URL}/farm-audit/audits/{audit_id}/transition", json={"to_status": "SUBMITTED_FOR_REVIEW"}, headers=headers)
    if resp.status_code == 200:
        print("✅ SUCCESS: IN_PROGRESS -> SUBMITTED_FOR_REVIEW")
    else:
        print(f"❌ FAILED: IN_PROGRESS -> SUBMITTED_FOR_REVIEW: {resp.status_code} - {resp.text}")

    print("\n--- 5. Testing Report Generation ---")
    resp = requests.get(f"{BASE_URL}/farm-audit/audits/{audit_id}/report", headers=headers)
    if resp.status_code == 200:
        print("✅ SUCCESS: Report generated for SUBMITTED_FOR_REVIEW audit")
        report_data = resp.json()["data"]
        print(f"Report status: {report_data['audit']['status']}")
    else:
        print(f"❌ FAILED: Report generation: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    main()
