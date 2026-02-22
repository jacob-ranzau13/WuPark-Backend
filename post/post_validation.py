import json

class PostRequestValidator:
    def validate(self, body):
        if not body:
            raise ValueError("Missing request body")

        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON body") from exc

        if 'lotNum' not in data:
            raise ValueError("lotNum is required")
        if 'timestamp' not in data:
            raise ValueError("timestamp is required")
        if 'status' not in data:
            raise ValueError("status is required")
        if 'image' not in data:
            raise ValueError("image is required")

        item = {
            'lotNum': int(data['lotNum']),
            'timestamp': int(data['timestamp']),
            'status': int(data['status']),
            'image': data['image'],
        }

        return item
