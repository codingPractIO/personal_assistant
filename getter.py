import requests
import json
import os
from datetime import datetime

# Headers for the request
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def get_json_data(url):
    # Send the GET request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse JSON response
        data = response.json()

        # Ensure the raw_data folder exists
        os.makedirs("raw_data", exist_ok=True)

        # Create a filename based on the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"raw_data/response_{timestamp}.json"

        # Save to a file with proper encoding
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Response saved to {file_path} with UTF-8 encoding. Code: {response.status_code}")
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
