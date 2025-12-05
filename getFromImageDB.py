import os
import requests
from typing import Dict, Any, Optional


GET_STALL_CONFIG_URL = os.getenv("GET_STALL_CONFIG_URL")

# Default stall configuration
DEFAULT_STALLS: Dict[str, Dict[str, int]] = {
    "A1": {"x1": 390,  "y1": 103, "x2": 569,  "y2": 223},
    "A2": {"x1": 377,  "y1": 236, "x2": 558,  "y2": 359},
    "A3": {"x1": 361,  "y1": 370, "x2": 549,  "y2": 503},
    "A4": {"x1": 342,  "y1": 512, "x2": 531,  "y2": 653},
    "A5": {"x1": 853,  "y1": 120, "x2": 1058, "y2": 250},
    "A6": {"x1": 851,  "y1": 266, "x2": 1058, "y2": 390},
    "A7": {"x1": 850,  "y1": 404, "x2": 1058, "y2": 540},
    "A8": {"x1": 845,  "y1": 551, "x2": 1066, "y2": 695},
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
