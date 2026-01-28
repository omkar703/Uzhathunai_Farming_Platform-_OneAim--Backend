import requests
import sys

# Constants
BASE_URL = "http://localhost:8000/api/v1"
FSP_EMAIL = "fsp_manager@gmail.com"
PASSWORD = "Test@12345"

def login(email, password):
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return None
        return resp.json()["data"]["tokens"]["access_token"]
    except Exception as e:
        print(f"Login error: {e}")
        return None

def verify_get_schedules():
    token = login(FSP_EMAIL, PASSWORD)
    if not token:
        sys.exit(1)
        
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Fetching Schedules...")
    try:
        resp = requests.get(f"{BASE_URL}/schedules", headers=headers)
        
        if resp.status_code == 200:
            print("✅ Successfully fetched schedules!")
            data = resp.json()
            print(f"Total: {data.get('total')}")
            print(f"Items: {len(data.get('items', []))}")
            if data.get('items'):
                print(f"Sample Item: {data['items'][0]['name']}")
            return True
        else:
            print(f"❌ Failed to fetch schedules: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"Request error: {e}")
        return False

if __name__ == "__main__":
    success = verify_get_schedules()
    sys.exit(0 if success else 1)
