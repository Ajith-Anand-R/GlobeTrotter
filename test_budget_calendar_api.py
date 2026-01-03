"""
Test script for Budget and Calendar API endpoints
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

# Test credentials (you may need to adjust these)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def test_budget_endpoints():
    """Test budget-related endpoints"""
    print("\n" + "="*60)
    print("TESTING BUDGET ENDPOINTS")
    print("="*60)
    
    # Assume trip_id = 1 exists
    trip_id = 1
    
    # Test 1: Get budget summary
    print("\n1. Testing GET /budget/{trip_id}")
    response = requests.get(f"{BASE_URL}/budget/{trip_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Budget Limit: ${data.get('budget_limit', 0):.2f}")
        print(f"Total Cost: ${data.get('total_cost', 0):.2f}")
        print(f"Remaining: ${data.get('remaining', 0):.2f}")
        print(f"Utilization: {data.get('utilization_percentage', 0):.1f}%")
        print(f"Alerts: {len(data.get('alerts', []))} alert(s)")
    else:
        print(f"Error: {response.text}")
    
    # Test 2: Get daily trend
    print("\n2. Testing GET /budget/{trip_id}/daily-trend")
    response = requests.get(f"{BASE_URL}/budget/{trip_id}/daily-trend")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Daily Budget Limit: ${data.get('budget_limit_per_day', 0):.2f}")
        print(f"Number of days: {len(data.get('days', []))}")
        if data.get('days'):
            first_day = data['days'][0]
            print(f"First day ({first_day['date']}): ${first_day['total']:.2f}")
    else:
        print(f"Error: {response.text}")

def test_expense_endpoints():
    """Test expense CRUD endpoints"""
    print("\n" + "="*60)
    print("TESTING EXPENSE ENDPOINTS")
    print("="*60)
    
    trip_id = 1
    
    # Test 1: Create expense
    print("\n1. Testing POST /trips/{trip_id}/expenses")
    expense_data = {
        "name": "Test Taxi Ride",
        "category": "transport",
        "amount": 25.50,
        "currency": "USD",
        "date": datetime.now().isoformat(),
        "notes": "From airport to hotel"
    }
    response = requests.post(f"{BASE_URL}/trips/{trip_id}/expenses", json=expense_data)
    print(f"Status: {response.status_code}")
    
    expense_id = None
    if response.status_code == 200:
        data = response.json()
        expense_id = data.get('id')
        print(f"Created expense ID: {expense_id}")
        print(f"Name: {data.get('name')}")
        print(f"Amount: ${data.get('amount'):.2f}")
    else:
        print(f"Error: {response.text}")
    
    # Test 2: Get all expenses
    print("\n2. Testing GET /trips/{trip_id}/expenses")
    response = requests.get(f"{BASE_URL}/trips/{trip_id}/expenses")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        expenses = response.json()
        print(f"Total expenses: {len(expenses)}")
        for exp in expenses[:3]:  # Show first 3
            print(f"  - {exp['name']}: ${exp['amount']:.2f} ({exp['category']})")
    else:
        print(f"Error: {response.text}")
    
    # Test 3: Update expense (if we created one)
    if expense_id:
        print(f"\n3. Testing PUT /expenses/{expense_id}")
        update_data = {
            "amount": 30.00,
            "notes": "Updated: From airport to hotel (with tip)"
        }
        response = requests.put(f"{BASE_URL}/expenses/{expense_id}", json=update_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Updated amount: ${data.get('amount'):.2f}")
            print(f"Updated notes: {data.get('notes')}")
        else:
            print(f"Error: {response.text}")
        
        # Test 4: Delete expense
        print(f"\n4. Testing DELETE /expenses/{expense_id}")
        response = requests.delete(f"{BASE_URL}/expenses/{expense_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")

def test_timeline_endpoints():
    """Test timeline and calendar endpoints"""
    print("\n" + "="*60)
    print("TESTING TIMELINE & CALENDAR ENDPOINTS")
    print("="*60)
    
    trip_id = 1
    
    # Test 1: Get timeline
    print("\n1. Testing GET /trips/{trip_id}/timeline")
    response = requests.get(f"{BASE_URL}/trips/{trip_id}/timeline")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Trip: {data.get('title')}")
        print(f"Duration: {data.get('start_date')} to {data.get('end_date')}")
        print(f"Number of days: {len(data.get('days', []))}")
        
        if data.get('days'):
            first_day = data['days'][0]
            print(f"\nFirst day: {first_day['title']}")
            print(f"  Activities: {len(first_day.get('activities', []))}")
            for activity in first_day.get('activities', [])[:2]:
                print(f"    - {activity['description']} ({activity.get('time', 'No time')})")
    else:
        print(f"Error: {response.text}")
    
    # Test 2: Get calendar
    print("\n2. Testing GET /trips/{trip_id}/calendar")
    response = requests.get(f"{BASE_URL}/trips/{trip_id}/calendar")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Month: {data.get('month')}")
        print(f"Total days in view: {len(data.get('days', []))}")
        
        trip_days = [d for d in data.get('days', []) if d['is_trip_day']]
        print(f"Trip days: {len(trip_days)}")
        
        days_with_activities = [d for d in data.get('days', []) if d['has_activities']]
        print(f"Days with activities: {len(days_with_activities)}")
    else:
        print(f"Error: {response.text}")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TRIP BUDGET & CALENDAR API ENDPOINT TESTS")
    print("="*60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Testing against trip_id: 1")
    print("\nNote: These tests assume:")
    print("  - The server is running on port 8000")
    print("  - A trip with ID 1 exists")
    print("  - The trip has start_date and end_date set")
    
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/trips/")
        if response.status_code == 401:
            print("\n⚠️  Authentication required. Tests will run without auth.")
            print("   Some endpoints may return 401 errors.")
        
        test_budget_endpoints()
        test_expense_endpoints()
        test_timeline_endpoints()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS COMPLETED")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print(f"   Make sure the server is running on {BASE_URL}")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    main()
