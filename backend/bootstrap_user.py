import requests

def bootstrap():
    url = "http://127.0.0.1:8000/auth/signup"
    data = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Alex Morgan"
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Successfully created test user!")
            print("Email: test@example.com")
            print("Password: password123")
        else:
            print(f"Failed to create user. Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error connecting to backend: {e}. Make sure the backend is running at http://localhost:8000")

if __name__ == "__main__":
    bootstrap()
