import requests
import json

# Define the API endpoint (replace with your local server URL)
API_URL = "http://127.0.0.1:5000/get_history"

# Sample user_id for testing
USER_ID = "test_user_123"

# Prepare the request payload
payload = {"user_id": USER_ID}

# Send the request
response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"})

# Print the response
print("Status Code:", response.status_code)
print("Response JSON:", json.dumps(response.json(), indent=2))
