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

        if response.status_code != 200:
            print(f"[GetFromImageDB] API returned {response.status_code}, using defaults")
            return DEFAULT_STALLS

        raw = response.json()
        # Normalize shapes: some APIs return a dict mapping stall ids to boxes,
        # others return a list of stall objects. Accept both.
        if isinstance(raw, dict):
            print(f"[GetFromImageDB] Fetched stall config (dict) from API")
            return raw

        if isinstance(raw, list):
            print(f"[GetFromImageDB] Fetched stall config (list) from API; normalizing to dict")
            normalized = {}
            for i, entry in enumerate(raw):
                if not isinstance(entry, dict):
                    continue

                # Try common id/name keys
                stall_id = None
                for key in ("id", "stall_id", "stallId", "name", "stall"):
                    if key in entry:
                        stall_id = entry[key]
                        break

                # If no id found, fall back to generated id
                if not stall_id:
                    stall_id = f"stall_{i}"

                # Extract bounding keys if present
                if all(k in entry for k in ("x1", "y1", "x2", "y2")):
                    normalized[stall_id] = {
                        "x1": int(entry["x1"]),
                        "y1": int(entry["y1"]),
                        "x2": int(entry["x2"]),
                        "y2": int(entry["y2"]),
                    }
                else:
                    # If the entry appears to already be a mapping of coordinates
                    # under nested structure, attempt to find a coords dict
                    coords = None
                    for candidate in ("coords", "box", "bounds"):
                        if candidate in entry and isinstance(entry[candidate], dict):
                            coords = entry[candidate]
                            break

                    if coords and all(k in coords for k in ("x1", "y1", "x2", "y2")):
                        normalized[stall_id] = {
                            "x1": int(coords["x1"]),
                            "y1": int(coords["y1"]),
                            "x2": int(coords["x2"]),
                            "y2": int(coords["y2"]),
                        }
                    else:
                        # Skip malformed entries
                        print(f"[GetFromImageDB] Skipping malformed stall entry: {entry}")

            if normalized:
                return normalized
            else:
                print("[GetFromImageDB] No valid stall entries found in API response; using defaults")
                return DEFAULT_STALLS

        # Unknown format
        print("[GetFromImageDB] Unexpected stall config format from API; using defaults")
        return DEFAULT_STALLS

    except Exception as e:
        print(f"[GetFromImageDB] Error fetching config: {e}, using defaults")
        return DEFAULT_STALLS
