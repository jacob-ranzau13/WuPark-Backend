import requests
import base64
from typing import Any, Dict


class InferenceHTTPClient:
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or "https://serverless.roboflow.com"
        self.api_key = api_key

    def run_workflow(self, workspace_name: str, workflow_id: str, images: Dict[str, Any], use_cache: bool = True):
        
        if not self.api_key:
            raise ValueError("Roboflow API key is required")
        
        # Handle image input - can be file path or already base64
        image_data = images.get("image")
        if isinstance(image_data, str):
            # If it's a file path, read and encode
            try:
                with open(image_data, 'rb') as f:
                    image_bytes = f.read()
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            except:
                
                image_b64 = image_data
        else:
            image_b64 = image_data
        
       
        url = f"{self.api_url}/{workspace_name}/workflows/{workflow_id}"
        
        
        payload = {
            "api_key": self.api_key,
            "inputs": {
                "image": {
                    "type": "base64",
                    "value": image_b64
                }
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        return [result]
