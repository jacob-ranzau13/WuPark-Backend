from picamera2 import Picamera2
from os import getenv
from cryptography.fernet import Fernet
from base64 import b64encode
from datetime import datetime
from time import time, sleep
from requests import post
from json import dumps
from dotenv import load_dotenv
from cv2 import imencode, IMWRITE_JPEG_QUALITY

LOT_NUM = 1 # adjust as needed

class CameraError(Exception):
    pass

class CameraModule:
    DEFAULT_RESOLUTION = (1280, 720)

    def __init__(self, resolution=DEFAULT_RESOLUTION):
        self.cam = Picamera2()
        self.cam.configure(self.cam.create_still_configuration(main={"size": resolution}))
        self.cam.start()

    def capture_image_bytes(self) -> bytes:
        try:
            image = self.cam.capture_array()
            _, buffer = imencode(".jpg", image, [int(IMWRITE_JPEG_QUALITY), 85])
            return buffer.tobytes()
        except Exception as e:
            return CameraError(f"Failed to capture image: {e}")
        
    def capture_image_file(self, timestamp: int = int(time())) -> str:
        try:
            filename = self.cam.capture_file(f"{timestamp}.jpg")
            return filename
        except Exception as e:
            raise CameraError(f"Failed to capture image: {e}")

class MessageProcessor:
    def __init__(self, camera: CameraModule):
        self.camera = camera
        self.url = getenv("aws_url")
        self.api_key = getenv("aws_api_key")

    def build_payload(self, status: int = 0) -> bytes: # build payload with header and image data, zero status by default, can be updated as needed
        lotNum = LOT_NUM
        timestamp = int(time())
        updated_status = status
        image_bytes = self.camera.capture_image_bytes()

        if isinstance(image_bytes, CameraError):
            image_bytes = b''  # Use empty bytes if capture failed
            updated_status = 1  # Set status to indicate error

        payload = bytearray()
        payload.extend(lotNum.to_bytes(1, 'big'))
        payload.extend(timestamp.to_bytes(4, 'big'))
        payload.extend(updated_status.to_bytes(1, 'big'))
        payload.extend(b64encode(image_bytes))

        return bytes(payload)

    def encrypt_image(self, image_bytes: bytes) -> str:
        key = getenv("encryption_key").encode()
        cipher = Fernet(key)
        encrypted = cipher.encrypt(image_bytes)
        return b64encode(encrypted).decode()

    def payload_to_json(self, payload: bytes) -> str:
        lotNum = payload[0]
        timestamp = int.from_bytes(payload[1:5], 'big')
        status = payload[5]
        image_bytes = payload[6:]

        encrypted_image = self.encrypt_image(image_bytes)

        data = {
            "lotNum": lotNum,
            "timestamp": timestamp,
            "status": status,
            "image": image_bytes.decode()
        }

        return dumps(data, indent=4)
    
    def post_message(self, payload: bytes):
        json_data = self.payload_to_json(payload)

        headers = {"x-api-key": self.api_key}
        response = post(url=self.url, data=json_data, headers=headers)

        return response.status_code

def main():
    load_dotenv(dotenv_path = ".env")
    camera = CameraModule()
    processor = MessageProcessor(camera)

    while True:
        payload = processor.build_payload(status=0)  # Example status
        print("Payload built, sending message...")
        status_code = processor.post_message(payload)
        print(f"Message sent with status {status_code}, waiting before next capture...")
        sleep(10)

if __name__ == "__main__":    main()
