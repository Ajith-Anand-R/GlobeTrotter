"""
Test script for Admin Dashboard API endpoints
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_admin_api():
    print("="*60)
    print("TESTING ADMIN DASHBOARD ENDPOINTS")
    print("="*60)
    
    # 1. Access without Admin Token (Should Fail)
    print("\n1. Testing GET /admin/stats (Unauthorized)")
    response = requests.get(f"{BASE_URL}/admin/stats")
    print(f"   Status: {response.status_code}") 
    # Expected: 401 or 403 (depending on auth middleware, usually 401 if no token)

    print("\n2. Admin Verification Steps:")
    print("   To verify admin features manually:")
    print("   a. DB: UPDATE users SET is_admin=1 WHERE email='your_email';")
    print("   b. Login to get token.")
    print("   c. Call GET /admin/stats")
    print("   d. Call GET /admin/stats/growth")
    print("   e. Call GET /admin/stats/top-destinations")
    print("   f. Call GET /admin/users")

if __name__ == "__main__":
    test_admin_api()
