from inference_sdk import InferenceHTTPClient
import json

STALLS = {
    "A1": {"x1": 403,  "y1": 81, "x2": 597, "y2": 197},
    "A2": {"x1": 405, "y1": 218, "x2": 598, "y2": 330},
    "A3": {"x1": 402, "y1": 356, "x2": 601, "y2": 482},
    "A4": {"x1": 402, "y1": 500, "x2": 602, "y2": 631},
    "A5": {"x1": 890, "y1": 55, "x2": 1115, "y2": 174},
    "A6": {"x1": 897, "y1": 200, "x2": 1124, "y2": 320},
    "A7": {"x1": 902, "y1": 356, "x2": 1132, "y2": 471},
    "A8": {"x1": 912, "y1": 497, "x2": 1151, "y2": 634}
}


client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="i1VhLE1hehZpZZqrLBHO",  # or use env var
)

WORKSPACE = "wupark-demo-model"
WORKFLOW_ID = "find-cars"



def point_in_box(x: float, y: float, box: dict) -> bool:
    return box["x1"] <= x <= box["x2"] and box["y1"] <= y <= box["y2"]


def compute_availability_from_predictions(preds, stalls=STALLS,
                                          target_class="car",
                                          conf_thresh=0.4):
    """
    preds is the list under result["results"]["image"]["predictions"].
    Uses the center point (x, y) of each detection.
    """
    status = {
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

        # assign this car to any stall whose box contains the center point
        for stall_id, box in stalls.items():
            if point_in_box(x, y, box):
                status[stall_id]["occupied"] = True
                status[stall_id]["cars"].append(idx)

    return status



if __name__ == "__main__":
    image_path = r"LotImages/Lot4.jpg"  # test image

    result = client.run_workflow(
        workspace_name=WORKSPACE,
        workflow_id=WORKFLOW_ID,
        images={"image": image_path},
        use_cache=True,
    )

    #  This is the important path based on your JSON
    preds = result[0]["predictions"]["predictions"]

    availability = compute_availability_from_predictions(preds)

    print(json.dumps(availability, indent=2))
