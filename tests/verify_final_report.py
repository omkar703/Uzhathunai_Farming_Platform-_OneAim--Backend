#!/usr/bin/env python3
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
TIMEOUT = 60

def print_step(msg):
    print(f"\n{YELLOW}=== {msg} ==={RESET}")

def verify_flow():
    session = requests.Session()
    
    try:
        print_step("1. Setup: Registering FSP & Farmer")
        timestamp = int(time.time())
        
        # Register FSP
        fsp_email = f"fsp_{timestamp}@test.com"
        resp = session.post(f"{BASE_URL}/auth/register/", json={
            "email": fsp_email, "password": "Test@123", "first_name": "FSP", "last_name": "User", "phone_number": f"+91{timestamp % 10000000000:010d}"
        }, timeout=TIMEOUT)
        fsp_token = resp.json()["data"]["tokens"]["access_token"]
        fsp_headers = {"Authorization": f"Bearer {fsp_token}"}
        
        # Register Farmer
        farmer_email = f"farmer_{timestamp}@test.com"
        resp = session.post(f"{BASE_URL}/auth/register/", json={
            "email": farmer_email, "password": "Test@123", "first_name": "Farmer", "last_name": "User", "phone_number": f"+91{(timestamp+1) % 10000000000:010d}"
        }, timeout=TIMEOUT)
        farmer_token = resp.json()["data"]["tokens"]["access_token"]
        farmer_headers = {"Authorization": f"Bearer {farmer_token}"}

        print_step("2. Setup: Organizations & Approvals")
        # FSP Org
        resp = session.post(f"{BASE_URL}/organizations/", json={
            "name": f"FSP_{timestamp}", "organization_type": "FSP", "description": "Test", "district": "Test", "pincode": "123456"
        }, headers=fsp_headers, timeout=TIMEOUT)
        fsp_org_id = resp.json()["data"]["id"]
        
        # Farmer Org
        resp = session.post(f"{BASE_URL}/organizations/", json={
            "name": f"Farm_{timestamp}", "organization_type": "FARMING", "description": "Test", "district": "Test", "pincode": "123456"
        }, headers=farmer_headers, timeout=TIMEOUT)
        farm_org_id = resp.json()["data"]["id"]

        # Approve via Shell (Simulating Admin)
        import subprocess
        subprocess.run(f'docker compose exec -T db psql -U postgres -d farm_db -c "UPDATE organizations SET is_approved = true, status = \'ACTIVE\' WHERE id IN (\'{fsp_org_id}\', \'{farm_org_id}\');"', shell=True)
        
        print_step("3. Setup: Farm, Plot, Crop, Template")
        # Farm
        resp = session.post(f"{BASE_URL}/farms/", json={
            "name": "Test Farm", "area": 10, "location": {"type": "Point", "coordinates": [0,0]},
            "boundary": {"type": "Polygon", "coordinates": [[[0,0],[1,0],[1,1],[0,1],[0,0]]]}
        }, headers=farmer_headers, timeout=TIMEOUT)
        farm_id = resp.json()["data"]["id"]
        
        # Plot
        resp = session.post(f"{BASE_URL}/plots/farms/{farm_id}/plots/", json={
            "name": "Plot 1", "area": 5
        }, headers=farmer_headers, timeout=TIMEOUT)
        plot_id = resp.json()["data"]["id"]

        # Crop
        resp = session.post(f"{BASE_URL}/crops/", json={
            "farm_id": farm_id, "plot_id": plot_id, "name": "Rice", "crop_type": "CEREAL", "sowing_date": "2025-01-01", "status": "ACTIVE"
        }, headers=farmer_headers, timeout=TIMEOUT)
        crop_id = resp.json()["data"]["id"]
        
        # Audit Template Seeding
        sec_resp = session.post(f"{BASE_URL}/farm-audit/sections/", json={"translations": [{"language_code": "en", "name": "Section 1"}], "code": f"S1_{timestamp}"}, headers=fsp_headers, timeout=TIMEOUT)
        section_id = sec_resp.json()["data"]["id"]
        
        # Create Numeric, Text, and Select Params
        p1 = session.post(f"{BASE_URL}/farm-audit/parameters/", json={"parameter_type": "NUMERIC", "translations": [{"language_code": "en", "name": "Yield"}], "code": f"P1_{timestamp}"}, headers=fsp_headers, timeout=TIMEOUT).json()["data"]["id"]
        p2 = session.post(f"{BASE_URL}/farm-audit/parameters/", json={"parameter_type": "TEXT", "translations": [{"language_code": "en", "name": "Health"}], "code": f"P2_{timestamp}"}, headers=fsp_headers, timeout=TIMEOUT).json()["data"]["id"]
        p3 = session.post(f"{BASE_URL}/farm-audit/parameters/", json={
            "parameter_type": "SINGLE_SELECT", 
            "translations": [{"language_code": "en", "name": "Type"}], 
            "code": f"P3_{timestamp}",
            "options": [
                {"label": "Organic", "value": "opt1"},
                {"label": "Chemical", "value": "opt2"}
            ]
        }, headers=fsp_headers, timeout=TIMEOUT).json()["data"]["id"]
        
        # Template
        template_resp = session.post(f"{BASE_URL}/farm-audit/templates/", json={
            "code": f"T_{timestamp}", "translations": [{"language_code": "en", "name": "Report Test"}],
            "sections": [{"section_id": section_id, "sort_order": 1, "parameters": [
                {"parameter_id": p1, "is_required": True, "sort_order": 1},
                {"parameter_id": p2, "is_required": True, "sort_order": 2},
                {"parameter_id": p3, "is_required": True, "sort_order": 3}
            ]}]
        }, headers=fsp_headers, timeout=TIMEOUT)
        template_id = template_resp.json()["data"]["id"]

        print_step("4. Audit Execution")
        audit_resp = session.post(f"{BASE_URL}/farm-audit/audits/", json={
            "template_id": template_id, "crop_id": crop_id, "fsp_organization_id": fsp_org_id, "name": "Final Test Audit"
        }, headers=fsp_headers, timeout=TIMEOUT)
        audit_id = audit_resp.json()["data"]["id"]
        
        # Get Instance IDs and find Option IDs
        struct = session.get(f"{BASE_URL}/farm-audit/audits/{audit_id}/structure/", headers=fsp_headers, timeout=TIMEOUT).json()["data"]
        params_meta = struct["sections"][0]["parameters"]
        inst_ids = [p["instance_id"] for p in params_meta]
        
        # Find option UUID for opt1
        p3_meta = next(p for p in params_meta if p["parameter_id"] == p3)
        snapshot = p3_meta.get("parameter_snapshot", {})
        options = snapshot.get("options", [])
        opt1_uuid = next((o["option_id"] for o in options if o["code"] == "opt1"), None)
        
        if not opt1_uuid:
            print(f"{RED}Could not find option UUID for opt1{RESET}")
            return

        # Submit Responses
        resp_ids = []
        # 1. Numeric
        r1 = session.post(f"{BASE_URL}/farm-audit/audits/{audit_id}/responses/", json={"audit_parameter_instance_id": inst_ids[0], "response_numeric": 50.5}, headers=fsp_headers, timeout=TIMEOUT).json()["data"]["id"]
        # 2. Text
        r2 = session.post(f"{BASE_URL}/farm-audit/audits/{audit_id}/responses/", json={"audit_parameter_instance_id": inst_ids[1], "response_text": "Good condition"}, headers=fsp_headers, timeout=TIMEOUT).json()["data"]["id"]
        # 3. Select
        r3 = session.post(f"{BASE_URL}/farm-audit/audits/{audit_id}/responses/", json={"audit_parameter_instance_id": inst_ids[2], "response_options": [opt1_uuid]}, headers=fsp_headers, timeout=TIMEOUT).json()["data"]["id"]
        resp_ids = [r1, r2, r3]

        print_step("5. Review & Flagging")
        # Flag all three for the report
        for rid in resp_ids:
            session.post(f"{BASE_URL}/farm-audit/audits/{audit_id}/reviews/", json={"audit_response_id": rid, "is_flagged_for_report": True}, headers=fsp_headers, timeout=TIMEOUT)
        
        # Add standalone recommendation
        session.post(f"{BASE_URL}/farm-audit/audits/{audit_id}/recommendations/", json={"category": "CROP", "title": "Buy Seeds", "description": "High yield seeds"}, headers=fsp_headers, timeout=TIMEOUT)
        
        print_step("6. Workflow Transitions")
        # DRAFT -> SUBMITTED_FOR_REVIEW
        print("Transitioning: DRAFT -> SUBMITTED_FOR_REVIEW")
        resp = session.post(f"{BASE_URL}/farm-audit/audits/{audit_id}/transition/", json={"to_status": "SUBMITTED_FOR_REVIEW"}, headers=fsp_headers, timeout=TIMEOUT)
        if resp.status_code != 200:
            print(f"{RED}Failed to move to SUBMITTED_FOR_REVIEW: {resp.text}{RESET}")
            return

        # SUBMITTED_FOR_REVIEW -> REVIEWED
        print("Transitioning: SUBMITTED_FOR_REVIEW -> REVIEWED")
        resp = session.post(f"{BASE_URL}/farm-audit/audits/{audit_id}/transition/", json={"to_status": "REVIEWED"}, headers=fsp_headers, timeout=TIMEOUT)
        if resp.status_code != 200:
            print(f"{RED}Failed to move to REVIEWED: {resp.text}{RESET}")
            return

        print_step("7. TESTING HANG FIX: FINALIZING REPORT")
        t0 = time.time()
        final_resp = session.post(f"{BASE_URL}/farm-audit/audits/{audit_id}/transition/", json={"to_status": "FINALIZED"}, headers=fsp_headers, timeout=TIMEOUT)
        duration = time.time() - t0
        
        if final_resp.status_code == 200:
            print(f"{GREEN}✓ Audit Finalized in {duration:.2f}s (No Hang!){RESET}")
            audit_data = final_resp.json()["data"]
            print(f"✓ Metadata: Status={audit_data['status']}, FinalizedAt={audit_data.get('finalized_at')}")
        else:
            print(f"{RED}✗ Finalization failed with {final_resp.status_code}: {final_resp.text}{RESET}")
            return

        print_step("8. VERIFYING FARMER REPORT (Actual Values)")
        # Switch to farmer to see if they can see it (or just use FSP headers if common endpoint)
        report_resp = session.get(f"{BASE_URL}/farm-audit/audits/{audit_id}/report/", headers=fsp_headers, timeout=TIMEOUT)
        report = report_resp.json()["data"]
        
        flagged = report.get("flagged_responses", [])
        print(f"Verifying {len(flagged)} flagged responses:")
        
        success = True
        for item in flagged:
            val = item['original_response']
            print(f"   - {item['parameter_name']}: {val}")
            if val in [None, "None", "N/A", "Selection"]:
                print(f"{RED}   ✗ Invalid value detected: {val}{RESET}")
                success = False
        
        recs = report.get("standalone_recommendations", [])
        if len(recs) >= 1:
            print(f"{GREEN}✓ Recommendation received: {recs[0]['title']}{RESET}")
        else:
            print(f"{RED}✗ No recommendation in report!{RESET}")
            success = False
            
        if success:
            print(f"\n{GREEN}★★★ ALL TESTS PASSED ★★★{RESET}")
        else:
            print(f"\n{RED}★★★ SOME TESTS FAILED ★★★{RESET}")

    except Exception as e:
        print(f"\n{RED}✗ Unexpected Error: {str(e)}{RESET}")

if __name__ == "__main__":
    verify_flow()
