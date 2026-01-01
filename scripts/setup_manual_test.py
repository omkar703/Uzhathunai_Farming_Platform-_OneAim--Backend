import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.work_order import WorkOrder
from app.models.organization import Organization
from app.models.user import User
from app.models.enums import WorkOrderStatus
from app.core.security import get_password_hash

def setup_manual_test_data():
    db = SessionLocal()
    try:
        print("--- Setting up Manual Test Data ---")
        
        # 1. Get Default Org
        org = db.query(Organization).filter(Organization.name == "Default Org").first()
        if not org:
            print("Error: Default Org not found. Please run 'python -m scripts.seed_data' first.")
            return

        # Ensure Org is Approved
        if not org.is_approved:
            org.is_approved = True
            db.commit()
            print("  - Approved Default Org")

        # 2. Get Users
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        farmer_user = db.query(User).filter(User.email == "farmer@example.com").first()
        
        if not admin_user or not farmer_user:
             print("Error: Seed users not found. Please run 'python -m scripts.seed_data' first.")
             return

        # 3. Create Work Order
        # We link the same org for both farming and FSP for simplicity in this self-test
        wo = WorkOrder(
            farming_organization_id=org.id,
            fsp_organization_id=org.id, 
            title="Manual Zoom Test Work Order",
            status=WorkOrderStatus.ACTIVE,
            created_by=admin_user.id
        )
        db.add(wo)
        db.commit()
        db.refresh(wo)
        
        print("\n[SUCCESS] Test Data Created!")
        print("-" * 50)
        print(f"Work Order ID:   {wo.id}")
        print("-" * 50)
        print("User Accounts:")
        print("1. FSP / Schedule Creator:")
        print(f"   Email: {admin_user.email}")
        print("   Pass:  password123")
        print("\n2. Farmer / Participant:")
        print(f"   Email: {farmer_user.email}")
        print("   Pass:  password123")
        print("-" * 50)
        print("\nYou can now use these details in the API calls.")
        
    finally:
        db.close()

if __name__ == "__main__":
    setup_manual_test_data()
