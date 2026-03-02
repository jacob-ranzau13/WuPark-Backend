# This simulates DynamoDB events for local testing

import argparse
import base64
import json
import os
from typing import Any, Dict


def build_dynamodb_insert_record(lot_num: int, timestamp: int, image_b64: str, status: int = 0) -> Dict[str, Any]:
    return {
        "eventName": "INSERT",
        "dynamodb": {
            "NewImage": {
                "lotNum": {"N": str(lot_num)},
                "timestamp": {"N": str(timestamp)},
                "status": {"N": str(status)},
                "image": {"B": image_b64}
            }
        }
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default="LotImages/lot4.jpg", help="Path to local image to encode")
    parser.add_argument("--mock", action="store_true", default=True, help="Mock external calls (Roboflow & POST) by default")
    parser.add_argument("--no-mock", dest="mock", action="store_false", help="Disable mock behavior and call real endpoints")
    args = parser.parse_args()

    if not os.path.exists(args.image):
        raise SystemExit(f"Image not found: {args.image}")

    with open(args.image, "rb") as f:
        b = f.read()
    image_b64 = base64.b64encode(b).decode("utf-8")

    # Build event
    import time
    event = {"Records": [build_dynamodb_insert_record(4, int(time.time()), image_b64, status=0)]}

    # Prepare environment: set GET_STALL_CONFIG_URL empty so defaults are used.
    os.environ.setdefault("GET_STALL_CONFIG_URL", "")

    # Import handler and optionally monkeypatch networked functions
    import image_processor
    import postToItemsDb

    if args.mock:
        # Mock Roboflow workflow runner
        def mock_run_workflow(path: str):
            print(f"[local_runner] Mock run_workflow called with path: {path}")
            # Return a single car detection inside stall A1-ish coordinates
            return [{"class": "car", "confidence": 0.95, "x": 450, "y": 150}]

        image_processor.run_roboflow_workflow = mock_run_workflow

        # Mock POST to items DB to just print payload
        def mock_post(payload: Dict[str, Any]):
            print("[local_runner] Mock post_availability payload:")
            print(json.dumps(payload, indent=2))
            return True

        postToItemsDb.post_availability = mock_post

    # Call handler
    print("[local_runner] Invoking image_processor.process_image_stream(event)")
    resp = image_processor.process_image_stream(event, None)
    print("[local_runner] Handler response:")
    print(resp)


if __name__ == "__main__":
    main()
