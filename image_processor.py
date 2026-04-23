import os
import json
import base64
import tempfile
import requests
from typing import Dict, Any, List

# Import our API modules
from postToItemsDb import post_availability
from getStallInfo import get_stall_config


ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_WORKSPACE = "wupark-demo-model"
ROBOFLOW_WORKFLOW_ID = "find-cars-2"
ROBOFLOW_WORKFLOW_URL = f"https://detect.roboflow.com/{ROBOFLOW_WORKSPACE}/{ROBOFLOW_WORKFLOW_ID}"


# Bounding Box helpers
def rect_from_prediction(det: Dict[str, Any]) -> Dict[str, float]: # Now uses width/height to compute rectangle instead of centerpoint
    half_w = det["width"] / 2
    half_h = det["height"] / 2
    return {
        "x1": det["x"] - half_w,
        "y1": det["y"] - half_h,
        "x2": det["x"] + half_w,
        "y2": det["y"] + half_h,
    }

def area(box: Dict[str, float]) -> float:
    return max(0.0, box["x2"] - box["x1"]) * max(0.0, box["y2"] - box["y1"])

def overlap_area(box1: Dict[str, float], box2: Dict[str, float]) -> float:
    x1 = max(box1["x1"], box2["x1"])
    y1 = max(box1["y1"], box2["y1"])
    x2 = min(box1["x2"], box2["x2"])
    y2 = min(box1["y2"], box2["y2"])
    if x2 <= x1 or y2 <= y1:
        return 0.0
    return (x2 - x1) * (y2 - y1)


# Old point-in-box logic left just in case
def point_in_box(x: float, y: float, box: Dict[str, int]) -> bool:
    return box["x1"] <= x <= box["x2"] and box["y1"] <= y <= box["y2"]


# Function to compare roboflow bboxes with stalls
def compute_availability_from_predictions(
    predicts: List[Dict[str, Any]],
    stalls: Dict[str, Dict[str, int]],
    target_class: str = "car",
    conf_thresh: float = 0.4,
    overlap_thresh: float = 0.15,  # require 15% of car bbox (need to run full demo to finetune)
) -> Dict[str, Any]:
    

    status: Dict[str, Dict[str, Any]] = {
        sid: {"occupied": False}
        for sid in stalls.keys()
    }

    for det in predicts:
        label = det.get("class")
        class_id = det.get("class_id")

        conf = det.get("confidence", 0.0)
        if conf < conf_thresh:
            continue

        if not ((label == target_class) or (class_id == 0 and target_class == "car")):
            continue

        try:
            car_box = rect_from_prediction(det)
        except KeyError:
            continue  # detection error

        car_area = area(car_box)
        if car_area <= 0:
            continue

        for stall_id, stall_box in stalls.items():
            ov = overlap_area(car_box, stall_box)
            if ov / car_area >= overlap_thresh:
                status[stall_id]["occupied"] = True

    return status


def run_roboflow_workflow(image_path: str) -> List[Dict[str, Any]]:
    with open(image_path, 'rb') as f:
        response = requests.post(
            ROBOFLOW_WORKFLOW_URL,
            params={'api_key': ROBOFLOW_API_KEY},
            files={'file': f}
        )
    response.raise_for_status()
    result = response.json()
    
    try:
        predicts = result.get("predictions", [])
    except (KeyError, TypeError) as e:
        print(f"[ImageProcessor] Error extracting predictions: {e}")
        print(f"[ImageProcessor] Response: {result}")
        raise

    return predicts


# Main Lambda handler
def process_image_stream(event, context):

    print(f"[ImageProcessor] Processing {len(event['Records'])} records")
    
    for record in event['Records']:
        event_name = record['eventName']
        
        # Process both INSERT and MODIFY 
        if event_name not in ['INSERT', 'MODIFY']:
            print(f"[ImageProcessor] Skipping {event_name} event")
            continue
        
        try:
            new_image = record['dynamodb']['NewImage']
            
            lot_num = int(new_image['lotNum']['N'])
            timestamp = int(new_image['timestamp']['N'])
            
            print(f"[ImageProcessor] Processing lot {lot_num}, timestamp {timestamp}")
            print(f"[ImageProcessor] Record keys: {list(new_image.keys())}")
            
            image_b64 = new_image.get('image', {}).get('B')
            if not image_b64:
                print(f"[ImageProcessor] No image data for lot {lot_num}")
                print(f"[ImageProcessor] Full record: {json.dumps(new_image, default=str)}")
                continue
            
            image_bytes = base64.b64decode(image_b64)
            
            # Get stall coordinates using getStallInfo
            stalls = get_stall_config(lot_num)
            
            # Give image bytes a file path for Roboflow
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            
            try:
                # Run Roboflow detection
                predictions = run_roboflow_workflow(tmp_path)
                
                # Get stall availability
                availability = compute_availability_from_predictions(predictions, stalls)

                # Post to API using postToItemsDb
                payload = {
                    "lotNum": lot_num,
                    "timestamp": timestamp,
                    "availability": availability
                }
                post_availability(payload)
                
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
        except Exception as e:
            print(f"[ImageProcessor] Error processing record: {e}")
            continue
    
    return {
        'statusCode': 200,
        'body': json.dumps({'[ImageProcessor]': 'Processing complete'})
    }
