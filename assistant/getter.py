"""Utility to fetch and store JSON data from URLs."""

import json
import logging
import os
from datetime import datetime
import requests
from typing import Any

logger = logging.getLogger(__name__)

# Headers for the request
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def get_json_data(url) -> dict[str, Any] | None:
    # Send the GET request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse JSON response
        data = response.json()
        return data
    else:
        logger.error(f"Failed to fetch data from {url}. Status code: {response.status_code}")
        return None
