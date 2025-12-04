import os
import requests
from typing import Dict, Any


POST_AVAILABILITY_URL = os.getenv("POST_AVAILABILITY_URL")


def post_availability(payload: Dict[str, Any]) -> bool:
    """
    Post availability results to the external API.
    
    Args:
        payload: Dictionary containing lotNum, timestamp, availability, and status
        
    Returns:
        True if successful, False otherwise
    """
    if not POST_AVAILABILITY_URL:
        print("[PostToItemsDb] POST_AVAILABILITY_URL not configured")
        return False
    
    try:
        response = requests.post(
            POST_AVAILABILITY_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"[PostToItemsDb] Successfully posted availability for lot {payload.get('lotNum')}")
            return True
        else:
            print(f"[PostToItemsDb] Failed: {response.status_code} {response.text}")
            return False
            
    except Exception as e:
        print(f"[PostToItemsDb] Error: {e}")
        return False
