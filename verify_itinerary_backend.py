
import requests
import sys

BASE_URL = "http://127.0.0.1:8000"
updated_trip = None

def test_backend():
    print("Starting Backend Verification...")
    
    try:
        # 0. Signup
        import random
        rand_id = random.randint(1000, 9999)
        email = f"verify_user_{rand_id}@example.com"
        pwd = "password123"
        print(f"0. Signing up new user: {email}...")
        
        signup_data = {"email": email, "password": pwd, "full_name": "Verify User"}
        resp = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
        if resp.status_code != 200:
            print(f"Signup failed: {resp.status_code} {resp.text}")
            sys.exit(1)

        # 1. Login
        print("1. Logging in...")
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": pwd, "full_name": "Verify User"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            sys.exit(1)
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   Login successful.")
    except Exception as e:
        print(f"EXCEPTION: {e}")
        sys.exit(1)
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        sys.exit(1)
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   Login successful.")

    # 2. Create Trip
    print("2. Creating Trip...")
    trip_data = {
        "title": "Itinerary Test Trip",
        "destination": "Europe",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-15T00:00:00",
        "status": "upcoming"
    }
    resp = requests.post(f"{BASE_URL}/trips/", json=trip_data, headers=headers)
    if resp.status_code != 200:
        print(f"Create trip failed: {resp.text}")
        sys.exit(1)
    trip_id = resp.json()["id"]
    print(f"   Trip created directly (ID: {trip_id})")

    # 3. Add Stops
    print("3. Adding Stops...")
    # Stop 1
    stop1_data = {
        "city_name": "London",
        "arrival_date": "2026-06-01T00:00:00",
        "departure_date": "2026-06-05T00:00:00",
        "sort_order": 0
    }
    resp = requests.post(f"{BASE_URL}/trips/{trip_id}/stops", json=stop1_data, headers=headers)
    stop1_id = resp.json()["id"]
    
    # Stop 2
    stop2_data = {
        "city_name": "Paris",
        "arrival_date": "2026-06-06T00:00:00",
        "departure_date": "2026-06-10T00:00:00",
        "sort_order": 1
    }
    resp = requests.post(f"{BASE_URL}/trips/{trip_id}/stops", json=stop2_data, headers=headers)
    stop2_id = resp.json()["id"]
    print(f"   Stops added: {stop1_id} (London), {stop2_id} (Paris)")

    # 4. Add Activity
    print("4. Adding Activity to Stop 1...")
    act_data = {
        "description": "Tower of London",
        "time": "10:00 AM",
        "cost": 25.0
    }
    resp = requests.post(f"{BASE_URL}/stops/{stop1_id}/activities", json=act_data, headers=headers)
    act_id = resp.json()["id"]
    print(f"   Activity added (ID: {act_id})")

    # 5. Update Stop
    print("5. Updating Stop 1...")
    update_data = {
        "city_name": "London Updated",
        "arrival_date": "2026-06-01T00:00:00",
        "departure_date": "2026-06-05T00:00:00",
        "sort_order": 0
    }
    resp = requests.put(f"{BASE_URL}/stops/{stop1_id}", json=update_data, headers=headers)
    if resp.json()["city_name"] != "London Updated":
        print("   Update Stop failed!")
        sys.exit(1)
    print("   Stop updated successfully.")

    # 6. Update Activity
    print("6. Updating Activity...")
    act_update = {
        "description": "Tower Tour Updated",
        "cost": 30.0
    }
    resp = requests.put(f"{BASE_URL}/activities/{act_id}", json=act_update, headers=headers)
    if resp.json()["description"] != "Tower Tour Updated":
        print("   Update Activity failed!")
        sys.exit(1)
    print("   Activity updated successfully.")

    # 7. Reorder Stops
    print("7. Reordering Stops (Paris first)...")
    reorder_data = {"stop_ids": [stop2_id, stop1_id]}
    resp = requests.post(f"{BASE_URL}/trips/{trip_id}/reorder_stops", json=reorder_data, headers=headers)
    if resp.status_code != 200:
        print("   Reorder failed!")
        sys.exit(1)
    
    # Verify Order
    resp = requests.get(f"{BASE_URL}/trips/{trip_id}", headers=headers)
    stops = resp.json()["stops"]
    # We need to sort by sort_order to check
    stops.sort(key=lambda x: x["sort_order"])
    if stops[0]["id"] != stop2_id:
         print(f"   Reorder Verification Failed! Expected {stop2_id} first, got {stops[0]['id']}")
    else:
         print(f"   Reorder Verified: Paris is first.")

    # 8. Delete Activity
    print("8. Deleting Activity...")
    resp = requests.delete(f"{BASE_URL}/activities/{act_id}", headers=headers)
    if resp.status_code != 200:
        print("   Delete Activity failed")
    
    # 9. Delete Stop
    print("9. Deleting Stop 1...")
    resp = requests.delete(f"{BASE_URL}/stops/{stop1_id}", headers=headers)
    if resp.status_code != 200:
        print("   Delete Stop failed")

    print("\nBackend Verification COMPLETE and SUCCESSFUL!")

if __name__ == "__main__":
    test_backend()
