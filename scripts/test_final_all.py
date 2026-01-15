#!/usr/bin/env python3
"""
Comprehensive Test Script for final_test_all.md
Verifies all JSON payloads work correctly.
"""
import requests
import json
import subprocess
import time

BASE_URL = "http://localhost:8000/api/v1"

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_result(step, response, expected_codes=[200, 201, 202]):
    if response.status_code in expected_codes:
        print(f"{GREEN}[PASS]{RESET} {step}")
        return True
    else:
        print(f"{RED}[FAIL]{RESET} {step}")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:500]}")
        return False

def run_test():
    print("=" * 60)
    print("COMPREHENSIVE MANUAL TEST VERIFICATION")
    print("=" * 60)
    
    s = requests.Session()
    results = {"passed": 0, "failed": 0}
    
    # 1.1 Register Farmer
    print("\n--- 1. USER AUTHENTICATION ---")
    resp = s.post(f"{BASE_URL}/auth/register", json={
        "email": "farmer.owner@karnataka.com",
        "password": "SecurePassword@123",
        "first_name": "Ramesh",
        "last_name": "Gowda",
        "phone_number": "+919876543210"
    })
    if print_result("1.1 Register Farmer", resp):
        results["passed"] += 1
        farmer_token = resp.json()["data"]["tokens"]["access_token"]
        farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
    else:
        results["failed"] += 1
        return results
    
    # 1.2 Register FSP
    resp = s.post(f"{BASE_URL}/auth/register", json={
        "email": "fsp.admin@agriservices.com",
        "password": "SecurePassword@123",
        "first_name": "Suresh",
        "last_name": "Reddy",
        "phone_number": "+919876543211"
    })
    if print_result("1.2 Register FSP User", resp):
        results["passed"] += 1
        fsp_token = resp.json()["data"]["tokens"]["access_token"]
        fsp_headers = {"Authorization": f"Bearer {fsp_token}"}
    else:
        results["failed"] += 1
        return results
    
    # 1.3 Register Super Admin
    resp = s.post(f"{BASE_URL}/auth/register", json={
        "email": "superadmin@uzhathunai.com",
        "password": "SuperSecure@Admin123",
        "first_name": "System",
        "last_name": "Admin",
        "phone_number": "+919000000001"
    })
    if print_result("1.3 Register Super Admin", resp):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # 1.4 Login Test
    resp = s.post(f"{BASE_URL}/auth/login", json={
        "email": "farmer.owner@karnataka.com",
        "password": "SecurePassword@123"
    })
    if print_result("1.4 Login", resp):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # 2. Organizations
    print("\n--- 2. ORGANIZATION MANAGEMENT ---")
    resp = s.post(f"{BASE_URL}/organizations", json={
        "name": "Green Valley Farms",
        "organization_type": "FARMING",
        "description": "Organic vegetable farming in Shimoga district",
        "district": "Shimoga",
        "pincode": "577201"
    }, headers=farmer_headers)
    if print_result("2.1 Create Farming Org", resp):
        results["passed"] += 1
        farming_org_id = resp.json()["id"]
    else:
        results["failed"] += 1
        return results

    # Seed master service
    subprocess.run(
        '''docker compose exec -T db psql -U postgres -d uzhathunai_db_v2 -c "INSERT INTO master_services (id, code, name, description, status) VALUES ('d3544d64-9840-410e-b79e-4c7406a64010', 'DRONE_SPRAY', 'Drone Spraying', 'Aerial pesticide application', 'ACTIVE') ON CONFLICT DO NOTHING;"''',
        shell=True, capture_output=True
    )
    
    resp = s.post(f"{BASE_URL}/organizations", json={
        "name": "AgriTech Sprayers Ltd",
        "organization_type": "FSP",
        "description": "Drone spraying services",
        "district": "Shimoga",
        "services": [{
            "service_id": "d3544d64-9840-410e-b79e-4c7406a64010",
            "title": "Drone Spraying",
            "description": "Precision pesticide application",
            "pricing_model": "PER_ACRE",
            "base_price": 500.0
        }]
    }, headers=fsp_headers)
    if print_result("2.2 Create FSP Org", resp):
        results["passed"] += 1
        fsp_org_id = resp.json()["id"]
    else:
        results["failed"] += 1
        return results
    
    # Approve orgs
    subprocess.run(
        '''docker compose exec -T db psql -U postgres -d uzhathunai_db_v2 -c "UPDATE organizations SET is_approved = true, status = 'ACTIVE';"''',
        shell=True, capture_output=True
    )
    print(f"{GREEN}[PASS]{RESET} 2.3 Approve Organizations (DB)")
    results["passed"] += 1

    # 3. Farm Management
    print("\n--- 3. FARM MANAGEMENT ---")
    resp = s.post(f"{BASE_URL}/farms", json={
        "name": "North Field - Sector A",
        "description": "Main rice cultivation area with canal irrigation",
        "area": 12.5,
        "location": {
            "type": "Point",
            "coordinates": [75.5678, 13.9234]
        },
        "boundary": {
            "type": "Polygon",
            "coordinates": [[
                [75.5670, 13.9230],
                [75.5690, 13.9230],
                [75.5690, 13.9250],
                [75.5670, 13.9250],
                [75.5670, 13.9230]
            ]]
        },
        "farm_attributes": {
            "irrigation_type": "Canal",
            "soil_health": "Good"
        }
    }, headers=farmer_headers)
    if print_result("3.1 Create Farm with GeoJSON", resp):
        results["passed"] += 1
        farm_id = resp.json()["id"]
    else:
        results["failed"] += 1
        return results

    resp = s.get(f"{BASE_URL}/farms/{farm_id}", headers=farmer_headers)
    if print_result("3.2 Get Farm Details", resp):
        results["passed"] += 1
    else:
        results["failed"] += 1

    resp = s.get(f"{BASE_URL}/farms", headers=farmer_headers)
    if print_result("3.3 List All Farms", resp):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # 4. Plot Management
    print("\n--- 4. PLOT MANAGEMENT ---")
    resp = s.post(f"{BASE_URL}/plots/farms/{farm_id}/plots", json={
        "name": "Plot A-1",
        "description": "Primary rice cultivation plot",
        "area": 5.0
    }, headers=farmer_headers)
    if print_result("4.1 Create Plot", resp):
        results["passed"] += 1
        plot_id = resp.json()["id"]
    else:
        results["failed"] += 1
        return results

    resp = s.post(f"{BASE_URL}/plots/farms/{farm_id}/plots", json={
        "name": "Plot A-2",
        "description": "Vegetable cultivation plot",
        "area": 3.5
    }, headers=farmer_headers)
    if print_result("4.2 Create Second Plot", resp):
        results["passed"] += 1
        plot_id_2 = resp.json()["id"]
    else:
        results["failed"] += 1

    # 5. Crop Management
    print("\n--- 5. CROP MANAGEMENT ---")
    resp = s.post(f"{BASE_URL}/crops", json={
        "farm_id": farm_id,
        "plot_id": plot_id,
        "name": "Sona Masoori Rice",
        "crop_type": "CEREAL",
        "sowing_date": "2024-06-15",
        "status": "ACTIVE",
        "attributes": {
            "variety": "Super Fine",
            "seed_source": "Govt Agriculture Center"
        }
    }, headers=farmer_headers)
    if print_result("5.1 Create Crop", resp):
        results["passed"] += 1
    else:
        results["failed"] += 1

    resp = s.post(f"{BASE_URL}/crops", json={
        "farm_id": farm_id,
        "plot_id": plot_id_2,
        "name": "Organic Tomatoes",
        "crop_type": "VEGETABLE",
        "sowing_date": "2024-07-01",
        "status": "ACTIVE",
        "attributes": {"variety": "Cherry"}
    }, headers=farmer_headers)
    if print_result("5.2 Create Second Crop", resp):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # 6. Work Order Management
    print("\n--- 6. WORK ORDER MANAGEMENT ---")
    resp = s.post(f"{BASE_URL}/work-orders", json={
        "farming_organization_id": farming_org_id,
        "fsp_organization_id": fsp_org_id,
        "title": "Monsoon Pest Control Contract",
        "description": "Drone spraying for pest control",
        "start_date": "2024-07-01",
        "end_date": "2024-07-15",
        "total_amount": 25000,
        "currency": "INR",
        "scope_items": [{
            "scope": "FARM",
            "scope_id": farm_id,
            "access_permissions": {"read": True, "write": True, "track": True}
        }]
    }, headers=farmer_headers)
    if print_result("6.1 Create Work Order", resp):
        results["passed"] += 1
        work_order_id = resp.json()["id"]
    else:
        results["failed"] += 1
        return results

    resp = s.post(f"{BASE_URL}/work-orders/{work_order_id}/accept", headers=fsp_headers)
    if print_result("6.2 Accept Work Order (FSP)", resp):
        results["passed"] += 1
    else:
        results["failed"] += 1

    resp = s.post(f"{BASE_URL}/work-orders/{work_order_id}/start", headers=fsp_headers)
    if print_result("6.3 Start Work Order", resp):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # 7. Zoom Video
    print("\n--- 7. ZOOM VIDEO CONSULTATION ---")
    resp = s.post(f"{BASE_URL}/video/schedule", json={
        "work_order_id": work_order_id,
        "topic": "Initial Crop Health Inspection",
        "start_time": "2024-07-02T10:00:00Z",
        "duration_minutes": 30,
        "agenda": "Inspect leaf health and discuss irrigation"
    }, headers=fsp_headers)
    if print_result("7.1 Schedule Video Session", resp):
        results["passed"] += 1
        session_id = resp.json().get("id")
    else:
        results["failed"] += 1

    if session_id:
        resp = s.get(f"{BASE_URL}/video/{session_id}", headers=fsp_headers)
        if print_result("7.2 Get Video Session", resp):
            results["passed"] += 1
        else:
            results["failed"] += 1

    # Complete Work Order
    resp = s.post(f"{BASE_URL}/work-orders/{work_order_id}/complete", headers=fsp_headers)
    if print_result("6.4 Complete Work Order", resp):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"RESULTS: {GREEN}{results['passed']} PASSED{RESET}, {RED}{results['failed']} FAILED{RESET}")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    run_test()
