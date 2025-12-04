import os
import json
import base64
import requests
from typing import Dict, Any, List, Optional
from inference_sdk import InferenceHTTPClient


STALLS: Dict[str, Dict[str, int]] = {
    "A1": {"x1": 403,  "y1": 81,  "x2": 597,  "y2": 197},
    "A2": {"x1": 405,  "y1": 218, "x2": 598,  "y2": 330},
    "A3": {"x1": 402,  "y1": 356, "x2": 601,  "y2": 482},
    "A4": {"x1": 402,  "y1": 500, "x2": 602,  "y2": 631},
    "A5": {"x1": 890,  "y1": 55,  "x2": 1115, "y2": 174},
    "A6": {"x1": 897,  "y1": 200, "x2": 1124, "y2": 320},
    "A7": {"x1": 902,  "y1": 356, "x2": 1132, "y2": 471},
    "A8": {"x1": 912,  "y1": 497, "x2": 1151, "y2": 634},
}


# ==========================
# 2. API ENDPOINTS
# ==========================
# This should be the "last-minute images" endpoint that returns an array
GET_RECENT_IMAGES_URL = "https://your-api/images/latest"
POST_AVAILABILITY_URL = "https://your-api/availability"


# ==========================
# 3. ROBOFLOW CLIENT
# ==========================
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "i1VhLE1hehZpZZqrLBHO")
ROBOFLOW_WORKSPACE = "wupark-demo-model"
ROBOFLOW_WORKFLOW_ID = "find-cars"

rf_client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=ROBOFLOW_API_KEY,
)


# ==========================
# 4. STALL / PREDICTION LOGIC
# ==========================
def point_in_box(x: float, y: float, box: Dict[str, int]) -> bool:
    return box["x1"] <= x <= box["x2"] and box["y1"] <= y <= box["y2"]


def compute_availability_from_predictions(
    preds: List[Dict[str, Any]],
    stalls: Dict[str, Dict[str, int]] = STALLS,
    target_class: str = "car",
    conf_thresh: float = 0.4,
) -> Dict[str, Any]:
    """
    preds: list under wf_result[0]["predictions"]["predictions"] from Roboflow.
    Uses the (x, y) center and class to determine which stalls are occupied.
    """

    status: Dict[str, Dict[str, Any]] = {
        sid: {"occupied": False, "cars": []}
        for sid in stalls.keys()
    }

    for idx, det in enumerate(preds):
        label = det.get("class")
        conf = det.get("confidence", 0.0)
        x = det.get("x")
        y = det.get("y")

        if label != target_class:
            continue
        if conf < conf_thresh:
            continue
        if x is None or y is None:
            continue

        # Assign to stalls whose rectangle contains the center point
        for stall_id, box in stalls.items():
            if point_in_box(x, y, box):
                status[stall_id]["occupied"] = True
                status[stall_id]["cars"].append(idx)

    return status


# ==========================
# 5. FETCH IMAGE FROM API
# ==========================
TIMESTAMP_FIELD = "timestamp"  # unix int
IMAGE_FIELD = "image"          # binary (base64-encoded in JSON)
LOT_FIELD = "lotNum"           # lot number


def fetch_latest_image_from_api() -> Optional[Dict[str, Any]]:
    """
    Calls your API which returns all images from the last minute.

    Expected JSON (simplified):
    [
      {
        "lotNum": 4,
        "timestamp": 1733281800,
        "image": "base64string..."
      },
      ...
    ]

    Returns:
        {
          "image_bytes": <bytes>,
          "timestamp": <int>,
          "lotNum": <str or int>
        }
    """
    try:
        resp = requests.get(GET_RECENT_IMAGES_URL, timeout=10)
    except Exception as e:
        print(f"[WuPark] Error calling GET_RECENT_IMAGES_URL: {e}")
        return None

    if resp.status_code != 200:
        print(f"[WuPark] Failed to fetch recent images: {resp.status_code} {resp.text}")
        return None

    data = resp.json()
    items = data  # assuming it's already a list

    if not isinstance(items, list) or not items:
        print("[WuPark] No images returned from API (last minute).")
        return None

    # Choose the item with the max unix timestamp
    def ts_of(item):
        ts = item.get(TIMESTAMP_FIELD)
        try:
            return int(ts)
        except (TypeError, ValueError):
            return 0

    latest = max(items, key=ts_of)

    ts_val = latest.get(TIMESTAMP_FIELD)
    lot_num = latest.get(LOT_FIELD)
    img_field = latest.get(IMAGE_FIELD)

    if img_field is None:
        print("[WuPark] Latest item missing 'image' field. Check IMAGE_FIELD constant.")
        return None

    # Backend exposes binary as base64 string in JSON
    try:
        image_bytes = base64.b64decode(img_field)
    except Exception as e:
        print(f"[WuPark] Error decoding base64 image: {e}")
        return None

    return {
        "image_bytes": image_bytes,
        "timestamp": int(ts_val) if ts_val is not None else None,
        "lotNum": lot_num,
    }


def save_image_bytes_to_local(image_bytes: bytes, local_path: str = "wupark_latest.jpg") -> str:
    with open(local_path, "wb") as f:
        f.write(image_bytes)
    return local_path


# ==========================
# 6. RUN ROBOFLOW WORKFLOW
# ==========================
def run_wupark_workflow(image_path: str) -> List[Dict[str, Any]]:
    
    wf_result = rf_client.run_workflow(
        workspace_name=ROBOFLOW_WORKSPACE,
        workflow_id=ROBOFLOW_WORKFLOW_ID,
        images={"image": image_path},
        use_cache=True,
    )

    try:
        preds = wf_result[0]["predictions"]["predictions"]
    except (KeyError, IndexError, TypeError) as e:
        print("[WuPark] Error extracting predictions from workflow result:", e)
        print("[WuPark] Workflow top-level type:", type(wf_result))
        raise

    return preds


# ==========================
# 7. POST AVAILABILITY TO YOUR STORE API
# ==========================
def post_availability_to_api(payload: Dict[str, Any]) -> None:
    """
    Sends the availability JSON to your store API.
    Adjust payload shape to the exact schema your teammate expects.
    """
    try:
        resp = requests.post(
            POST_AVAILABILITY_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
    except Exception as e:
        print(f"[WuPark] Error calling POST_AVAILABILITY_URL: {e}")
        return

    if resp.status_code != 200:
        print(f"[WuPark] Failed to store availability: {resp.status_code} {resp.text}")
    else:
        print("[WuPark] Availability stored successfully!")


# ==========================
# 8. HIGH-LEVEL PIPELINE
# ==========================
def process_latest_image() -> Optional[Dict[str, Any]]:
    """
    Pipeline:
      1. GET last-minute images (binary) from API
      2. Pick most recent by unix timestamp
      3. Save to disk
      4. Run Roboflow workflow
      5. Compute stall availability
      6. Return result dict
    """
    meta = fetch_latest_image_from_api()
    if not meta:
        print("[WuPark] No image metadata from API.")
        return None

    image_bytes = meta["image_bytes"]
    timestamp = meta["timestamp"]
    lot_num = meta["lotNum"]

    local_path = save_image_bytes_to_local(image_bytes)
    print(f"[WuPark] Saved latest image to {local_path}")

    preds = run_wupark_workflow(local_path)
    availability = compute_availability_from_predictions(preds)

    result = {
        "lotNum": lot_num,
        "timestamp": timestamp,  # still unix, your backend can keep it that way
        "availability": availability,
    }

    print("[WuPark] Computed availability:")
    print(json.dumps(result, indent=2))

    return result


# ==========================
# 9. CLI ENTRYPOINT
# ==========================
if __name__ == "__main__":
    if ROBOFLOW_API_KEY in ("REPLACE_ME", "", None):
        print("Please set ROBOFLOW_API_KEY env var or update ROBOFLOW_API_KEY in this script.")
        raise SystemExit(1)

    res = process_latest_image()
    if res is not None:
        # Adjust this if your store API expects a different shape
        post_availability_to_api(res)
