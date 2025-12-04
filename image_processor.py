import os
import json
import base64
import tempfile
from typing import Dict, Any, List
from inference_sdk import InferenceHTTPClient

# Import our API modules
from postToItemsDb import post_availability
from getFromImageDB import get_stall_config


# ==========================
# CONFIGURATION
# ==========================
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_WORKSPACE = "wupark-demo-model"
ROBOFLOW_WORKFLOW_ID = "find-cars-2"

rf_client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=ROBOFLOW_API_KEY,
)


# ==========================
# HELPER FUNCTIONS
# ==========================
def point_in_box(x: float, y: float, box: Dict[str, int]) -> bool:
    """Check if a point (x, y) is inside a bounding box."""
    return box["x1"] <= x <= box["x2"] and box["y1"] <= y <= box["y2"]


def compute_availability_from_predictions(
    preds: List[Dict[str, Any]],
    stalls: Dict[str, Dict[str, int]],
    target_class: str = "car",
    conf_thresh: float = 0.4,
) -> Dict[str, Any]:
    """
    Compute which stalls are occupied based on car detection predictions.
    """
    status: Dict[str, Dict[str, Any]] = {
        sid: {"occupied": False, "cars": []}
        for sid in stalls.keys()
    }

    for idx, det in enumerate(preds):
        # Handle both "class" and "class_id" (where 0 typically means "car")
        label = det.get("class")
        class_id = det.get("class_id")
        
        conf = det.get("confidence", 0.0)
        x = det.get("x")
        y = det.get("y")

        # Accept if label matches target_class OR if class_id is 0 (typically car)
        is_target_class = (label == target_class) or (class_id == 0 and target_class == "car")
        
        if not is_target_class:
            continue
        if conf < conf_thresh:
            continue
        if x is None or y is None:
            continue

        for stall_id, box in stalls.items():
            if point_in_box(x, y, box):
                status[stall_id]["occupied"] = True
                status[stall_id]["cars"].append(idx)

    return status


def run_roboflow_workflow(image_path: str) -> List[Dict[str, Any]]:
    """Run the Roboflow workflow on an image."""
    wf_result = rf_client.run_workflow(
        workspace_name=ROBOFLOW_WORKSPACE,
        workflow_id=ROBOFLOW_WORKFLOW_ID,
        images={"image": image_path},
        use_cache=True,
    )

    try:
        print(f"[ImageProcessor] Workflow result type: {type(wf_result)}")
        
        # Expected structure: [{"outputs": [{"predictions": {"predictions": [...]}}]}]
        if isinstance(wf_result, list) and len(wf_result) > 0:
            first_item = wf_result[0]
            
            if isinstance(first_item, dict):
                # Check for outputs structure
                if "outputs" in first_item and isinstance(first_item["outputs"], list):
                    if len(first_item["outputs"]) > 0:
                        output = first_item["outputs"][0]
                        if "predictions" in output and isinstance(output["predictions"], dict):
                            if "predictions" in output["predictions"]:
                                preds = output["predictions"]["predictions"]
                            else:
                                preds = []
                        else:
                            preds = []
                    else:
                        preds = []
                # Check if it's direct predictions list
                elif 'class' in first_item or 'confidence' in first_item:
                    preds = wf_result
                else:
                    preds = []
            else:
                preds = []
        else:
            preds = []
            
        print(f"[ImageProcessor] Extracted {len(preds)} predictions")
        return preds
        
    except Exception as e:
        print(f"[ImageProcessor] Error extracting predictions: {e}")
        import traceback
        traceback.print_exc()
        return []


# ==========================
# MAIN HANDLER
# ==========================
def process_image_stream(event, context):
    """
    Lambda handler triggered by DynamoDB Stream from Wupark-Pi-Image-Table.
    Processes new image entries and posts results to existing API.
    """
    print(f"[ImageProcessor] Processing {len(event['Records'])} records")
    
    for record in event['Records']:
        event_name = record['eventName']
        
        # Process both INSERT and MODIFY events
        if event_name not in ['INSERT', 'MODIFY']:
            print(f"[ImageProcessor] Skipping {event_name} event")
            continue
        
        try:
            new_image = record['dynamodb']['NewImage']
            
            lot_num = int(new_image['lotNum']['N'])
            timestamp = int(new_image['timestamp']['N'])
            status = int(new_image.get('status', {}).get('N', 0))
            
            image_b64 = new_image.get('image', {}).get('B')
            if not image_b64:
                print(f"[ImageProcessor] No image data for lot {lot_num}")
                continue
            
            image_bytes = base64.b64decode(image_b64)
            
            print(f"[ImageProcessor] Processing lot {lot_num}, timestamp {timestamp}")
            
            # Get stall configuration using getFromImageDB
            stalls = get_stall_config()
            
            # Save image to temp file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            
            try:
                # Run YOLO detection
                predictions = run_roboflow_workflow(tmp_path)
                print(f"[ImageProcessor] Detected {len(predictions)} objects")
                
                # Compute availability
                availability = compute_availability_from_predictions(predictions, stalls)
                
                # Post to existing API using postToItemsDb
                payload = {
                    "lotNum": lot_num,
                    "timestamp": timestamp,
                    "availability": availability,
                    "status": status
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
        'body': json.dumps({'message': 'Processing complete'})
    }
