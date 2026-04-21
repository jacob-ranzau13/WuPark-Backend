from os import getenv
from cryptography.fernet import Fernet
from base64 import b64encode
from datetime import datetime
from requests import post
from json import dumps

class MessageProcessor:
    @staticmethod
    def encrypt_image(image_bytes: bytes) -> str:
        key = getenv("encryption_key").encode()
        cipher = Fernet(key)
        encrypted = cipher.encrypt(image_bytes)
        return b64encode(encrypted).decode()
    

    @staticmethod
    def payload_to_json(payload: bytes) -> str:
        lotNum = payload[0]
        timestamp = int.from_bytes(payload[1:5], byteorder='big')
        status = payload[5]
        image_bytes = payload[6:]

        encrypted_image = MessageProcessor.encrypt_image(image_bytes)

        data = {
            "lot_num": lotNum,
            "timestamp_unix": timestamp,
            "timestamp_readable": datetime.fromtimestamp(timestamp).isoformat(),
            "status": status,
            "image": encrypted_image

        }

        return dumps(data, indent=4)
    
    @staticmethod
    def handle_message(payload: bytes):
        json_data = MessageProcessor.payload_to_json(payload)
        print("Message received:")
        print(json_data)

        url = getenv("aws_url")
        key = getenv("aws_api_key")
        headers = {"x-api-key": key}
        response = post(url=url, json=json_data, headers=headers)

        print("Status:", response.status_code)