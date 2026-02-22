# This is a simplified version of the InferenceHTTPClient class that we can use to test the processing logic locally
from typing import Any, Dict


class InferenceHTTPClient:
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or "https://serverless.roboflow.com"
        self.api_key = api_key

    def run_workflow(self, workspace_name: str, workflow_id: str, images: Dict[str, Any], use_cache: bool = True):
        return [{"predictions": {"predictions": []}}]
