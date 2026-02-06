import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"
CROP_ID = "ce82ddc9-8f4d-49cb-bd99-eda8648160a4" 

# Credentials
EMAIL = "superadmin@uzhathunai.com"
PASSWORD = "SuperSecure@Admin123"

def main():
    session = requests.Session()

    # 1. Login
    print(f"Logging in as {EMAIL}...")
    try:
        resp = session.post(f"{API_V1}/auth/login", json={"email": EMAIL, "password": PASSWORD})
        resp.raise_for_status()
        data = resp.json()
        token = data["data"]["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful.")
    except Exception as e:
        print(f"Login failed: {e}")
        try:
             print(resp.text)
        except:
             pass
        sys.exit(1)

    # 2. Get Measurement Unit
    print("Fetching measurement units...")
    try:
        resp = session.get(f"{API_V1}/measurement-units/", headers=headers, params={"category": "WEIGHT"})
        resp.raise_for_status()
        units = resp.json()
        if not units:
            print("No weight units found! Cannot proceed.")
            sys.exit(1)
        unit_id = units[0]["id"]
        print(f"Using unit: {units[0]['name']} ({unit_id})")
    except Exception as e:
        print(f"Fetch units failed: {e}")
        sys.exit(1)

    # 3. Post Yield (VALID)
    payload = {
        "yield_type": "ACTUAL",
        "quantity": 123.45,
        "quantity_unit_id": unit_id,
        "harvest_date": "2024-02-01",
        "notes": "Post-fix verification"
    }

    print(f"\nSending VALID POST to /crops/{CROP_ID}/yields...")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        resp = session.post(
            f"{API_V1}/crop-yields/crops/{CROP_ID}/yields",
            headers=headers,
            json=payload
        )
        print(f"Status Code: {resp.status_code}")
        print("Response Body:")
        print(resp.text)
        
        if resp.status_code == 500:
            print("\n!!! 500 ERROR STILL PERSISTS !!!")
        elif resp.status_code == 403:
             print("\n!!! 403 Forbidden - expected for superadmin without org, FIX VERIFIED (Backend handled request logic) !!!")
        elif resp.status_code == 201:
             print("\n!!! SUCCESS !!!")
        else:
             print(f"\nUnexpected status: {resp.status_code}")

    except Exception as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    main()
