
from sqlalchemy import create_url, create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/uzhathunai_dev")
engine = create_engine(db_url)

def check_user_role(email):
    with engine.connect() as conn:
        print(f"\n--- Checking User: {email} ---")
        user = conn.execute(text("SELECT id, email FROM users WHERE email = :email"), {"email": email}).first()
        if not user:
            print("User not found!")
            return
        
        user_id = user[0]
        print(f"User ID: {user_id}")
        
        roles = conn.execute(text("""
            SELECT r.code, r.name, omr.organization_id 
            FROM roles r
            JOIN org_member_roles omr ON r.id = omr.role_id
            WHERE omr.user_id = :user_id
        """), {"user_id": user_id}).all()
        
        print("Roles found:")
        for r in roles:
            print(f"  - Code: {r[0]}, Name: {r[1]}, Org ID: {r[2]}")

def list_system_items():
    with engine.connect() as conn:
        print("\n--- System Defined Input Items (Sample) ---")
        items = conn.execute(text("SELECT id, code, is_system_defined FROM input_items WHERE is_system_defined = true LIMIT 5")).all()
        for i in items:
            print(f"  - ID: {i[0]}, Code: {i[1]}, System: {i[2]}")

if __name__ == "__main__":
    check_user_role("superadmin@uzhathunai.com")
    list_system_items()
