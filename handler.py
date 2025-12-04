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

def point_in_box(x: float, y: float, box: Dict[str, int]) -> bool:
    return box["x1"] <= x <= box["x2"] and box["y1"] <= y <= box["y2"]


def compute_availability_from_predictions(
    preds: List[Dict[str, Any]],
    stalls: Dict[str, Dict[str, int]] = STALLS,
    target_class: str = "car",
    conf_thresh: float = 0.4,
) -> Dict[str, Any]:
    

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