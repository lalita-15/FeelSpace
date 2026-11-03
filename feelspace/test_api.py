
import requests

BASE_URL = "http://127.0.0.1:5000"

# Test 1: Health Check API
print("\n--- HEALTH CHECK API ---")

health_response = requests.get(f"{BASE_URL}/health")

print("Status Code:", health_response.status_code)
print("Response:", health_response.json())


# Test 2: Create Thought (POST API)
print("\n--- CREATE THOUGHT API ---")

data = {
    "content": "I am learning DevOps and building FeelSpace!",
    "mood": "Motivated",
    "anonymous": True
}

post_response = requests.post(
    f"{BASE_URL}/api/thoughts",
    json=data
)

print("Status Code:", post_response.status_code)
print("Response:", post_response.json())


# Test 3: Get All Thoughts (GET API)
print("\n--- GET ALL THOUGHTS API ---")

get_response = requests.get(
    f"{BASE_URL}/api/thoughts"
)

print("Status Code:", get_response.status_code)
print("Response:", get_response.json())


# Test Results
print("\n--- TEST SUMMARY ---")

if health_response.status_code == 200:
    print("Health Check: PASSED")
else:
    print("Health Check: FAILED")

if post_response.status_code == 201:
    print("Create Thought: PASSED")
else:
    print("Create Thought: FAILED")

if get_response.status_code == 200:
    print("Get Thoughts: PASSED")
else:
    print("Get Thoughts: FAILED")
