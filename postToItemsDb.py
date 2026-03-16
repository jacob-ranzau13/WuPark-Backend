import os
import requests
from typing import Dict, Any


POST_AVAILABILITY_URL = os.getenv("POST_AVAILABILITY_URL")
AVAILABILITY_API_KEY = os.getenv("AVAILABILITY_API_KEY")



def post_availability(payload: Dict[str, Any]) -> bool:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AVAILABILITY_API_KEY}"
    }
    
    try:
        response = requests.post(
            POST_AVAILABILITY_URL,
            json=payload,
            headers=headers,
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
