import json

class PostParkingAvailabilityValidator:
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
        if 'availability' not in data:
            raise ValueError("availability is required")

        if not isinstance(data['lotNum'], int):
            raise ValueError("lotNum must be a number")
        if not isinstance(data['timestamp'], int):
            raise ValueError("timestamp must be a number")
        if not isinstance(data['availability'], dict):
            raise ValueError("availability must be an object")

        return {
            'lotNum': data['lotNum'],
            'timestamp': data['timestamp'],
            'availability': data['availability'],
        }
