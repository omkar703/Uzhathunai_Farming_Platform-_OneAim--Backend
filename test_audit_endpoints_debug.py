#!/usr/bin/env python3
"""
Audit Endpoints Debugging Script
Tests and debugs all audit-related endpoints with detailed error reporting.
"""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_test(name, passed, details=""):
    """Print test result"""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} | {name}")
    if details:
        print(f"       {details}")


def test_endpoint(method, url, headers=None, json_data=None, expected_codes=[200, 201]):
    """Test an endpoint and return response"""
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=json_data, timeout=10)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, json=json_data, timeout=10)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=10)
        
        success = resp.status_code in expected_codes
        
        if not success:
            try:
                error = resp.json()
                details = f"Status: {resp.status_code}, Error: {json.dumps(error, indent=2)[:200]}"
            except:
                details = f"Status: {resp.status_code}, Response: {resp.text[:200]}"
        else:
            details = f"Status: {resp.status_code}"
        
        return success, resp, details
    except Exception as e:
        return False, None, f"Exception: {str(e)}"


def main():
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}AUDIT ENDPOINTS DEBUGGING SCRIPT{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")
    
    session = requests.Session()
    
    # Step 1: Register and login users
    print(f"\n{YELLOW}=== STEP 1: USER AUTHENTICATION ==={RESET}\n")
    
    farmer_email = f"debug_farmer_{int(time.time())}@test.com"
    fsp_email = f"debug_fsp_{int(time.time())}@test.com"
    
    # Register Farmer
    success, resp, details = test_endpoint(
        "POST", f"{BASE_URL}/auth/register",
        json_data={
            "email": farmer_email,
            "password": "Test@123",
            "first_name": "Test",
            "last_name": "Farmer",
            "phone_number": f"+91{int(time.time()) % 10000000000:010d}"
        }
    )
    print_test("Register Farmer", success, details)
    
    if success:
        farmer_token = resp.json()["data"]["tokens"]["access_token"]
        farmer_headers = {"Authorization": f"Bearer {farmer_token}"}
        print(f"       Farmer Token: {farmer_token[:30]}...")
    else:
        print(f"{RED}Cannot proceed without farmer authentication{RESET}")
        return
    
    # Register FSP
    success, resp, details = test_endpoint(
        "POST", f"{BASE_URL}/auth/register",
        json_data={
            "email": fsp_email,
            "password": "Test@123",
            "first_name": "Test",
            "last_name": "FSP",
            "phone_number": f"+91{int(time.time()) % 10000000000:010d}"
        }
    )
    print_test("Register FSP", success, details)
    
    if success:
        fsp_token = resp.json()["data"]["tokens"]["access_token"]
        fsp_headers = {"Authorization": f"Bearer {fsp_token}"}
        print(f"       FSP Token: {fsp_token[:30]}...")
    else:
        print(f"{RED}Cannot proceed without FSP authentication{RESET}")
        return
    
    # Step 2: Create Organizations
    print(f"\n{YELLOW}=== STEP 2: ORGANIZATION CREATION ==={RESET}\n")
    
    success, resp, details = test_endpoint(
        "POST", f"{BASE_URL}/organizations",
        headers=farmer_headers,
        json_data={
            "name": f"Debug Farm Org {int(time.time())}",
            "organization_type": "FARMING",
            "description": "Debug farming org",
            "district": "Test District",
            "pincode": "123456"
        }
    )
    print_test("Create Farming Org", success, details)
    
    if success:
        try:
            farming_org_id = resp.json()["id"]
            print(f"       Farming Org ID: {farming_org_id}")
        except KeyError:
            print(f"       {YELLOW}Response structure: {json.dumps(resp.json(), indent=2)[:300]}{RESET}")
            # Try alternate keys
            data = resp.json()
            if "data" in data and "id" in data["data"]:
                farming_org_id = data["data"]["id"]
                print(f"       Farming Org ID (from data): {farming_org_id}")
            else:
                print(f"{RED}Cannot find org ID in response{RESET}")
                return
    else:
        return
    
    success, resp, details = test_endpoint(
        "POST", f"{BASE_URL}/organizations",
        headers=fsp_headers,
        json_data={
            "name": f"Debug FSP Org {int(time.time())}",
            "organization_type": "FSP",
            "description": "Debug FSP org",
            "district": "Test District",
            "pincode": "123456"
        }
    )
    print_test("Create FSP Org", success, details)
    
    if success:
        try:
            fsp_org_id = resp.json()["id"]
            print(f"       FSP Org ID: {fsp_org_id}")
        except KeyError:
            data = resp.json()
            if "data" in data and "id" in data["data"]:
                fsp_org_id = data["data"]["id"]
                print(f"       FSP Org ID (from data): {fsp_org_id}")
            else:
                print(f"{RED}Cannot find org ID in response{RESET}")
                return
    else:
        return
    
    # Approve orgs
    import subprocess
    result = subprocess.run(
        f'''docker compose exec -T db psql -U postgres -d farm_db -c "UPDATE organizations SET is_approved = true, status = 'ACTIVE' WHERE id IN ('{farming_org_id}', '{fsp_org_id}');"''',
        shell=True, capture_output=True, text=True
    )
    print_test("Approve Organizations", result.returncode == 0, f"DB Update: {result.stdout[:100]}")
    
    # Step 3: Create Farm and Crop
    print(f"\n{YELLOW}=== STEP 3: FARM & CROP CREATION ==={RESET}\n")
    
    success, resp, details = test_endpoint(
        "POST", f"{BASE_URL}/farms",
        headers=farmer_headers,
        json_data={
            "name": f"Debug Farm {int(time.time())}",
            "description": "Debug farm",
            "area": 5.0,
            "location": {"type": "Point", "coordinates": [77.5, 12.9]},
            "boundary": {
                "type": "Polygon",
                "coordinates": [[[77.49, 12.89], [77.51, 12.89], [77.51, 12.91], [77.49, 12.91], [77.49, 12.89]]]
            }
        }
    )
    print_test("Create Farm", success, details)
    
    if success:
        try:
            farm_id = resp.json()["id"]
            print(f"       Farm ID: {farm_id}")
        except KeyError:
            data = resp.json()
            if "data" in data and "id" in data["data"]:
                farm_id = data["data"]["id"]
            else:
                print(f"{RED}Cannot find farm ID{RESET}")
                return
    else:
        return
    
    # Create Plot
    success, resp, details = test_endpoint(
        "POST", f"{BASE_URL}/plots/farms/{farm_id}/plots",
        headers=farmer_headers,
        json_data={
            "name": f"Debug Plot {int(time.time())}",
            "description": "Debug plot",
            "area": 2.5
        }
    )
    print_test("Create Plot", success, details)
    
    if success:
        try:
            plot_id = resp.json()["id"]
            print(f"       Plot ID: {plot_id}")
        except KeyError:
            data = resp.json()
            if "data" in data and "id" in data["data"]:
                plot_id = data["data"]["id"]
            else:
                print(f"{RED}Cannot find plot ID{RESET}")
                return
    else:
        return
    
    # Create Crop
    success, resp, details = test_endpoint(
        "POST", f"{BASE_URL}/crops",
        headers=farmer_headers,
        json_data={
            "farm_id": farm_id,
            "plot_id": plot_id,
            "name": "Debug Rice",
            "crop_type": "CEREAL",
            "sowing_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "status": "ACTIVE"
        }
    )
    print_test("Create Crop", success, details)
    
    if success:
        try:
            crop_id = resp.json()["id"]
            print(f"       Crop ID: {crop_id}")
        except KeyError:
            data = resp.json()
            if "data" in data and "id" in data["data"]:
                crop_id = data["data"]["id"]
            else:
                print(f"{RED}Cannot find crop ID{RESET}")
                return
    else:
        return
    
    # Step 4: Create Work Order
    print(f"\n{YELLOW}=== STEP 4: WORK ORDER CREATION ==={RESET}\n")
    
    success, resp, details = test_endpoint(
        "POST", f"{BASE_URL}/work-orders",
        headers=farmer_headers,
        json_data={
            "farming_organization_id": farming_org_id,
            "fsp_organization_id": fsp_org_id,
            "title": f"Debug Work Order {int(time.time())}",
            "description": "Debug work order",
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "total_amount": 5000,
            "currency": "INR",
            "scope_items": [{
                "scope": "FARM",
                "scope_id": farm_id,
                "access_permissions": {"read": True, "write": True, "track": True}
            }]
        }
    )
    print_test("Create Work Order", success, details)
    
    if success:
        try:
            work_order_id = resp.json()["id"]
            print(f"       Work Order ID: {work_order_id}")
        except KeyError:
            data = resp.json()
            if "data" in data and "id" in data["data"]:
                work_order_id = data["data"]["id"]
            else:
                print(f"{RED}Cannot find work order ID{RESET}")
                return
    else:
        return
    
    # Accept and Start Work Order
    success, resp, details = test_endpoint(
        "POST", f"{BASE_URL}/work-orders/{work_order_id}/accept",
        headers=fsp_headers
    )
    print_test("Accept Work Order", success, details)
    
    success, resp, details = test_endpoint(
        "POST", f"{BASE_URL}/work-orders/{work_order_id}/start",
        headers=fsp_headers
    )
    print_test("Start Work Order", success, details)
    
    # Step 5: Test Audit Template Endpoints
    print(f"\n{YELLOW}=== STEP 5: AUDIT TEMPLATE ENDPOINTS ==={RESET}\n")
    
    success, resp, details = test_endpoint(
        "POST", f"{BASE_URL}/farm-audit/templates",
        headers=fsp_headers,
        json_data={
            "name": f"Debug Template {int(time.time())}",
            "description": "Debug audit template",
            "version": "1.0",
            "crop_types": ["CEREAL"],
            "sections": [{
                "name": "Test Section",
                "description": "Test section desc",
                "display_order": 1,
                "parameters": [{
                    "name": "Test Parameter",
                    "description": "Test param",
                    "parameter_type": "NUMERIC",
                    "display_order": 1,
                    "is_required": True,
                    "parameter_metadata": {"min_value": 0, "max_value": 100}
                }]
            }]
        }
    )
    print_test("Create Audit Template", success, details)
    
    if success:
        template_id = resp.json()["data"]["id"]
        print(f"       Template ID: {template_id}")
    else:
        print(f"{RED}Cannot proceed without template{RESET}")
        return
    
    # List Templates
    success, resp, details = test_endpoint(
        "GET", f"{BASE_URL}/farm-audit/templates",
        headers=fsp_headers
    )
    print_test("List Templates", success, details)
    
    # Get Template Details
    success, resp, details = test_endpoint(
        "GET", f"{BASE_URL}/farm-audit/templates/{template_id}",
        headers=fsp_headers
    )
    print_test("Get Template Details", success, details)
    
    # Step 6: Test Audit Endpoints
    print(f"\n{YELLOW}=== STEP 6: AUDIT CREATION & MANAGEMENT ==={RESET}\n")
    
    success, resp, details = test_endpoint(
        "POST", f"{BASE_URL}/farm-audit/audits",
        headers=fsp_headers,
        json_data={
            "template_id": template_id,
            "crop_id": crop_id,
            "fsp_organization_id": fsp_org_id,
            "name": f"Debug Audit {int(time.time())}",
            "work_order_id": work_order_id,
            "audit_date": datetime.now().strftime("%Y-%m-%d")
        }
    )
    print_test("Create Audit", success, details)
    
    if success:
        audit_id = resp.json()["data"]["id"]
        print(f"       Audit ID: {audit_id}")
    else:
        print(f"{RED}Cannot proceed without audit{RESET}")
        return
    
    # Get Audit
    success, resp, details = test_endpoint(
        "GET", f"{BASE_URL}/farm-audit/audits/{audit_id}",
        headers=fsp_headers
    )
    print_test("Get Audit Details", success, details)
    
    # List Audits
    success, resp, details = test_endpoint(
        "GET", f"{BASE_URL}/farm-audit/audits",
        headers=fsp_headers
    )
    print_test("List Audits", success, details)
    
    # Get Audit Structure
    success, resp, details = test_endpoint(
        "GET", f"{BASE_URL}/farm-audit/audits/{audit_id}/structure",
        headers=fsp_headers
    )
    print_test("Get Audit Structure", success, details)
    
    if success:
        structure = resp.json()["data"]
        print(f"       Sections: {len(structure.get('sections', []))}")
        
        # Get parameter instance ID
        param_instance_id = None
        for section in structure.get('sections', []):
            for param in section.get('parameters', []):
                param_instance_id = param['id']
                print(f"       Parameter Instance ID: {param_instance_id}")
                break
            if param_instance_id:
                break
    else:
        return
    
    # Step 7: Test Response Endpoints
    print(f"\n{YELLOW}=== STEP 7: AUDIT RESPONSE ENDPOINTS ==={RESET}\n")
    
    if param_instance_id:
        # Submit Response
        success, resp, details = test_endpoint(
            "POST", f"{BASE_URL}/farm-audit/audits/{audit_id}/responses",
            headers=fsp_headers,
            json_data={
                "audit_parameter_instance_id": param_instance_id,
                "response_numeric": 50.5
            }
        )
        print_test("Submit Response", success, details)
        
        if success:
            response_id = resp.json()["data"]["id"]
            print(f"       Response ID: {response_id}")
        else:
            response_id = None
        
        # Bulk Submit
        success, resp, details = test_endpoint(
            "POST", f"{BASE_URL}/farm-audit/audits/{audit_id}/responses/save",
            headers=fsp_headers,
            json_data=[{
                "audit_parameter_instance_id": param_instance_id,
                "response_numeric": 75.0
            }]
        )
        print_test("Bulk Submit Responses", success, details)
        
        # Get Responses
        success, resp, details = test_endpoint(
            "GET", f"{BASE_URL}/farm-audit/audits/{audit_id}/responses",
            headers=fsp_headers
        )
        print_test("Get Audit Responses", success, details)
        
        # Update Response
        if response_id:
            success, resp, details = test_endpoint(
                "PUT", f"{BASE_URL}/farm-audit/audits/{audit_id}/responses/{response_id}",
                headers=fsp_headers,
                json_data={"response_numeric": 60.0}
            )
            print_test("Update Response", success, details)
    
    # Step 8: Test Status Transitions
    print(f"\n{YELLOW}=== STEP 8: AUDIT STATUS TRANSITIONS ==={RESET}\n")
    
    # Validate
    success, resp, details = test_endpoint(
        "GET", f"{BASE_URL}/farm-audit/audits/{audit_id}/validation",
        headers=fsp_headers
    )
    print_test("Validate Audit", success, details)
    
    # Transition to IN_PROGRESS
    success, resp, details = test_endpoint(
        "POST", f"{BASE_URL}/farm-audit/audits/{audit_id}/transition",
        headers=fsp_headers,
        json_data={"to_status": "IN_PROGRESS"}
    )
    print_test("Transition to IN_PROGRESS", success, details)
    
    # Step 9: Test Issue Endpoints
    print(f"\n{YELLOW}=== STEP 9: ISSUE MANAGEMENT ==={RESET}\n")
    
    success, resp, details = test_endpoint(
        "POST", f"{BASE_URL}/farm-audit/audits/{audit_id}/issues",
        headers=fsp_headers,
        json_data={
            "title": "Test Issue",
            "description": "Test issue description",
            "severity": "MEDIUM"
        }
    )
    print_test("Create Issue", success, details)
    
    if success:
        issue_id = resp.json()["data"]["id"]
        print(f"       Issue ID: {issue_id}")
    else:
        issue_id = None
    
    # List Issues
    success, resp, details = test_endpoint(
        "GET", f"{BASE_URL}/farm-audit/audits/{audit_id}/issues",
        headers=fsp_headers
    )
    print_test("List Issues", success, details)
    
    # Update Issue
    if issue_id:
        success, resp, details = test_endpoint(
            "PUT", f"{BASE_URL}/farm-audit/audits/{audit_id}/issues/{issue_id}",
            headers=fsp_headers,
            json_data={"severity": "HIGH"}
        )
        print_test("Update Issue", success, details)
    
    # Step 10: Test Recommendations
    print(f"\n{YELLOW}=== STEP 10: RECOMMENDATIONS ==={RESET}\n")
    
    success, resp, details = test_endpoint(
        "GET", f"{BASE_URL}/farm-audit/audits/{audit_id}/recommendations",
        headers=fsp_headers
    )
    print_test("List Recommendations", success, details)
    
    # Step 11: Cleanup
    print(f"\n{YELLOW}=== STEP 11: CLEANUP ==={RESET}\n")
    
    # Delete Issue
    if issue_id:
        success, resp, details = test_endpoint(
            "DELETE", f"{BASE_URL}/farm-audit/audits/{audit_id}/issues/{issue_id}",
            headers=fsp_headers,
            expected_codes=[200, 204]
        )
        print_test("Delete Issue", success, details)
    
    # Delete Audit
    success, resp, details = test_endpoint(
        "DELETE", f"{BASE_URL}/farm-audit/audits/{audit_id}",
        headers=fsp_headers,
        expected_codes=[200, 204]
    )
    print_test("Delete Audit", success, details)
    
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}DEBUGGING COMPLETE{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")


if __name__ == "__main__":
    main()
