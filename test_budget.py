import requests

def test():
    # Check Ping
    try:
        resp = requests.get("http://127.0.0.1:8001/ping")
        print(f"Ping Response: {resp.status_code}")
    except Exception as e:
        print(f"Ping failed: {e}")
        return

    # Login first (assuming test user exists, otherwise sign up)
    email = "test_budget_unique_234@example.com"
    password = "password"
    
    # Try signup just in case
    try:
        requests.post("http://127.0.0.1:8001/auth/signup", json={"email": email, "password": password, "full_name": "Test User"})
    except:
        pass
        
    # Login
    resp = requests.post("http://127.0.0.1:8001/auth/login", json={"email": email, "password": password, "full_name": "Test User"})
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return
        
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create Trip
    print("Creating trip...")
    resp = requests.post("http://127.0.0.1:8001/trips/", json={
        "title": "Budget Test Trip",
        "destination": "London",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-10T00:00:00",
        "status": "upcoming"
    }, headers=headers)
    
    if resp.status_code != 200:
        print(f"Create trip failed: {resp.status_code}")
        print(resp.text)
        return

    trip = resp.json()
    trip_id = trip["id"]
    print(f"Created Trip {trip_id}")
    
    # Check Trip Detail
    resp = requests.get(f"http://127.0.0.1:8001/trips/{trip_id}", headers=headers)
    print(f"Trip Detail Response: {resp.status_code}")

    # Get Budget
    resp = requests.get(f"http://127.0.0.1:8001/budget/{trip_id}", headers=headers)
    print(f"Budget Response: {resp.status_code}")
    print(resp.json())

if __name__ == "__main__":
    test()
