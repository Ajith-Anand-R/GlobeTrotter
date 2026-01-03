
import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_search():
    print("Starting Search Verification...")
    
    # 1. Search Cities
    print("1. Searching Cities (query='Paris')...")
    resp = requests.get(f"{BASE_URL}/cities/search", params={"query": "Paris"})
    if resp.status_code != 200:
        print(f"Search failed: {resp.status_code} {resp.text}")
        sys.exit(1)
    results = resp.json()
    if len(results) == 0:
         print("   No cities found! Seeding likely failed.")
         sys.exit(1)
    
    city = results[0]
    print(f"   Found: {city['name']} ({city['country']}) - ID: {city['id']}")
    
    # 2. Search Activities
    print(f"2. Searching Activities for {city['name']}...")
    resp = requests.get(f"{BASE_URL}/activities/search", params={"city_id": city['id']})
    if resp.status_code != 200:
        print(f"Activity Search failed: {resp.status_code}")
        sys.exit(1)
    acts = resp.json()
    print(f"   Found {len(acts)} activities.")
    for act in acts:
        print(f"   - {act['name']} ({act['category']}) ${act['cost']}")

    # 3. Filter Activities
    print("3. Filtering Activities (max_cost=20)...")
    resp = requests.get(f"{BASE_URL}/activities/search", params={"city_id": city['id'], "cost_max": 20})
    acts = resp.json()
    print(f"   Found {len(acts)} activities under $20.")
    if len(acts) > 0 and acts[0]['cost'] > 20:
        print("   Filter failed!")
        sys.exit(1)

    print("\nSearch Verification COMPLETE and SUCCESSFUL!")

if __name__ == "__main__":
    test_search()
