# WuPark Image Processing (Lambda)

This repository contains the image processing pipeline for WuPark. The active Lambda handler is `image_processor.py` which is wired in `serverless.yml` to run when a new image record is inserted into the DynamoDB image table. The legacy poller lives in `YoloProcessing.py` and remains as a local fallback.

Environment variables required (set in AWS Lambda or locally for testing):

- `ROBOFLOW_API_KEY` - Roboflow inference API key (required to call Roboflow workflows).
- `POST_AVAILABILITY_URL` - The API endpoint to POST computed availability (the items DB API).
- `GET_STALL_CONFIG_URL` - (optional) URL to fetch stall configuration; defaults are used if empty.

Quick local smoke-run (PowerShell):

```powershell
# Install deps
pip install -r requirements.txt

# Run the local lambda runner (uses LotImages/lot4.jpg by default and mocks network calls)
python .\local_lambda_runner.py --image LotImages\lot4.jpg --mock
```

Run unit tests (pytest):

```powershell
pip install pytest
pytest -q
```

Deploy with Serverless Framework (configured in `serverless.yml`):

```powershell
# Ensure ROBOFLOW_API_KEY, POST_AVAILABILITY_URL, GET_STALL_CONFIG_URL are exported in your shell
serverless deploy -v
```

Notes:
- `image_processor.py` expects DynamoDB stream INSERT events where the new image is encoded in DynamoDB Binary (`B`) as a base64 string. The serverless config already wires the function to `Wupark-Pi-Image-Table` stream.
- For local testing, `local_lambda_runner.py` will monkeypatch network calls so you don't need live Roboflow or external APIs.
