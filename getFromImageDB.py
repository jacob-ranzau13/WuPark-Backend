import os
import requests
from typing import Dict, Any, Optional


GET_STALL_CONFIG_URL = os.getenv("GET_STALL_CONFIG_URL")

# Default stall configuration
DEFAULT_STALLS: Dict[str, Dict[str, int]] = {
    "A1": {"x1": 403,  "y1": 81,  "x2": 597,  "y2": 197},
    "A2": {"x1": 405,  "y1": 218, "x2": 598,  "y2": 330},
    "A3": {"x1": 402,  "y1": 356, "x2": 601,  "y2": 482},
    "A4": {"x1": 402,  "y1": 500, "x2": 602,  "y2": 631},
    "A5": {"x1": 890,  "y1": 55,  "x2": 1115, "y2": 174},
    "A6": {"x1": 897,  "y1": 200, "x2": 1124, "y2": 320},
    "A7": {"x1": 902,  "y1": 356, "x2": 1132, "y2": 471},
    "A8": {"x1": 912,  "y1": 497, "x2": 1151, "y2": 634},
}


def get_stall_config() -> Dict[str, Dict[str, int]]:
    
    if not GET_STALL_CONFIG_URL:
        print(f"[GetFromImageDB] No config URL set, using default stalls")
        return DEFAULT_STALLS
    
    try:
        response = requests.get(
            GET_STALL_CONFIG_URL,
            timeout=10
        )
        
        if response.status_code == 200:
            stalls = response.json()
            print(f"[GetFromImageDB] Fetched stall config from API")
            return stalls
        else:
            print(f"[GetFromImageDB] API returned {response.status_code}, using defaults")
            return DEFAULT_STALLS
            
    except Exception as e:
        print(f"[GetFromImageDB] Error fetching config: {e}, using defaults")
        return DEFAULT_STALLS
