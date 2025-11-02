import requests
import json

# Test registration
register_data = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "test1234",
    "full_name": "Test User"
}

try:
    response = requests.post(
        "http://localhost:8000/api/v1/auth/register",
        headers={"Content-Type": "application/json"},
        data=json.dumps(register_data)
    )
    print(f"Registration response: {response.status_code}")
    print(f"Response data: {response.json()}")
except Exception as e:
    print(f"Error during registration: {e}")

# Test login
login_data = {
    "email": "test@example.com",
    "password": "testpassword123"
}

try:
    response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        headers={"Content-Type": "application/json"},
        data=json.dumps(login_data)
    )
    print(f"Login response: {response.status_code}")
    print(f"Response data: {response.json()}")
except Exception as e:
    print(f"Error during login: {e}")