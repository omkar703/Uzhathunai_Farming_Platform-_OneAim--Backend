import httpx
import time
import json
import uuid
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

BASE_URL = "http://localhost:8000/api/v1"
DB_URL = "postgresql://postgres:postgres@db:5432/farm_db"

def upgrade_user(user_id):
    print(f"Upgrading user {user_id} to SUPER_ADMIN...")
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Get SUPER_ADMIN role id
        res = session.execute(text("SELECT id FROM roles WHERE code = 'SUPER_ADMIN'")).fetchone()
        if not res:
            print("SUPER_ADMIN role not found in roles table")
            # Try searching in other tables or just return false
            return False
        role_id = res[0]
        
        # Insert into org_member_roles
        session.execute(text(
            "INSERT INTO org_member_roles (id, user_id, role_id, is_primary) "
            "VALUES (:uuid, :user_id, :role_id, true)"
        ), {"uuid": str(uuid.uuid4()), "user_id": user_id, "role_id": role_id})
        session.commit()
        print("Successfully upgraded user via SQLAlchemy")
        return True
    except Exception as e:
        print(f"Upgrade failed: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def run_test():
    with httpx.Client() as client:
        print("--- 1. Registering User ---")
        email = f"test_user_{int(time.time())}@example.com"
        payload = {
            "email": email,
            "password": "Password123",
            "first_name": "Test",
            "last_name": "User"
        }
        resp = client.post(f"{BASE_URL}/auth/register", json=payload)
        if resp.status_code != 201:
            print(f"Register failed: {resp.text}")
            return
        
        data = resp.json()
        user_id = data["data"]["user"]["id"]
        print(f"User registered with ID: {user_id}")

        print("\n--- 2. Upgrading User ---")
        if not upgrade_user(user_id):
            return

        print("\n--- 3. Logging in ---")
        login_resp = client.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "Password123"})
        if login_resp.status_code != 200:
            print(f"Login failed: {login_resp.text}")
            return
            
        token = login_resp.json()["data"]["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        print("\n--- 4. Creating SINGLE_SELECT Parameter with Inline Options ---")
        param_code = f"PRM_TEST_{int(time.time())}"
        payload = {
            "code": param_code,
            "parameter_type": "SINGLE_SELECT",
            "translations": [
                {
                    "language_code": "en",
                    "name": "this is the single choice question",
                    "description": ""
                }
            ],
            "option_set": [
                { "label": "option1", "value": "option1" },
                { "label": "option2", "value": "option2" }
            ],
            "options": [
                { "label": "option1", "value": "option1" },
                { "label": "option2", "value": "option2" }
            ]
        }
        
        resp = client.post(f"{BASE_URL}/farm-audit/parameters", json=payload, headers=headers)
        
        if resp.status_code == 201:
            print("✅ SUCCESS: Parameter created successfully with inline options!")
            result = resp.json()
            param_id = result["data"]["id"]
            
            # --- VERIFICATION STEP ---
            print(f"\n--- 5. GET Parameter {param_id} to verify response ---")
            get_resp = client.get(f"{BASE_URL}/farm-audit/parameters/{param_id}", headers=headers)
            
            if get_resp.status_code == 200:
                get_data = get_resp.json()["data"]
                # print(json.dumps(get_data, indent=2))
                
                # Check for option_set
                option_set = get_data.get("option_set")
                if option_set and len(option_set) > 0:
                     print(f"✅ Verified: GET response contains 'option_set' with {len(option_set)} items.")
                     for opt in option_set:
                         print(f"   - Option: {opt.get('value')} (Label: {opt.get('label')})")
                else:
                    print("❌ Error: GET response missing 'option_set' or it is empty!")
                    print(json.dumps(get_data, indent=2))
            else:
                 print(f"❌ Failed to GET parameter: {get_resp.status_code}")
                 print(get_resp.text)
            
        else:
            print(f"❌ FAILED to create parameter: Status {resp.status_code}")
            print(resp.text)

if __name__ == "__main__":
    run_test()
