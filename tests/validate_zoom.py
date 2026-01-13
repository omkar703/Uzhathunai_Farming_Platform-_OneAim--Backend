import requests
import time
import sys
import os
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
AUTH_URL = "http://localhost:8000/api/v1/auth"
VIDEO_URL = "http://localhost:8000/api/v1/video"

def log(msg, success=True):
    prefix = "[PASS]" if success else "[FAIL]"
    print(f"{prefix} {msg}")

def get_token(email, password="password123"):
    response = requests.post(f"{AUTH_URL}/login", json={"email": email, "password": password})
    if response.status_code == 200:
        return response.json()["data"]["tokens"]["access_token"]
    else:
        log(f"Login failed for {email}: {response.text}", False)
        return None

def run_tests():
    print("Starting Zoom Integration Validation...")
    
    # 1. Login
    fsp_token = get_token("admin@example.com") # Org Admin acting as FSP
    if not fsp_token: sys.exit(1)
    
    # 2. Setup Data (WorkOrder)
    # Start DB Session manually to create WorkOrder if API not available easily
    # We will use the seeded Default Org (fetch via API or DB)
    # For now, let's try to fetch user credentials to get Org ID?
    # Or just assume assuming we can create one via DB script helper?
    # Better: Use the python script itself to insert WorkOrder into DB directly to save time.
    from app.core.database import SessionLocal
    from app.models.work_order import WorkOrder
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.video_session import VideoSession
    from app.models.enums import WorkOrderStatus
    import uuid
    
    db = SessionLocal()
    try:
        org = db.query(Organization).filter(Organization.name == "Default Org").first()
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        
        if org:
            org.is_approved = True
            db.commit()
            
        # Create Dummy WorkOrder
        wo = WorkOrder(
            farming_organization_id=org.id,
            fsp_organization_id=org.id, # Self-contract for testing
            title="Test Zoom WO",
            status=WorkOrderStatus.ACTIVE,
            created_by=admin_user.id
        )
        db.add(wo)
        
        # Create Outsider User
        from app.core.security import get_password_hash
        outsider = db.query(User).filter(User.email == "outsider@example.com").first()
        if not outsider:
            outsider = User(
                email="outsider@example.com",
                password_hash=get_password_hash("password123"),
                first_name="Out",
                last_name="Sider",
                is_active=True
            )
            db.add(outsider)
            
        db.commit()
        db.refresh(wo)
        work_order_id = str(wo.id)
        print(f"Created WorkOrder: {work_order_id}")
        
    finally:
        db.close()
        
    # 3. Schedule Meeting
    headers = {"Authorization": f"Bearer {fsp_token}"}
    payload = {
        "work_order_id": work_order_id,
        "topic": "Validation Meeting",
        "start_time": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "duration": 30
    }
    
    print("Scheduling meeting...")
    resp = requests.post(f"{VIDEO_URL}/schedule", json=payload, headers=headers)
    
    if resp.status_code == 202:
        log("Schedule Endpoint returned 202 Accepted")
        session_id = resp.json()["data"]["session_id"]
        print(f"Session ID: {session_id}")
    else:
        log(f"Schedule failed: {resp.text}", False)
        sys.exit(1)
        
    # 4. Wait for Background Task
    print("Waiting 5s for background task...")
    time.sleep(5)
    
    # 5. Check Output (DB)
    # API Verification
    # Join URL (FSP - Host)
    resp = requests.get(f"{VIDEO_URL}/{session_id}/join-url", headers=headers)
    if resp.status_code == 200:
        data = resp.json()["data"]
        if data["role"] == "host" and "http" in data["url"]:
            log("FSP retrieved Host URL successfully")
        else:
            log(f"Unexpected data for FSP: {data}", False)
    else:
        # If it failed, maybe background task failed?
        log(f"FSP failed to get URL: {resp.text}. Note: If Mock/Real Zoom not reached, status might be PENDING/CANCELLED.", False)
        
        # Check DB status directly
        db = SessionLocal()
        session = db.query(VideoSession).filter(VideoSession.id == session_id).first()
        print(f"DB Status: {session.status}, ZoomID: {session.zoom_meeting_id}")
        db.close()

    # 6. Security Check (Outsider)
    outsider_token = get_token("outsider@example.com")
    if outsider_token:
        headers_out = {"Authorization": f"Bearer {outsider_token}"}
        resp = requests.get(f"{VIDEO_URL}/{session_id}/join-url", headers=headers_out)
        if resp.status_code == 403:
            log("Security Check Passed: Outsider received 403 Forbidden")
        else:
            log(f"Security Check Failed: Outsider received {resp.status_code}", False)

if __name__ == "__main__":
    run_tests()
