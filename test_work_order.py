
import requests
import json
import sys

# Constants
BASE_URL = "http://localhost:8000/api/v1"
FARMER_EMAIL = "niren@gmail.com"
PASSWORD = "Test@12345"

# Seeded IDs
FSP_ORG_ID = "b8879df7-59e2-4141-a51b-6b18223ed0f9"
FARMER_ORG_ID = "323a3c49-1a25-4979-b4b0-8debf75ec516"
SERVICE_LISTING_ID = "8c0ae5af-8404-4fce-be36-e580ec3f14f9"

def debug_work_order():
    try:
        # 1. Login
        print("Logging in...")
        login_resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": FARMER_EMAIL,
            "password": PASSWORD
        })
        
        if login_resp.status_code != 200:
            print(f"Login failed: {login_resp.text}")
            return
            
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Logged in successfully.")

        # 2. Try POST Work Order with Minimal Payload
        print("\nAttempting Minimal Work Order Creation...")
        payload = {
            "farming_organization_id": FARMER_ORG_ID,
            "fsp_organization_id": FSP_ORG_ID,
            "service_listing_id": SERVICE_LISTING_ID,
            "title": "Debug Work Order"
        }
        
        resp = requests.post(f"{BASE_URL}/work-orders", json=payload, headers=headers)
        
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_work_order()
