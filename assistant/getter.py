"""Utility to fetch and store JSON data from URLs."""

import json
import logging
import os
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

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
        logger.info("Response saved to %s with UTF-8 encoding. Code: %s", file_path, response.status_code)
    else:
        logger.error("Request failed with status code %s", response.status_code)
        logger.error(response.text)
