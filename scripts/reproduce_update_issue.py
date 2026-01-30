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
            return False
        role_id = res[0]
        
        # Insert into org_member_roles
        session.execute(text(
            "INSERT INTO org_member_roles (id, user_id, role_id, is_primary) "
            "VALUES (:uuid, :user_id, :role_id, true)"
        ), {"uuid": str(uuid.uuid4()), "user_id": user_id, "role_id": role_id})
        session.commit()
        return True
    except Exception as e:
        print(f"Upgrade failed: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def run_test():
    with httpx.Client() as client:
        # 1. Register & Login
        email = f"test_update_{int(time.time())}@example.com"
        resp = client.post(f"{BASE_URL}/auth/register", json={
            "email": email, "password": "Password123", "first_name": "Test", "last_name": "User"
        })
        if resp.status_code != 201:
            print(f"Register failed: {resp.text}")
            return
        user_id = resp.json()["data"]["user"]["id"]
        
        upgrade_user(user_id)
        
        login_resp = client.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "Password123"})
        token = login_resp.json()["data"]["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create Parameter with Option A, B
        print("\n--- Creating Parameter with Options A, B ---")
        param_code = f"PRM_UPD_{int(time.time())}"
        create_payload = {
            "code": param_code,
            "parameter_type": "SINGLE_SELECT",
            "translations": [{"language_code": "en", "name": "Update Test Param"}],
            "options": [
                { "label": "Option A", "value": "A" },
                { "label": "Option B", "value": "B" }
            ]
        }
        resp = client.post(f"{BASE_URL}/farm-audit/parameters", json=create_payload, headers=headers)
        if resp.status_code != 201:
            print(f"Create failed: {resp.text}")
            return
        param_id = resp.json()["data"]["id"]
        print(f"Parameter created: {param_id}")
        
        # 3. Update Parameter with Option A, B, C
        print("\n--- Updating Parameter to Options A, B, C ---")
        update_payload = {
            "translations": [{"language_code": "en", "name": "Update Test Param Updated"}],
            "options": [
                { "label": "Option A", "value": "A" },
                { "label": "Option B", "value": "B" },
                { "label": "Option C", "value": "C" }
            ]
        }
        resp = client.put(f"{BASE_URL}/farm-audit/parameters/{param_id}", json=update_payload, headers=headers)
        print(f"Update status: {resp.status_code}")
        if resp.status_code != 200:
             print(f"Update failed: {resp.text}")

        # 4. Get Parameter to Verify
        print("\n--- Verifying Options ---")
        resp = client.get(f"{BASE_URL}/farm-audit/parameters/{param_id}", headers=headers)
        data = resp.json()["data"]
        
        print("Returned Options:")
        found_c = False
        if "option_set" in data:
            for opt in data["option_set"]:
                print(f" - {opt['label']} ({opt['value']})")
                if opt['value'] == 'C':
                    found_c = True
        
        if found_c:
            print("✅ SUCCCESS: Option C found!")
        else:
            print("❌ FAILURE: Option C NOT found!")

if __name__ == "__main__":
    run_test()
