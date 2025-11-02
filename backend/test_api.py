import requests
import json

# Test registering a new user
register_data = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123",
    "full_name": "Test User",
    "role": "mentor"
}

response = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    headers={"accept": "application/json", "Content-Type": "application/json"},
    data=json.dumps(register_data)
)

print("Register response:", response.status_code)
print("Register data:", response.json())

# Test creating a mentor profile
if response.status_code == 201:
    user_data = response.json()
    user_id = user_data["id"]
    
    mentor_data = {
        "user_id": user_id,
        "bio": "Experienced software developer",
        "specialization": "Python, FastAPI",
        "experience_years": 5,
        "hourly_rate": 5000,  # 50 USD in cents
        "is_available": True
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/mentors/",
        headers={"accept": "application/json", "Content-Type": "application/json"},
        data=json.dumps(mentor_data)
    )
    
    print("Mentor creation response:", response.status_code)
    print("Mentor data:", response.json())