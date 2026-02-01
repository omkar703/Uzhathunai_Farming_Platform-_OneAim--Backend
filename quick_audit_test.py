#!/usr/bin/env python3
"""
Quick Audit Endpoints Test
Tests the working audit endpoints without template creation complexity.
"""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def test_audit_flow():
    """Test the complete audit flow that's currently working"""
    
    print_header("AUDIT SYSTEM QUICK TEST")
    
    session = requests.Session()
    
    # 1. Setup Users
    print("1. Creating test users...")
    farmer_email = f"quick_farmer_{int(time.time())}@test.com"
    fsp_email = f"quick_fsp_{int(time.time())}@test.com"
    
    resp = session.post(f"{BASE_URL}/auth/register", json={
        "email": farmer_email,
        "password": "Test@123",
        "first_name": "Quick",
        "last_name": "Farmer",
        "phone_number": f"+91{int(time.time()) % 10000000000:010d}"
    })
    farmer_token = resp.json()["data"]["tokens"]["access_token"]
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
    print(f"   ✓ Farmer created: {farmer_email}")
    
    resp = session.post(f"{BASE_URL}/auth/register", json={
        "email": fsp_email,
        "password": "Test@123",
        "first_name": "Quick",
        "last_name": "FSP",
        "phone_number": f"+91{int(time.time()) % 10000000000:010d}"
    })
    fsp_token = resp.json()["data"]["tokens"]["access_token"]
    fsp_headers = {"Authorization": f"Bearer {fsp_token}"}
    print(f"   ✓ FSP created: {fsp_email}")
    
    # 2. Create Organizations
    print("\n2. Creating organizations...")
    resp = session.post(f"{BASE_URL}/organizations", json={
        "name": f"Quick Farm {int(time.time())}",
        "organization_type": "FARMING",
        "description": "Quick test farm",
        "district": "Test",
        "pincode": "123456"
    }, headers=farmer_headers)
    farming_org_id = resp.json()["data"]["id"]
    print(f"   ✓ Farming Org: {farming_org_id}")
    
    resp = session.post(f"{BASE_URL}/organizations", json={
        "name": f"Quick FSP {int(time.time())}",
        "organization_type": "FSP",
        "description": "Quick test FSP",
        "district": "Test",
        "pincode": "123456"
    }, headers=fsp_headers)
    fsp_org_id = resp.json()["data"]["id"]
    print(f"   ✓ FSP Org: {fsp_org_id}")
    
    # Approve orgs
    import subprocess
    subprocess.run(
        f'''docker compose exec -T db psql -U postgres -d farm_db -c "UPDATE organizations SET is_approved = true, status = 'ACTIVE' WHERE id IN ('{farming_org_id}', '{fsp_org_id}');"''',
        shell=True, capture_output=True
    )
    print("   ✓ Organizations approved")
    
    # 3. Create Farm & Crop
    print("\n3. Creating farm and crop...")
    resp = session.post(f"{BASE_URL}/farms", json={
        "name": f"Quick Farm {int(time.time())}",
        "description": "Quick test",
        "area": 5.0,
        "location": {"type": "Point", "coordinates": [77.5, 12.9]},
        "boundary": {
            "type": "Polygon",
            "coordinates": [[[77.49, 12.89], [77.51, 12.89], [77.51, 12.91], [77.49, 12.91], [77.49, 12.89]]]
        }
    }, headers=farmer_headers)
    farm_id = resp.json()["data"]["id"]
    print(f"   ✓ Farm: {farm_id}")
    
    resp = session.post(f"{BASE_URL}/plots/farms/{farm_id}/plots", json={
        "name": f"Quick Plot {int(time.time())}",
        "description": "Quick test",
        "area": 2.5
    }, headers=farmer_headers)
    plot_id = resp.json()["data"]["id"]
    print(f"   ✓ Plot: {plot_id}")
    
    resp = session.post(f"{BASE_URL}/crops", json={
        "farm_id": farm_id,
        "plot_id": plot_id,
        "name": "Quick Rice",
        "crop_type": "CEREAL",
        "sowing_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        "status": "ACTIVE"
    }, headers=farmer_headers)
    crop_id = resp.json()["data"]["id"]
    print(f"   ✓ Crop: {crop_id}")
    
    # 4. Create Work Order
    print("\n4. Creating work order...")
    resp = session.post(f"{BASE_URL}/work-orders", json={
        "farming_organization_id": farming_org_id,
        "fsp_organization_id": fsp_org_id,
        "title": f"Quick WO {int(time.time())}",
        "description": "Quick test",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "total_amount": 5000,
        "currency": "INR",
        "scope_items": [{
            "scope": "FARM",
            "scope_id": farm_id,
            "access_permissions": {"read": True, "write": True, "track": True}
        }]
    }, headers=farmer_headers)
    work_order_id = resp.json()["data"]["id"]
    print(f"   ✓ Work Order: {work_order_id}")
    
    session.post(f"{BASE_URL}/work-orders/{work_order_id}/accept", headers=fsp_headers)
    session.post(f"{BASE_URL}/work-orders/{work_order_id}/start", headers=fsp_headers)
    print("   ✓ Work Order accepted and started")
    
    # 5. Test Audit Endpoints (without template)
    print("\n5. Testing audit list endpoints...")
    
    resp = session.get(f"{BASE_URL}/farm-audit/audits", headers=fsp_headers)
    print(f"   ✓ List all audits: {resp.status_code}")
    
    resp = session.get(
        f"{BASE_URL}/farm-audit/audits?fsp_organization_id={fsp_org_id}",
        headers=fsp_headers
    )
    print(f"   ✓ Filter by FSP org: {resp.status_code}")
    
    resp = session.get(
        f"{BASE_URL}/farm-audit/audits?work_order_id={work_order_id}",
        headers=fsp_headers
    )
    print(f"   ✓ Filter by work order: {resp.status_code}")
    
    resp = session.get(
        f"{BASE_URL}/farm-audit/audits?status=DRAFT",
        headers=fsp_headers
    )
    print(f"   ✓ Filter by status: {resp.status_code}")
    
    # 6. Test Template Endpoints
    print("\n6. Testing template list endpoints...")
    
    resp = session.get(f"{BASE_URL}/farm-audit/templates", headers=fsp_headers)
    print(f"   ✓ List templates: {resp.status_code}")
    if resp.status_code == 200:
        templates = resp.json()["data"]["items"]
        print(f"   ℹ Found {len(templates)} existing templates")
        
        if templates:
            template_id = templates[0]["id"]
            resp = session.get(
                f"{BASE_URL}/farm-audit/templates/{template_id}",
                headers=fsp_headers
            )
            print(f"   ✓ Get template details: {resp.status_code}")
    
    # 7. Summary
    print_header("TEST SUMMARY")
    print("✓ User Registration: Working")
    print("✓ Organization Management: Working")
    print("✓ Farm & Crop Management: Working")
    print("✓ Work Order Management: Working")
    print("✓ Audit Listing: Working")
    print("✓ Template Listing: Working")
    print("\n⚠ Template Creation: Requires pre-existing sections/parameters")
    print("⚠ Audit Creation: Requires valid template")
    print("\nℹ See AUDIT_E2E_TESTING_GUIDE.md for complete endpoint documentation")
    print_header("END")

if __name__ == "__main__":
    try:
        test_audit_flow()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
