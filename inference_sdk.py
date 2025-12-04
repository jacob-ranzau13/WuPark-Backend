"""
Minimal local stub for `inference_sdk.InferenceHTTPClient` used in tests and
local runs. This stub is intentionally lightweight and meant only for local
development/testing when the real `inference-sdk` package is not installed.
"""
from typing import Any, Dict


class InferenceHTTPClient:
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url
        self.api_key = api_key

    def run_workflow(self, workspace_name: str, workflow_id: str, images: Dict[str, Any], use_cache: bool = True):
        # Return an empty but valid-looking structure. Real tests/mock runners
        # can monkeypatch this method if they need actual predictions.
        return [{"predictions": {"predictions": []}}]
