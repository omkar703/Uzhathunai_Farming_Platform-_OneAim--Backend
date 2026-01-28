import requests
import json
import sys
import time

# Constants
BASE_URL = "http://localhost:8000/api/v1"
FARMER_EMAIL = "niren@gmail.com"
FSP_EMAIL = "fsp_manager@gmail.com" # FSP Manager
PASSWORD = "Test@12345"
TEMPLATE_CODE = "WHEAT_120_PLAN"

# IDs from seed (optional fallback)
FSP_ORG_ID = "b8879df7-59e2-4141-a51b-6b18223ed0f9"
FARMER_ORG_ID = "323a3c49-1a25-4979-b4b0-8debf75ec516"
TEMPLATE_ID = "b4f9e6d6-457d-4582-8c0e-055cccece3cc"

def login(email, password):
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    if resp.status_code != 200:
        print(f"Login failed for {email}: {resp.text}")
        sys.exit(1)
    return resp.json()["data"]["tokens"]["access_token"]

def verify_deployment():
    try:
        session = requests.Session()
        
        # 1. Login Farmer
        print("Logging in Farmer...")
        farmer_token = login(FARMER_EMAIL, PASSWORD)
        farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
        
        # 2. Get Crop ID
        print("Fetching Crops...")
        crops_resp = session.get(f"{BASE_URL}/crops", headers=farmer_headers)
        if crops_resp.status_code != 200:
            print(f"Failed to get crops: {crops_resp.text}")
            return False
            
        crops = crops_resp.json()["data"]["items"]
        if not crops:
            print("No crops found for farmer.")
            return False
            
        target_crop = crops[0] # Just pick first
        crop_id = target_crop["id"]
        print(f"Target Crop: {target_crop.get('name')} ({crop_id})")

        # 3. Create Work Order (Farmer)
        print("\nCreating Work Order...")
        wo_payload = {
            "farming_organization_id": FARMER_ORG_ID,
            "fsp_organization_id": FSP_ORG_ID,
            "title": "Schedule Deployment Test",
            "description": "Testing schedule deployment permissions",
            "access_granted": True # Default
        }
        wo_resp = session.post(f"{BASE_URL}/work-orders", json=wo_payload, headers=farmer_headers)
        if wo_resp.status_code != 201:
            print(f"Failed to create WO: {wo_resp.text}")
            return False
        
        wo_id = wo_resp.json()["data"]["id"]
        print(f"Work Order Created: {wo_id}")

        # 4. Add Scope (Farmer) - with WRITE=FALSE
        print("Adding Scope (Write=False)...")
        scope_payload = {
            "scope_items": [
                {
                    "scope": "CROP",
                    "scope_id": crop_id,
                    "access_permissions": {
                        "read": True,
                        "write": False, # Explicitly denied write
                        "track": True
                    }
                }
            ]
        }
        scope_resp = session.post(f"{BASE_URL}/work-orders/{wo_id}/scope", json=scope_payload, headers=farmer_headers)
        if scope_resp.status_code != 201:
            print(f"Failed to add scope: {scope_resp.text}")
            # return False # Proceeding anyway to see if we can accept
            
        # 5. Login FSP
        print("\nLogging in FSP...")
        fsp_token = login(FSP_EMAIL, PASSWORD)
        fsp_headers = {"Authorization": f"Bearer {fsp_token}"}
        
        # 6. Accept Work Order (FSP)
        print("FSP Accepting Work Order...")
        accept_resp = session.post(f"{BASE_URL}/work-orders/{wo_id}/accept", headers=fsp_headers)
        if accept_resp.status_code != 200:
            print(f"Failed to accept WO: {accept_resp.text}")
            return False
        print("Work Order Accepted.")

        # 7. Start Work Order (FSP)
        print("FSP Starting Work Order...")
        start_resp = session.post(f"{BASE_URL}/work-orders/{wo_id}/start", headers=fsp_headers)
        if start_resp.status_code != 200:
            print(f"Failed to start WO: {start_resp.text}")
            return False
        print("Work Order Started (ACTIVE).")

        # 8. Deploy Schedule (FSP) - Should SUCCEED (access_granted=True overrides write=False)
        print("\n[TEST 1] Creating Schedule (Expect SUCCESS)...")
        deploy_payload = {
            "crop_id": crop_id,
            "template_id": TEMPLATE_ID,
            "name": "Deployed Valid Schedule",
            "template_parameters": {
                "start_date": "2026-02-01"
            }
        }
        
        deploy_resp = session.post(f"{BASE_URL}/schedules/from-template", json=deploy_payload, headers=fsp_headers)
        
        if deploy_resp.status_code == 200:
            print("✅ Schedule created successfully!")
        else:
            print(f"❌ Schedule creation failed: {deploy_resp.text}")
            return False
            
        # 9. Revoke Access (Farmer)
        print("\n[TEST 2] Revoking Access...")
        revoke_payload = {"access_granted": False}
        revoke_resp = session.put(f"{BASE_URL}/work-orders/{wo_id}/access", json=revoke_payload, headers=farmer_headers)
        if revoke_resp.status_code != 200:
            print(f"Failed to revoke access: {revoke_resp.text}")
            return False
        print("Access Revoked.")
        
        # 10. Deploy Schedule (FSP) - Should FAIL
        print("\n[TEST 3] Creating Schedule after Revoke (Expect FAILURE)...")
        deploy_payload["name"] = "Deployed Invalid Schedule"
        
        deploy_fail_resp = session.post(f"{BASE_URL}/schedules/from-template", json=deploy_payload, headers=fsp_headers)
        
        if deploy_fail_resp.status_code == 403 or deploy_fail_resp.status_code == 401 or "permission" in deploy_fail_resp.text.lower():
             print(f"✅ Schedule creation correctly rejected. Status: {deploy_fail_resp.status_code}")
        else:
             print(f"❌ Schedule creation should have failed but got: {deploy_fail_resp.status_code} - {deploy_fail_resp.text}")
             return False
             
        print("\n🎉 Verification Successful!")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_deployment()
    sys.exit(0 if success else 1)
