import os
import requests
from typing import Dict, Any, Optional


GET_STALL_CONFIG_URL = os.getenv("GET_STALL_CONFIG_URL")

# Default stall configuration
DEFAULT_STALLS: Dict[str, Dict[str, int]] = {
    "A1": {"x1": 428,  "y1": 36,  "x2": 628,  "y2": 175},
    "A2": {"x1": 424,  "y1": 188, "x2": 613,  "y2": 322},
    "A3": {"x1": 410,  "y1": 321, "x2": 606,  "y2": 471},
    "A4": {"x1": 398,  "y1": 471, "x2": 592,  "y2": 618},
    "A5": {"x1": 937,  "y1": 64,  "x2": 1148, "y2": 207},
    "A6": {"x1": 923,  "y1": 218, "x2": 1142, "y2": 360},
    "A7": {"x1": 917,  "y1": 366, "x2": 1131, "y2": 511},
    "A8": {"x1": 907,  "y1": 514, "x2": 1126, "y2": 672},
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
