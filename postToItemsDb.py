import os
import requests
from typing import Dict, Any


POST_AVAILABILITY_URL = os.getenv("POST_AVAILABILITY_URL")
AVAILABILITY_API_KEY = os.getenv("AVAILABILITY_API_KEY")

#Yippie

def post_availability(payload: Dict[str, Any]) -> bool:
    headers = {
        "Content-Type": "application/json",
        "x-api-key": AVAILABILITY_API_KEY
    }
    
    try:
        print(f"[PostToItemsDb] POST {POST_AVAILABILITY_URL}")
        print(f"[PostToItemsDb] API key set: {bool(AVAILABILITY_API_KEY)}, length: {len(AVAILABILITY_API_KEY) if AVAILABILITY_API_KEY else 0}")
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
            print(f"[PostToItemsDb] Request headers sent: { {k: v[:10] + '...' if k == 'x-api-key' else v for k, v in headers.items()} }")
            return False
            
    except Exception as e:
        print(f"[PostToItemsDb] Error: {e}")
        return False
