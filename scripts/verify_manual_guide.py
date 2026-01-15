
import requests
import json
import time
import subprocess

BASE_URL = "http://localhost:8000/api/v1"

# --- Colors ---
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def print_result(step, response):
    if response.status_code in [200, 201, 202, 204]:
        print(f"{GREEN}[PASS] {step}{RESET}")
        return True
    else:
        print(f"{RED}[FAIL] {step}{RESET}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def run_verification():
    print("--- Starting Manual Guide Verification ---")
    
    # Session to keep connections
    s = requests.Session()

    # 1.1 Register Farmer
    print("\n1.1 Register Farmer")
    farmer_payload = {
      "email": "farmer.owner@karnataka.com",
      "password": "SecurePassword@123",
      "first_name": "Ramesh",
      "last_name": "Gowda",
      "phone_number": "+919876543210"
    }
    resp = s.post(f"{BASE_URL}/auth/register", json=farmer_payload)
    if not print_result("Register Farmer", resp): return
    # Auth response is wrapped in data.tokens
    farmer_token = resp.json()["data"]["tokens"]["access_token"]
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}

    # 1.2 Register FSP
    print("\n1.2 Register FSP")
    fsp_payload = {
      "email": "fsp.admin@agriservices.com",
      "password": "SecurePassword@123",
      "first_name": "Suresh",
      "last_name": "Reddy",
      "phone_number": "+919876543211"
    }
    resp = s.post(f"{BASE_URL}/auth/register", json=fsp_payload)
    if not print_result("Register FSP", resp): return
    # Auth response is wrapped in data.tokens
    fsp_token = resp.json()["data"]["tokens"]["access_token"]
    fsp_headers = {"Authorization": f"Bearer {fsp_token}"}

    # 1.3 Create Farming Org
    print("\n1.3 Create Farming Org")
    farming_org_payload = {
      "name": "Green Valley Farms",
      "organization_type": "FARMING",
      "description": "Organic vegetable farming in Shimoga district",
      "district": "Shimoga",
      "pincode": "577201"
    }
    resp = s.post(f"{BASE_URL}/organizations", json=farming_org_payload, headers=farmer_headers)
    if not print_result("Create Farming Org", resp): return
    farming_org_id = resp.json()["id"]

    # 1.4 Create FSP Org
    print("\n1.4 Create FSP Org")
    # SEED Master Service first
    cmd = """docker compose exec -T db psql -U postgres -d uzhathunai_db_v2 -c "INSERT INTO master_services (id, code, name, description, status) VALUES ('d3544d64-9840-410e-b79e-4c7406a64010', 'DRONE_SPRAY', 'Drone Spraying', 'Aerial pesticide application', 'ACTIVE') ON CONFLICT DO NOTHING;" """
    subprocess.run(cmd, shell=True, check=True)
    
    fsp_org_payload = {
      "name": "AgriTech Sprayers Ltd",
      "organization_type": "FSP",
      "description": "Drone spraying and soil testing services",
      "district": "Shimoga",
      "services": [
        {
          "service_id": "d3544d64-9840-410e-b79e-4c7406a64010", 
          "title": "Drone Spraying",
          "description": "Precision pesticide application",
          "pricing_model": "PER_ACRE",
          "base_price": 500.0
        }
      ]
    }
    resp = s.post(f"{BASE_URL}/organizations", json=fsp_org_payload, headers=fsp_headers)
    if not print_result("Create FSP Org", resp): return
    fsp_org_id = resp.json()["id"]

    # 1.5 Manual Approval (Simulated via DB command)
    print("\nExecuting DB Approval Override...")
    # Using 'docker compose' (V2) or 'docker-compose' (V1)
    # Trying docker compose first, if fails, assume env issues but previous run showed docker-compose not found.
    # We will try 'docker compose'
    cmd = """docker compose exec -T db psql -U postgres -d uzhathunai_db_v2 -c "UPDATE organizations SET is_approved = true, status = 'ACTIVE' WHERE name IN ('Green Valley Farms', 'AgriTech Sprayers Ltd');" """
    subprocess.run(cmd, shell=True, check=True)
    print("Organizations Approved.")

    # 2.1 Create Farm
    print("\n2.1 Create Farm")
    farm_payload = {
      "name": "North Field - Sector A",
      "description": "Main rice cultivation area",
      "area": 12.5,
      "location": {
        "type": "Point",
        "coordinates": [75.56, 13.92] 
      },
      "farm_attributes": {
        "irrigation_type": "Canal",
        "soil_health": "Good"
      }
    }
    resp = s.post(f"{BASE_URL}/farms", json=farm_payload, headers=farmer_headers)
    if not print_result("Create Farm", resp): return
    farm_id = resp.json()["id"]

    # 2.2 Create Plot
    print("\n2.2 Create Plot")
    plot_payload = {
      "name": "Plot 1",
      "description": "Main plot for rice",
      "area": 5.0
    }
    resp = s.post(f"{BASE_URL}/plots/farms/{farm_id}/plots", json=plot_payload, headers=farmer_headers)
    if not print_result("Create Plot", resp): return
    plot_id = resp.json()["id"]

    # 2.3 Create Crop
    print("\n2.3 Create Crop")
    crop_payload = {
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
    }
    resp = s.post(f"{BASE_URL}/crops", json=crop_payload, headers=farmer_headers)
    if not print_result("Create Crop", resp): return
    # crop_id = resp.json()["id"]

    # 3.1 Create Work Order
    print("\n3.1 Create Work Order")
    wo_payload = {
      "farming_organization_id": farming_org_id,
      "fsp_organization_id": fsp_org_id,
      "title": "Monsoon Spraying Contract",
      "description": "Drone spraying for pest control across North Field",
      "start_date": "2024-07-01",
      "end_date": "2024-07-05",
      "total_amount": 15000,
      "currency": "INR",
      "scope_items": [
        {
          "scope": "FARM",
          "scope_id": farm_id,
          "access_permissions": {
            "read": True,
            "write": True,
            "track": True
          }
        }
      ]
    }
    resp = s.post(f"{BASE_URL}/work-orders", json=wo_payload, headers=farmer_headers)
    if not print_result("Create Work Order", resp): return
    work_order_id = resp.json()["id"]

    # 3.2 Accept Work Order
    print("\n3.2 Accept Work Order")
    resp = s.post(f"{BASE_URL}/work-orders/{work_order_id}/accept", headers=fsp_headers)
    if not print_result("Accept Work Order", resp): return
    
    print("\nVerifying FSP Farm Access...")
    resp = s.get(f"{BASE_URL}/farms/{farm_id}", headers=fsp_headers)
    if resp.status_code == 200:
        print(f"{GREEN}[PASS] FSP Access Granted{RESET}")
    else:
        print(f"{RED}[FAIL] FSP Access Denied (Status: {resp.status_code}){RESET}")
        return

    # 4.1 Schedule Video
    print("\n4.1 Schedule Video")
    video_payload = {
      "work_order_id": work_order_id,
      "topic": "Initial Crop Inspection",
      "start_time": "2024-07-02T10:00:00Z",
      "duration_minutes": 30,
      "agenda": "Inspect leaf health and irrigation levels"
    }
    resp = s.post(f"{BASE_URL}/video/schedule", json=video_payload, headers=fsp_headers)
    if not print_result("Schedule Video", resp): return

    if not print_result("Schedule Video", resp): return

    # 5.1 Start Work Order
    print("\n5.1 Start Work Order")
    resp = s.post(f"{BASE_URL}/work-orders/{work_order_id}/start", headers=fsp_headers)
    if not print_result("Start Work Order", resp): return

    # 5.2 Complete Work Order
    print("\n5.2 Complete Work Order")
    resp = s.post(f"{BASE_URL}/work-orders/{work_order_id}/complete", headers=fsp_headers)
    if not print_result("Complete Work Order", resp): return

    # Verify FSP Access Revoked
    print("\nVerifying FSP Access Revoked...")
    resp = s.get(f"{BASE_URL}/farms/{farm_id}", headers=fsp_headers)
    if resp.status_code == 403 or resp.status_code == 404:
        print(f"{GREEN}[PASS] FSP Access Revoked{RESET}")
    else:
        print(f"{RED}[FAIL] FSP Access NOT Revoked (Status: {resp.status_code}){RESET}")

    print("\n--- Verification SUCCEEDED ---")

if __name__ == "__main__":
    run_verification()
