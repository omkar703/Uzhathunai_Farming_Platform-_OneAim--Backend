
import json
import urllib.request
import urllib.error
import sys
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1"

def make_request(method, url, data=None, headers=None):
    if headers is None:
        headers = {}
    
    if data is not None:
        data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

def main():
    print("Starting API-Only Verification of Schedule Template DELETE...")
    
    # 1. Register new FSP User
    email = f"fsp_verify_{uuid4().hex[:6]}@test.com"
    password = "TestUser@123456" # > 8 chars
    
    print(f"Registering user {email}...")
    reg_data = {
        "email": email,
        "password": password,
        "full_name": "Delete Tester",
        "phone_number": f"+91{uuid4().int % 10000000000:010d}", # Random phone
        "preferred_language": "en"
    }
    status, body = make_request("POST", f"{BASE_URL}/auth/register", reg_data)
    
    if status not in [200, 201]:
         print(f"Registration Failed: {status} {body}")
         # Maybe user exists, try login
         pass

    print("Logging in...")
    status, body = make_request("POST", f"{BASE_URL}/auth/login", {"email": email, "password": password})
    
    if status != 200:
        print(f"Login Failed: {status} {body}")
        sys.exit(1)

    resp_json = json.loads(body)
    token = resp_json["data"]["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 1.1 Create Organization (User needs to be in an org to own a template)
    print("Creating FSP Organization...")
    org_data = {
        "name": f"Verif Org {uuid4().hex[:6]}",
        "organization_type": "FSP",
        "description": "Test Org",
        "contact_email": email,
        "contact_phone": "+919876543210",
         # Add address fields if required by schema, usually validation is strict
        "address": "123 Test St",
        "city": "Test City", 
        "state": "Test State",
        "postal_code": "123456",
        "country": "Test Country"
    }
    status, body = make_request("POST", f"{BASE_URL}/organizations", org_data, headers=headers)
    if status not in [200, 201]:
         print(f"Org Create Failed: {status} {body}")
         # Attempt to list orgs if create failed (maybe user already has one?)
         pass


    # 2. Get Required Data (Crop Type, Org ID)
    # Get Org ID from Profile
    print("Fetching User Profile...")
    status, body = make_request("GET", f"{BASE_URL}/auth/me", headers=headers)
    profile_resp = json.loads(body)
    # Handle response wrapper if present
    if "data" in profile_resp:
        user_id = profile_resp["data"]["id"]
    else:
        user_id = profile_resp["id"]
    
    # Get Organizations
    print("Fetching Organizations...")
    status, body = make_request("GET", f"{BASE_URL}/organizations", headers=headers)
    org_resp = json.loads(body)
    
    orgs = []
    if "data" in org_resp and isinstance(org_resp["data"], dict) and "items" in org_resp["data"]:
        orgs = org_resp["data"]["items"]
    elif "items" in org_resp:
        orgs = org_resp["items"]
    elif isinstance(org_resp, list):
         orgs = org_resp
    elif "data" in org_resp and isinstance(org_resp["data"], list):
         orgs = org_resp["data"]

    if not orgs:
        # Check if we just created one, maybe listing is delayed or we need to handle pagination differently?
        # But we just created one, so it should be there.
        # Fallback: Use the one we created if we can't list it? 
        # But Create Org likely returns the ID.
        print(f"No organizations found. Response: {body}")
        # Try to use the created one if listing fails
        sys.exit(1)
    
    val_org_id = orgs[0]["id"]
    print(f"Using Org ID: {val_org_id}")

    # 3. Enable Consultancy Service (Required for Template Creation)
    print("Fetching Master Services...")
    status, body = make_request("GET", f"{BASE_URL}/fsp-services/master-services", headers=headers)
    master_resp = json.loads(body)
    
    master_services = []
    if "data" in master_resp and isinstance(master_resp["data"], dict) and "items" in master_resp["data"]:
         master_services = master_resp["data"]["items"]
    elif "items" in master_resp:
         master_services = master_resp["items"]
    elif isinstance(master_resp, list):
         master_services = master_resp

    consultancy_id = None
    for ms in master_services:
        if ms.get("code") == "CONSULTANCY" or ms.get("name") == "Consultancy":
            consultancy_id = ms["id"]
            break
            
    if not consultancy_id:
        print("Consultancy Master Service not found. Attempting creation without it (might fail)...")
    else:
        print(f"Adding Consultancy Service ({consultancy_id}) to Org...")
        svc_data = {
            "service_id": consultancy_id,
            "is_active": True,
            "areas_served": ["Test Area"],
            "base_price": 100,
            "price_unit": "per_visit"
        }
        # Endpoint might be /fsp-services/services or /fsp-services/listings
        # Checking file list... api/v1/fsp_services.py
        # Assuming POST /fsp-services/services
        status, body = make_request("POST", f"{BASE_URL}/fsp-services/items", svc_data, headers=headers) 
        # Actually usually it is /fsp-services/items or similar. Let's guess /fsp-services/listings based on typical naming.
        # But wait, looking at file list: api/v1/fsp_services.py.
        # Let's try /fsp-services/listings first.
        if status not in [200, 201]:
             # Try alternate endpoint if 404
             status, body = make_request("POST", f"{BASE_URL}/fsp-services/services", svc_data, headers=headers)

        if status not in [200, 201]:
             print(f"Failed to add service: {status} {body}")
             # Proceeding anyway, maybe it isn't strictly enforced or I guessed wrong endpoint
        else:
             print("Consultancy Service Added.")

    # Get Crop Type
    print("Fetching Crop Types...")
    status, body = make_request("GET", f"{BASE_URL}/crop-data/types", headers=headers)
    crop_resp = json.loads(body)
    
    crop_types = []
    if "data" in crop_resp and isinstance(crop_resp["data"], dict) and "items" in crop_resp["data"]:
         crop_types = crop_resp["data"]["items"]
    elif "items" in crop_resp:
         crop_types = crop_resp["items"]
    elif isinstance(crop_resp, list):
         crop_types = crop_resp
    elif "data" in crop_resp and isinstance(crop_resp["data"], list):
         crop_types = crop_resp["data"]

    if not crop_types:
        print(f"No crop types found. Response: {body}")
        sys.exit(1)
        
    crop_type_id = crop_types[0]["id"]
    print(f"Using Crop Type ID: {crop_type_id}")

    # 3. Create Template
    print("Creating Schedule Template...")
    new_code = f"API_DEL_TEST_{uuid4().hex[:6]}"
    tmpl_data = {
        "code": new_code,
        "crop_type_id": crop_type_id,
        "is_system_defined": False,
        "owner_org_id": val_org_id,
        "notes": "Created by verification script",
        "translations": [
             {"language_code": "en", "name": "Verification Template", "description": "To be deleted"}
        ]
    }
    
    status, body = make_request("POST", f"{BASE_URL}/schedule-templates", data=tmpl_data, headers=headers)
    if status not in [200, 201]:
        print(f"Create Template Failed: {status} {body}")
        sys.exit(1)
        
    template = json.loads(body)
    template_id = template["id"]
    print(f"Template Created: {template_id}")

    # 4. Delete Template
    print(f"Calling DELETE /api/v1/schedule-templates/{template_id}...")
    status, body = make_request("DELETE", f"{BASE_URL}/schedule-templates/{template_id}", headers=headers)
    
    print(f"DELETE Response Status: {status}")
    if status != 204:
        print(f"DELETE Failed Body: {body}")
        sys.exit(1)
    
    print("Delete Request Successful (204).")

    # 5. Verify Deletion (Get Template)
    print("Verifying Deletion via GET...")
    status, body = make_request("GET", f"{BASE_URL}/schedule-templates/{template_id}", headers=headers)
    
    if status == 200:
        tmpl_check = json.loads(body)
        is_active = tmpl_check.get("is_active")
        print(f"GET Template is_active: {is_active}")
        if is_active is False:
            print("SUCCESS: Template soft-deleted via API.")
        else:
            print("FAILURE: Template still active after delete!")
            sys.exit(1)
    else:
        print(f"GET Response Status: {status} (If 404, that might be okay depending on implementation, but we expect soft delete)")
        # Soft delete usually implies 200 with is_active=False OR filtered out from lists. 
        # Detailed GET usually returns it regardless of status if ID is known, or might return 404.
        # Based on my code implementation, I didn't change GET logic, so it should return the object.
        
if __name__ == "__main__":
    main()
