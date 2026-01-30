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
        email = f"test_tpl_{int(time.time())}@example.com"
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

        # 2. Check for an existing template
        resp = client.get(f"{BASE_URL}/farm-audit/templates", headers=headers)
        if resp.status_code != 200:
             print(f"GET templates failed: {resp.text}")
             return
             
        items = resp.json()["data"]["items"]
        if not items:
            print("No templates found to test. Please create one.")
            return

        template_id = items[0]["id"]
        print(f"Testing Template ID: {template_id}")

        # 3. Get Template Details
        resp = client.get(f"{BASE_URL}/farm-audit/templates/{template_id}", headers=headers)
        if resp.status_code != 200:
             print(f"GET template details failed: {resp.text}")
             return
             
        data = resp.json()["data"]
        print(json.dumps(data, indent=2))
        
        # 4. Check Sections
        sections = data.get("sections", [])
        print(f"\nScanning {len(sections)} sections...")
        for sec in sections:
            print(f"Section ID: {sec.get('id')}")
            print(f"  - Name: {sec.get('name')}")         
            print(f"  - Title: {sec.get('title')}")       
            print(f"  - Section Name: {sec.get('section_name')}") 
            print(f"  - Code: {sec.get('section_code')}")
            
            print("  Parameters:")
            params = sec.get("parameters", [])
            for p in params:
                 print(f"    - ID: {p.get('id')}")
                 print(f"      - Name: {p.get('name')}")
                 print(f"      - Label: {p.get('label')}")
                 print(f"      - Code (snapshot): {p.get('parameter_snapshot', {}).get('code')}")

if __name__ == "__main__":
    run_test()
