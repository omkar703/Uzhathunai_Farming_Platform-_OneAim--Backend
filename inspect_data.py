
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.config import settings
from app.core.database import SessionLocal

def inspect_data():
    db = SessionLocal()
    try:
        print("--- MASTER SERVICES ---")
        results = db.execute(text("SELECT id, code, name, status FROM master_services")).fetchall()
        for r in results:
            print(f"ID: {r.id} | Code: {r.code} | Name: {r.name} | Status: {r.status}")

        print("\n--- SCHEDULE TEMPLATES (Farming) ---")
        results = db.execute(text("SELECT id, code, is_system_defined, owner_org_id FROM schedule_templates")).fetchall()
        for r in results:
            print(f"ID: {r.id} | Code: {r.code} | System: {r.is_system_defined}")

        print("\n--- TEMPLATES (Audit) ---")
        # Check if templates table exists (it should based on ddl)
        try:
            results = db.execute(text("SELECT id, code, is_system_defined FROM templates")).fetchall()
            for r in results:
                print(f"ID: {r.id} | Code: {r.code} | System: {r.is_system_defined}")
        except Exception as e:
            print(f"Error querying templates: {e}")
            
        print("\n--- TASKS ---")
        print("\n--- USERS (FSP Owner) ---")
        org_id = '5504357f-21a4-4877-b78e-37f8fe7dfec5'
        # Try to find a user who is a member of this org
        # query organization_members or similar tables? 
        # based on models: org_members table?
        # Let's check users table first
        results = db.execute(text(f"SELECT u.id, u.email FROM users u JOIN org_members om ON u.id = om.user_id WHERE om.organization_id = '{org_id}' LIMIT 1")).fetchall()
        for r in results:
            print(f"User ID: {r.id} | Email: {r.email}")

    finally:
        db.close()

if __name__ == "__main__":
    inspect_data()
