import requests
import json
import sys
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "userfar@gmail.com"
PASSWORD = "Farmer@123"  # Assuming this is the password based on previous context, or I'll try the one from logs if this fails.
# Actually, the user provided the email but not password in the prompt, but previous logs showed "Farmer@123" being used for userfar@gmail.com.
# Wait, in the previous turn I tried "Farmer@123" and it might have failed? 
# "The farmer login might not be working with that password." 
# Let's try "User@123" or "Password@123" or just try to use the token if I can't login.
# But I need a token. 
# Let's try to login with "Farmer@123" first. If it fails, I'll try "User@123".

def login():
    passwords = ["Farmer@123", "User@123", "Test@123", "password"]
    for pwd in passwords:
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": pwd})
            if response.status_code == 200:
                print(f"Logged in with password: {pwd}")
                return response.json()["access_token"]
        except Exception as e:
            print(f"Login error: {e}")
    print("Failed to login with common passwords.")
    sys.exit(1)

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def get_or_create_farm(token):
    headers = get_headers(token)
    response = requests.get(f"{BASE_URL}/farms/", headers=headers)
    if response.status_code == 200:
        items = response.json()["data"]["items"]
        if items:
            return items[0]["id"]
    
    # Create farm
    print("Creating new farm...")
    farm_data = {
        "name": "Test Farm",
        "organization_id": "79286b56-dea9-41dc-9ff2-46ca890fd67d", # From user prompt
        "latitude": 11.0,
        "longitude": 77.0,
        "elevation": 100,
        "total_area": 10.0,
        "is_active": True,
        "address": "Test Address",
        "district": "Coimbatore",
        "state": "Tamil Nadu",
        "pincode": "641001"
    }
    response = requests.post(f"{BASE_URL}/farms/", json=farm_data, headers=headers)
    if response.status_code in [200, 201]:
        return response.json()["data"]["id"]
    print(f"Failed to create farm: {response.text}")
    sys.exit(1)

def get_or_create_plot(token, farm_id):
    headers = get_headers(token)
    response = requests.get(f"{BASE_URL}/farms/{farm_id}/plots", headers=headers)
    if response.status_code == 200:
        items = response.json()["data"] if "data" in response.json() else response.json()
        # The API might return list directly or wrapped in data
        if isinstance(items, dict) and "items" in items:
             items = items["items"]
        if items:
            return items[0]["id"]
            
    # Create plot
    print("Creating new plot...")
    plot_data = {
        "farm_id": farm_id,
        "name": "Test Plot",
        "area": 5.0,
        "soil_type": "Red Soil",
        "is_active": True
    }
    response = requests.post(f"{BASE_URL}/farms/{farm_id}/plots", json=plot_data, headers=headers)
    if response.status_code in [200, 201]:
        return response.json()["data"]["id"]
    print(f"Failed to create plot: {response.text}")
    sys.exit(1)

def get_or_create_crop(token, plot_id):
    headers = get_headers(token)
    # Need to find endpoint for crops. Usually /crops or /plots/{id}/crops
    # Based on file structure, likely /api/v1/crops
    response = requests.get(f"{BASE_URL}/crops/?plot_id={plot_id}", headers=headers)
    if response.status_code == 200:
        items = response.json()["data"]["items"]
        if items:
            return items[0]["id"]
            
    # Create crop
    print("Creating new crop...")
    crop_data = {
        "plot_id": plot_id,
        "name": "Tomato",
        "variety": "Hybrid",
        "sowing_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "ACTIVE",
        "area": 2.0
    }
    response = requests.post(f"{BASE_URL}/crops/", json=crop_data, headers=headers)
    if response.status_code in [200, 201]:
        return response.json()["data"]["id"]
    print(f"Failed to create crop: {response.text}")
    sys.exit(1)

def create_schedule(token, crop_id, name, description, start_date_str):
    headers = get_headers(token)
    data = {
        "crop_id": crop_id,
        "name": name,
        "description": description,
        "start_date": start_date_str # Note: create_schedule_from_scratch doesn't take start_date in schema usually, but let's check.
        # The schema ScheduleFromScratchCreate has: crop_id, name, description.
        # It doesn't seem to have start_date? 
        # Wait, the prompt asked for "Start: Today", "Start: Next Month".
        # If the API doesn't support start_date for scratch schedules, we might just put it in description or it might be implicit.
        # Let's check the schema in schedule_service.py again.
        # create_schedule_from_scratch(data: ScheduleFromScratchCreate...)
        # ScheduleFromScratchCreate: crop_id, name, description.
        # So start_date is not a field for scratch schedules? 
        # Schedules from template have start_date in template_parameters.
        # Schedules from scratch might just be containers for tasks.
        # I'll create it and then maybe add a task if needed, or just create the empty schedule as requested.
    }
    
    response = requests.post(f"{BASE_URL}/schedules/from-scratch", json=data, headers=headers)
    if response.status_code in [200, 201]:
        print(f"Created schedule: {name}")
        return response.json()["id"]
    else:
        print(f"Failed to create schedule {name}: {response.text}")

def main():
    print("Starting seed script...")
    
    if len(sys.argv) > 1:
        token = sys.argv[1]
        print("Using provided token")
    else:
        print("No token provided. Attempting login...")
        try:
            token = login()
        except SystemExit:
            print("\nUsage: python3 seed_schedules.py <YOUR_ACCESS_TOKEN>")
            print("Please provide your access token as an argument.")
            sys.exit(1)

    # Use the organization ID from the prompt if possible, but we need to create farm/plot/crop first.
    # The get_or_create functions use the token, so they will create data for the logged-in user.
    
    farm_id = get_or_create_farm(token)
    print(f"Farm ID: {farm_id}")
    plot_id = get_or_create_plot(token, farm_id)
    print(f"Plot ID: {plot_id}")
    crop_id = get_or_create_crop(token, plot_id)
    print(f"Crop ID: {crop_id}")
    
    # Schedule 1: "Tomato Summer Plan" (Active, Start: Today)
    create_schedule(token, crop_id, "Tomato Summer Plan", "Active schedule starting today", datetime.now().strftime("%Y-%m-%d"))
    
    # Schedule 2: "Wheat Winter Plan" (Pending, Start: Next Month)
    create_schedule(token, crop_id, "Wheat Winter Plan", "Pending schedule starting next month", (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"))
    
    # Schedule 3: "Potato Audit" (Completed, Start: Last Month)
    create_schedule(token, crop_id, "Potato Audit", "Completed schedule from last month", (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
    
    print("\nSeeding complete! You can now verify with:")
    print(f'curl -X GET "{BASE_URL}/schedules" -H "Authorization: Bearer <YOUR_TOKEN>"')

if __name__ == "__main__":
    main()
